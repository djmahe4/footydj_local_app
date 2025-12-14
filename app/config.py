# app/config.py

APP_CONFIG = {
    "port": 8000,
    "host": "127.0.0.1",
    "license_key": "YOUR_LICENSE_KEY_HERE",
}

# Configuration for the VideoTrimmer
TRIMMER_CONFIG = {
    "target_analysis_fps": 10,
    "save_video": True,
    "visualize_live": False,
    "verify_movement": True,
    "max_movement_threshold": 80.0,
    "mse_threshold": 1400.0,
    "roi_border": 150,
    "min_fragment_duration_secs": 5,
    "output_width": 1280,
    "output_height": 720,
    "org_output_width": 1920,
    "org_output_height": 1080,
}

# Configuration for the VideoAnalyzer
ANALYZER_CONFIG = {
    "lower_green": [30, 40, 40],
    "upper_green": [90, 255, 255],
    "morph_kernel_size": (5, 5),
    "min_contour_area_abs": 1000,
    "min_contour_area_ratio": 0.05,
    "angle_horizontal_tolerance": 25,
    "min_aspect_ratio_for_standard": 3.0,
    "max_aspect_ratio_for_standard": 1.0 / 3.0,
}

# Configuration for the Homography
HOMOGRAPHY_CONFIG = {
    "enabled": True,
    "yolo_model_path": "models/yolov8l_seg_37e.pt",
    "world_points_json_path": "line_endpoints.json",
    "confidence_threshold": 0.25,
    "ransac_reproj_thresh": 5.0,
    "homography_smoothing_alpha": 0.8,
    "update_interval_frames": 10,
    "min_points_for_homography": 4,
    "debug_draw_points": False,
}

# Configuration for Player Analysis
PLAYER_ANALYSIS_CONFIG = {
    "enabled": True,
    "yolo_model_path": "models/best.pt",
    "confidence_threshold": 0.25,
    "reid_config": {
        "enabled": True,
        "save_rois": False,
    },
}

# Configuration for Ball Analysis
BALL_ANALYSIS_CONFIG = {
    "enabled": True,
    "yolo_model_path": "models/yolov8m_ball_60e_1280.pt",
    "confidence_threshold": 0.3,
}

# Cache Configuration
CACHE_CONFIG = {
    "use_homography_cache": True,
    "use_analysis_cache": True,
    "load_analysis_cache": False,
}
