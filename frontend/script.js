document.addEventListener('DOMContentLoaded', () => {
    const licenseSection = document.getElementById('license-section');
    const processingSection = document.getElementById('processing-section');
    const licenseKeyInput = document.getElementById('license-key');
    const activateBtn = document.getElementById('activate-btn');
    const licenseStatus = document.getElementById('license-status');
    const processBtn = document.getElementById('process-btn');
    const videoUpload = document.getElementById('video-upload');
    const processingStatus = document.getElementById('processing-status');

    // This is a placeholder. In a real app, you would communicate
    // with the Python backend to check the license status.
    // We'll simulate it with a variable.
    let isLicensed = false;

    function checkLicense() {
        // TODO: Make an API call to GET /api/license-status
        // For now, we just use the local variable.
        if (isLicensed) {
            licenseStatus.textContent = 'Status: Active';
            licenseStatus.style.color = 'green';
            licenseSection.classList.add('hidden');
            processingSection.classList.remove('hidden');
        } else {
            licenseStatus.textContent = 'Status: Inactive';
            licenseStatus.style.color = 'red';
            licenseSection.classList.remove('hidden');
            processingSection.classList.add('hidden');
        }
    }

    activateBtn.addEventListener('click', () => {
        const key = licenseKeyInput.value.trim();
        if (!key) {
            alert('Please enter a license key.');
            return;
        }
        
        // TODO: Make an API call to POST /api/activate with the key
        console.log(`Simulating activation with key: ${key}`);
        
        // --- Placeholder Logic ---
        // In a real app, the backend would verify this.
        // We'll just assume it's successful for demonstration.
        isLicensed = true;
        alert('License activated successfully!');
        checkLicense();
        // --- End Placeholder ---
    });

    videoUpload.addEventListener('change', () => {
        if (videoUpload.files.length > 0) {
            processBtn.disabled = false;
        } else {
            processBtn.disabled = true;
        }
    });

    processBtn.addEventListener('click', () => {
        if (videoUpload.files.length === 0) {
            alert('Please select a video file.');
            return;
        }

        const videoFile = videoUpload.files[0];
        const formData = new FormData();
        formData.append('video_file', videoFile);

        processingStatus.textContent = 'Uploading and processing... This may take a while.';
        processBtn.disabled = true;
        videoUpload.disabled = true;

        // TODO: Make a POST request to /api/process-video with the formData
        
        console.log(`Simulating processing for file: ${videoFile.name}`);
        
        // --- Placeholder Logic ---
        setTimeout(() => {
            processingStatus.textContent = `Processing complete for ${videoFile.name}!`;
            processBtn.disabled = false;
            videoUpload.disabled = false;
        }, 10000); // Simulate a 10-second processing time
        // --- End Placeholder ---
    });

    // Initial check
    checkLicense();
});
