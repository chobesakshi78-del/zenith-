import os

# Configurable detection weights for Noisy-OR Fusion
DETECTION_CONFIG = {
    "weights": {
        "access_mismatch": 0.55,
        "role_dna_anomaly": 0.45,
        "circular_flow": 0.70,
        "transaction_splitting": 0.50,
        "rapid_movement": 0.55,
        "bulk_access": 0.40,
        "collusion": 0.65,
        "insider_touch": 0.85,
    },
    # Insider Touch Configuration
    "insider_touch_window_minutes": int(os.getenv("INSIDER_TOUCH_WINDOW_MINUTES", "30")),
    "insider_touch_lag_boost_threshold_minutes": 10,  # Lag under 10m gets immediate boost
    "insider_touch_lag_boost_multiplier": 1.25,

    # Structuring Configuration
    "structuring_threshold": float(os.getenv("STRUCTURING_THRESHOLD", "50000.0")),
    "structuring_lower_ratio": float(os.getenv("STRUCTURING_LOWER_RATIO", "0.90")),  # >= 45,000
    "structuring_upper_ratio": float(os.getenv("STRUCTURING_UPPER_RATIO", "0.999")), # <= 49,950
    "structuring_window_hours": 24,
    "structuring_min_count": 3,

    # Circular Flow Configuration
    "circular_max_cycle_length": int(os.getenv("CIRCULAR_MAX_CYCLE_LENGTH", "5")),
    "circular_window_hours": 48,
    "circular_amount_similarity_tolerance": 0.15,  # within 15% amount retention

    # Rapid Movement Configuration
    "rapid_pass_through_minutes": int(os.getenv("RAPID_PASS_THROUGH_MINUTES", "15")),
    "rapid_pass_through_preservation_ratio": float(os.getenv("RAPID_PASS_THROUGH_RATIO", "0.90")),

    # False Positive Shield Configuration
    "shield_enabled": os.getenv("SHIELD_ENABLED", "true").lower() in ("true", "1", "yes"),
    "shield_max_reduction": 0.65,  # Up to 65% reduction for solid benign evidence
}
