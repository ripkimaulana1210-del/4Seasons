CAMERA_PRESETS = {
    "sakura": {
        "position": (0.0, 2.82, 14.1),
        "target": (0.0, 1.8, 0.0),
    },
    "bridge": {
        "position": (7.4, 2.88, 10.8),
        "target": (1.4, 1.0, 2.8),
    },
    "village": {
        "position": (-14.2, 5.0, 14.0),
        "target": (-2.0, 1.5, 0.4),
    },
    "fuji": {
        "position": (-4.2, 4.2, 18.0),
        "target": (-17.5, 7.0, -57.0),
    },
    "season_spring": {
        "position": (-8.2, 2.78, 11.8),
        "target": (-1.6, 0.9, 1.8),
    },
    "season_summer": {
        "position": (6.6, 3.0, 18.6),
        "target": (8.8, 1.05, 10.2),
    },
    "season_autumn": {
        "position": (9.8, 3.12, 12.5),
        "target": (0.6, 0.8, 5.2),
    },
    "season_winter": {
        "position": (-2.8, 4.4, 15.2),
        "target": (-8.6, 7.5, -42.0),
    },
}

TRANSITION_PRESETS = {
    "winter->early_spring": {
        "duration": 7.0,
        "camera_route": ("season_winter", "bridge", "season_spring"),
        "timeline": (("Wet snow", 0.00, 0.45), ("Thaw", 0.18, 0.72), ("Sprouts", 0.46, 1.00)),
        "audio_cue": "thaw",
    },
    "early_spring->spring": {
        "duration": 6.0,
        "camera_route": ("season_spring", "sakura", "bridge"),
        "timeline": (("Mist clears", 0.00, 0.42), ("Grass", 0.22, 0.72), ("Flowers", 0.46, 1.00)),
        "audio_cue": "blend",
    },
    "spring->hanami": {
        "duration": 6.0,
        "camera_route": ("season_spring", "sakura", "season_spring"),
        "timeline": (("Bud color", 0.12, 0.52), ("Full bloom", 0.32, 0.86), ("Petal rain", 0.52, 1.00)),
        "audio_cue": "blend",
    },
    "hanami->tsuyu": {
        "duration": 6.5,
        "camera_route": ("sakura", "bridge", "season_spring"),
        "timeline": (("Petals fall", 0.00, 0.48), ("Clouds", 0.20, 0.72), ("Rain", 0.42, 1.00)),
        "audio_cue": "rain",
    },
    "tsuyu->summer": {
        "duration": 6.5,
        "camera_route": ("season_spring", "bridge", "season_summer"),
        "timeline": (("Rain fades", 0.00, 0.52), ("Clear sky", 0.24, 0.78), ("Heat", 0.44, 1.00)),
        "audio_cue": "heat",
    },
    "winter->spring": {
        "duration": 8.0,
        "camera_route": ("season_winter", "bridge", "sakura", "season_spring"),
        "timeline": (
            ("Crack", 0.12, 0.52),
            ("Melt", 0.02, 0.64),
            ("Sprout", 0.30, 0.80),
            ("Bloom", 0.46, 0.94),
            ("Petals", 0.55, 1.00),
        ),
        "audio_cue": "thaw",
    },
    "spring->summer": {
        "duration": 7.0,
        "camera_route": ("season_spring", "bridge", "season_summer"),
        "timeline": (
            ("Petals fade", 0.10, 0.70),
            ("Heat", 0.16, 0.86),
            ("Sparkle", 0.36, 0.95),
            ("Fireflies", 0.55, 1.00),
        ),
        "audio_cue": "heat",
    },
    "summer->midsummer": {
        "duration": 6.0,
        "camera_route": ("season_summer", "village", "season_summer"),
        "timeline": (("Heat peak", 0.12, 0.72), ("Lanterns", 0.32, 0.96), ("Fireflies", 0.52, 1.00)),
        "audio_cue": "heat",
    },
    "midsummer->late_summer": {
        "duration": 6.0,
        "camera_route": ("village", "season_summer", "bridge"),
        "timeline": (("Festival fades", 0.00, 0.46), ("Dry grass", 0.28, 0.88), ("Dust", 0.42, 1.00)),
        "audio_cue": "blend",
    },
    "late_summer->autumn": {
        "duration": 6.5,
        "camera_route": ("season_summer", "sakura", "season_autumn"),
        "timeline": (("Dry heat", 0.00, 0.48), ("Yellowing", 0.24, 0.84), ("First leaves", 0.44, 1.00)),
        "audio_cue": "leaves",
    },
    "summer->autumn": {
        "duration": 7.5,
        "camera_route": ("season_summer", "sakura", "season_autumn"),
        "timeline": (
            ("Gold leaves", 0.16, 0.72),
            ("Leaf fall", 0.22, 0.92),
            ("Wind", 0.20, 0.88),
            ("Cold rain", 0.60, 1.00),
        ),
        "audio_cue": "leaves",
    },
    "autumn->momiji": {
        "duration": 6.0,
        "camera_route": ("season_autumn", "sakura", "season_autumn"),
        "timeline": (("Red leaves", 0.14, 0.72), ("Leaf carpet", 0.28, 0.92), ("Golden sun", 0.48, 1.00)),
        "audio_cue": "leaves",
    },
    "momiji->first_frost": {
        "duration": 6.5,
        "camera_route": ("season_autumn", "bridge", "season_winter"),
        "timeline": (("Color fades", 0.00, 0.48), ("Cold mist", 0.20, 0.82), ("First frost", 0.42, 1.00)),
        "audio_cue": "snow",
    },
    "first_frost->winter": {
        "duration": 6.5,
        "camera_route": ("season_autumn", "bridge", "season_winter"),
        "timeline": (("Frost spreads", 0.00, 0.58), ("Snow cover", 0.32, 1.00), ("Quiet light", 0.54, 1.00)),
        "audio_cue": "snow",
    },
    "winter->deep_winter": {
        "duration": 6.5,
        "camera_route": ("season_winter", "fuji", "season_winter"),
        "timeline": (("Snow deepens", 0.00, 0.68), ("Pond stills", 0.28, 0.90), ("Aurora glow", 0.56, 1.00)),
        "audio_cue": "snow",
    },
    "first_frost->deep_winter": {
        "duration": 7.0,
        "camera_route": ("season_winter", "fuji", "season_winter"),
        "timeline": (("Frost thickens", 0.00, 0.55), ("Snow cover", 0.24, 0.92), ("Aurora", 0.56, 1.00)),
        "audio_cue": "snow",
    },
    "autumn->winter": {
        "duration": 8.0,
        "camera_route": ("season_autumn", "bridge", "season_winter"),
        "timeline": (
            ("Frost", 0.24, 0.88),
            ("Freeze", 0.38, 0.96),
            ("First snow", 0.42, 1.00),
            ("Aurora", 0.62, 1.00),
        ),
        "audio_cue": "snow",
    },
    "deep_winter->early_spring": {
        "duration": 8.0,
        "camera_route": ("season_winter", "bridge", "sakura", "season_spring"),
        "timeline": (("Deep ice", 0.00, 0.40), ("Crack", 0.12, 0.56), ("Thaw", 0.34, 0.86), ("Sprout", 0.62, 1.00)),
        "audio_cue": "thaw",
    },
}

SCENE_LAYOUT = {
    "ground": {
        "pos": (0.0, -0.055, 0.0),
        "scale": (30.5, 1.0, 30.5),
        "repeat": (25.5, 25.5),
    },
    "pond": {
        "radius_scale": 6.22 / 4.80,
        "center": (0.0, 0.0, 0.0),
    },
    "island": {
        "radius_scale": 2.63 / 1.95,
        "center": (0.0, 0.0, 0.0),
    },
    "sakura_tree": {
        "pos": (0.0, 0.24, 0.0),
        "rot": (0.0, 0.0, 0.0),
        "scale": (1.49, 1.49, 1.49),
    },
    "road": {
        "radius": 11.25,
        "width": 0.96,
    },
    "bridge": {
        "center": (0.0, 0.0, 5.90),
        "yaw": 0.0,
    },
    "building_additions": {
        "tea_house": {"pos": (-12.4, 4.2), "yaw": 38.0, "scale": 0.88},
        "pavilion": {"pos": (-7.4, 10.8), "yaw": 18.0, "scale": 0.80},
        "water_mill": {"pos": (-11.8, -6.5), "yaw": -38.0, "scale": 0.80},
        "secondary_torii": {"pos": (0.0, 17.20), "yaw": 0.0, "scale": 0.86},
        "yatai_row": {"pos": (9.6, 10.8), "yaw": -24.0, "scale": 0.82},
        "bathhouse": {"pos": (-13.0, -9.4), "yaw": 34.0, "scale": 0.88},
        "storage_shed": {"pos": (16.2, 4.0), "yaw": 78.0, "scale": 0.74},
        "viewing_deck": {"pos": (-8.6, 11.0), "yaw": 24.0, "scale": 0.84},
        "covered_bridge": {"scale": 0.76},
        "rice_field": {"pos": (16.0, -7.7), "yaw": -12.0, "scale": 0.92},
    },
}

QUALITY_PROFILES = [
    {
        "id": "low",
        "name": "Low",
        "shadow_map_size": 1024,
        "shadow_min_scale": 0.12,
        "shadow_pcf": 0,
        "culling": {
            "opaque_distance": 24.0,
            "transparent_distance": 30.0,
            "shadow_distance": 22.0,
        },
        "fractions": {
            "pond_rock": 0.45,
            "wind": 0.40,
            "rain": 0.45,
            "particle": 0.45,
            "firefly": 0.35,
            "glow": 0.60,
            "shadow": 0.45,
        },
    },
    {
        "id": "medium",
        "name": "Medium",
        "shadow_map_size": 1536,
        "shadow_min_scale": 0.06,
        "shadow_pcf": 1,
        "culling": {
            "opaque_distance": 36.0,
            "transparent_distance": 44.0,
            "shadow_distance": 32.0,
        },
        "fractions": {
            "pond_rock": 0.75,
            "wind": 0.70,
            "rain": 0.75,
            "particle": 0.75,
            "firefly": 0.70,
            "glow": 0.85,
            "shadow": 0.75,
        },
    },
    {
        "id": "high",
        "name": "High",
        "shadow_map_size": 2048,
        "shadow_min_scale": 0.0,
        "shadow_pcf": 2,
        "culling": {
            "opaque_distance": 58.0,
            "transparent_distance": 68.0,
            "shadow_distance": 52.0,
        },
        "fractions": {
            "pond_rock": 1.0,
            "wind": 1.0,
            "rain": 1.0,
            "particle": 1.0,
            "firefly": 1.0,
            "glow": 1.0,
            "shadow": 1.0,
        },
    },
]

POND_FENCE_ARCS = [
    (114, 172, 8),
    (218, 288, 10),
    (322, 352, 5),
]

HOUSE_SPECS = [
    (26, 19.4, (0.88, 0.67, 0.78), (0.72, 0.58, 0.42), (0.43, 0.12, 0.09), (0.84, 0.78, 0.64), -7, "cottage"),
    (42, 18.6, (1.02, 0.78, 0.88), (0.64, 0.54, 0.36), (0.36, 0.16, 0.12), (0.80, 0.73, 0.58), 5, "two_story"),
    (68, 17.5, (0.96, 0.72, 0.86), (0.76, 0.66, 0.48), (0.50, 0.18, 0.11), (0.88, 0.82, 0.66), -4, "l_shape"),
    (116, 18.3, (0.94, 0.72, 0.84), (0.67, 0.57, 0.43), (0.34, 0.18, 0.15), (0.80, 0.74, 0.60), 5, "split_level"),
    (142, 18.1, (1.08, 0.80, 0.92), (0.72, 0.61, 0.45), (0.45, 0.13, 0.10), (0.86, 0.79, 0.62), -4, "tower"),
    (170, 17.9, (0.88, 0.66, 0.78), (0.61, 0.52, 0.38), (0.38, 0.20, 0.13), (0.78, 0.70, 0.56), 6, "wide_veranda"),
    (202, 19.2, (1.00, 0.74, 0.86), (0.70, 0.55, 0.39), (0.46, 0.16, 0.10), (0.85, 0.77, 0.60), -5, "two_story"),
    (228, 17.7, (1.10, 0.80, 0.94), (0.66, 0.58, 0.42), (0.35, 0.15, 0.13), (0.82, 0.75, 0.59), 3, "l_shape"),
    (252, 18.6, (0.90, 0.68, 0.80), (0.73, 0.63, 0.47), (0.49, 0.17, 0.11), (0.88, 0.80, 0.64), -2, "cottage"),
    (282, 18.2, (0.98, 0.72, 0.86), (0.63, 0.53, 0.37), (0.39, 0.14, 0.10), (0.81, 0.72, 0.57), 5, "split_level"),
    (306, 17.8, (0.92, 0.70, 0.82), (0.74, 0.60, 0.43), (0.44, 0.15, 0.10), (0.86, 0.78, 0.61), -5, "tower"),
    (318, 18.7, (1.00, 0.74, 0.92), (0.68, 0.56, 0.40), (0.34, 0.17, 0.13), (0.82, 0.75, 0.58), 4, "wide_veranda"),
    (350, 17.6, (0.92, 0.68, 0.82), (0.69, 0.58, 0.42), (0.37, 0.16, 0.12), (0.84, 0.77, 0.60), -3, "cottage"),
    (104, 20.2, (0.86, 0.66, 0.78), (0.70, 0.60, 0.44), (0.42, 0.15, 0.10), (0.84, 0.78, 0.62), 4, "wide_veranda"),
]
