// API Base URL
const API_BASE = window.location.origin;

// Application State
const appState = {
    isLicensed: false,
    currentSection: 'license',
    selectedFile: null,
    lastAnalysisResult: null
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await checkServerConnection();
    await checkLicenseStatus();
    updateUI();
}

// Server Connection Check
async function checkServerConnection() {
    const statusIndicator = document.getElementById('connection-status');
    try {
        const response = await fetch(`${API_BASE}/api/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            statusIndicator.classList.add('connected');
            statusIndicator.querySelector('.status-text').textContent = 'Connected';
        } else {
            throw new Error('Server not responding');
        }
    } catch (error) {
        console.error('Connection error:', error);
        statusIndicator.querySelector('.status-text').textContent = 'Disconnected';
        showNotification('Unable to connect to server', 'error');
    }
}

// License Management
async function checkLicenseStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/license-status`);
        const data = await response.json();
        
        appState.isLicensed = data.active;
        updateLicenseUI(data);
        
        if (appState.isLicensed) {
            await loadSystemStatus();
        }
    } catch (error) {
        console.error('Error checking license:', error);
        appState.isLicensed = false;
    }
}

function updateLicenseUI(data) {
    const banner = document.getElementById('license-banner');
    const title = document.getElementById('license-status-title');
    const subtitle = document.getElementById('license-status-subtitle');
    const infoLicense = document.getElementById('info-license');
    
    if (data.active) {
        banner.classList.add('active');
        title.textContent = 'License Active';
        subtitle.textContent = `Activated on ${new Date(data.activated_at).toLocaleDateString()}`;
        infoLicense.textContent = 'Active';
        infoLicense.style.color = 'var(--success-color)';
    } else {
        banner.classList.remove('active');
        title.textContent = 'License Inactive';
        subtitle.textContent = 'Please enter your license key to continue';
        infoLicense.textContent = 'Inactive';
        infoLicense.style.color = 'var(--danger-color)';
    }
}

async function activateLicense() {
    const keyInput = document.getElementById('license-key');
    const key = keyInput.value.trim();
    const activateBtn = document.getElementById('activate-btn');
    
    if (!key) {
        showNotification('Please enter a license key', 'error');
        return;
    }
    
    activateBtn.disabled = true;
    activateBtn.innerHTML = '<span>Activating...</span>';
    
    try {
        const response = await fetch(`${API_BASE}/api/activate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('License activated successfully!', 'success');
            await checkLicenseStatus();
            switchSection('analyze');
        } else {
            showNotification(data.detail || 'Activation failed', 'error');
        }
    } catch (error) {
        console.error('Activation error:', error);
        showNotification('Failed to activate license', 'error');
    } finally {
        activateBtn.disabled = false;
        activateBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M13.8 12H3" stroke-width="2"/>
            </svg>
            Activate License
        `;
    }
}

// File Management
function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const videoUpload = document.getElementById('video-upload');
    const browseBtn = document.getElementById('browse-btn');
    const fileInfo = document.getElementById('file-info');
    const removeFileBtn = document.getElementById('remove-file');
    
    // Browse button
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        videoUpload.click();
    });
    
    // Upload area click
    uploadArea.addEventListener('click', () => {
        videoUpload.click();
    });
    
    // File selection
    videoUpload.addEventListener('change', (e) => {
        handleFileSelection(e.target.files[0]);
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelection(file);
        }
    });
    
    // Remove file
    removeFileBtn.addEventListener('click', () => {
        clearFileSelection();
    });
}

function handleFileSelection(file) {
    if (!file) return;
    
    // Validate file type
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];
    if (!validTypes.includes(file.type)) {
        showNotification('Please select a valid video file (MP4, MOV, AVI, MKV)', 'error');
        return;
    }
    
    // Validate file size (2GB max)
    const maxSize = 2 * 1024 * 1024 * 1024; // 2GB in bytes
    if (file.size > maxSize) {
        showNotification('File size exceeds 2GB limit', 'error');
        return;
    }
    
    appState.selectedFile = file;
    
    // Update UI
    document.getElementById('upload-area').classList.add('hidden');
    document.getElementById('file-info').classList.remove('hidden');
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('process-btn').disabled = false;
}

function clearFileSelection() {
    appState.selectedFile = null;
    document.getElementById('upload-area').classList.remove('hidden');
    document.getElementById('file-info').classList.add('hidden');
    document.getElementById('video-upload').value = '';
    document.getElementById('process-btn').disabled = true;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Video Analysis
async function startAnalysis() {
    if (!appState.selectedFile) {
        showNotification('Please select a video file', 'error');
        return;
    }
    
    if (!appState.isLicensed) {
        showNotification('Please activate your license first', 'error');
        switchSection('license');
        return;
    }
    
    const processBtn = document.getElementById('process-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = document.getElementById('progress-percent');
    const progressDetail = document.getElementById('progress-detail');
    
    // Show progress UI
    processBtn.disabled = true;
    progressContainer.classList.remove('hidden');
    
    // Simulate progress updates
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        progressFill.style.width = `${progress}%`;
        progressPercent.textContent = `${Math.round(progress)}%`;
        
        // Update progress messages
        if (progress < 30) {
            progressDetail.textContent = 'Uploading video...';
        } else if (progress < 60) {
            progressDetail.textContent = 'Detecting field lines and camera calibration...';
        } else if (progress < 80) {
            progressDetail.textContent = 'Tracking players and ball...';
        } else {
            progressDetail.textContent = 'Finalizing analysis...';
        }
    }, 500);
    
    try {
        const formData = new FormData();
        formData.append('video_file', appState.selectedFile);
        
        const response = await fetch(`${API_BASE}/api/analyze-video`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        progressDetail.textContent = 'Analysis complete!';
        
        if (response.ok) {
            appState.lastAnalysisResult = data;
            showNotification('Video analysis completed successfully!', 'success');
            
            setTimeout(() => {
                displayResults(data);
                switchSection('results');
                progressContainer.classList.add('hidden');
                processBtn.disabled = false;
                clearFileSelection();
            }, 1000);
        } else {
            throw new Error(data.detail || 'Analysis failed');
        }
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Analysis error:', error);
        showNotification('Analysis failed: ' + error.message, 'error');
        progressContainer.classList.add('hidden');
        processBtn.disabled = false;
    }
}

function displayResults(data) {
    const noResults = document.getElementById('no-results');
    const resultsContent = document.getElementById('results-content');
    
    noResults.classList.add('hidden');
    resultsContent.classList.remove('hidden');
    
    // Check if this is mock data or real analysis
    const analysis = data.analysis || {};
    
    // Field Detection
    if (analysis.field_detection) {
        document.getElementById('field-confidence').textContent = 
            (analysis.field_detection.confidence * 100).toFixed(1) + '%';
        document.getElementById('field-lines').textContent = 
            analysis.field_detection.lines_detected || 'N/A';
        document.getElementById('field-status').textContent = 
            analysis.field_detection.detected ? 'Detected' : 'Not Found';
        document.getElementById('field-status').className = 
            analysis.field_detection.detected ? 'badge badge-success' : 'badge badge-warning';
    }
    
    // Player Tracking
    if (analysis.player_tracking) {
        document.getElementById('player-count').textContent = 
            analysis.player_tracking.players_detected || 'N/A';
        document.getElementById('team-count').textContent = 
            analysis.player_tracking.teams_identified || 'N/A';
        document.getElementById('player-status').textContent = 'Active';
        document.getElementById('player-status').className = 'badge badge-success';
    }
    
    // Ball Tracking
    if (analysis.ball_tracking) {
        document.getElementById('ball-confidence').textContent = 
            (analysis.ball_tracking.tracking_confidence * 100).toFixed(1) + '%';
        document.getElementById('possession-status').textContent = 
            analysis.ball_tracking.possession_analyzed ? 'Analyzed' : 'N/A';
        document.getElementById('ball-status').textContent = 
            analysis.ball_tracking.ball_detected ? 'Tracked' : 'Not Found';
        document.getElementById('ball-status').className = 
            analysis.ball_tracking.ball_detected ? 'badge badge-success' : 'badge badge-warning';
    }
    
    // Homography
    if (analysis.homography) {
        document.getElementById('homography-quality').textContent = 
            analysis.homography.transformation_quality || 'N/A';
        document.getElementById('calibration-status').textContent = 
            analysis.homography.calibrated ? 'Success' : 'Failed';
        document.getElementById('homography-status').textContent = 
            analysis.homography.calibrated ? 'Calibrated' : 'Failed';
        document.getElementById('homography-status').className = 
            analysis.homography.calibrated ? 'badge badge-success' : 'badge badge-warning';
    }
}

// System Status
async function loadSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        document.getElementById('info-modules').textContent = 
            data.modules_available ? 'Available' : 'Not Available';
        document.getElementById('info-modules').style.color = 
            data.modules_available ? 'var(--success-color)' : 'var(--warning-color)';
        
        const modelStatus = Object.values(data.models_available || {});
        const allModelsAvailable = modelStatus.length > 0 && modelStatus.every(v => v);
        
        document.getElementById('info-models').textContent = 
            allModelsAvailable ? 'All Available' : 'Some Missing';
        document.getElementById('info-models').style.color = 
            allModelsAvailable ? 'var(--success-color)' : 'var(--warning-color)';
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Navigation
function switchSection(sectionName) {
    // Update state
    appState.currentSection = sectionName;
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === sectionName) {
            item.classList.add('active');
        }
    });
    
    // Update content sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

// Event Listeners Setup
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            
            // Check license for protected sections
            if (!appState.isLicensed && section !== 'license' && section !== 'settings') {
                showNotification('Please activate your license first', 'error');
                switchSection('license');
                return;
            }
            
            switchSection(section);
        });
    });
    
    // License activation
    document.getElementById('activate-btn').addEventListener('click', activateLicense);
    document.getElementById('license-key').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            activateLicense();
        }
    });
    
    // File upload
    setupFileUpload();
    
    // Process video
    document.getElementById('process-btn').addEventListener('click', startAnalysis);
    
    // Download buttons
    document.getElementById('download-json').addEventListener('click', () => {
        if (appState.lastAnalysisResult) {
            downloadJSON(appState.lastAnalysisResult, 'analysis-results.json');
            showNotification('Results downloaded', 'success');
        } else {
            showNotification('No results available', 'error');
        }
    });
    
    document.getElementById('download-video').addEventListener('click', () => {
        showNotification('Annotated video download coming soon', 'info');
    });
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Simple notification system (could be enhanced with a toast library)
    const colors = {
        success: 'var(--success-color)',
        error: 'var(--danger-color)',
        warning: 'var(--warning-color)',
        info: 'var(--primary-color)'
    };
    
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message); // Simple fallback, could use a toast library
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function updateUI() {
    // Any additional UI updates based on current state
    if (appState.isLicensed) {
        // Enable analyze section navigation
        const analyzeNav = document.querySelector('[data-section="analyze"]');
        if (analyzeNav) {
            analyzeNav.style.opacity = '1';
            analyzeNav.style.pointerEvents = 'auto';
        }
    }
}
