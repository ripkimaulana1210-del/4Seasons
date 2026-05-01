import math
import numpy as np


def _normalize(v):
    v = np.asarray(v, dtype=np.float32)
    n = float(np.linalg.norm(v))
    if n < 1e-6:
        return np.array([0.0, 1.0, 0.0], dtype=np.float32)
    return v / n


def _make_basis(direction):
    forward = _normalize(direction)

    helper = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    if abs(float(np.dot(forward, helper))) > 0.92:
        helper = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    right = _normalize(np.cross(helper, forward))
    up = _normalize(np.cross(forward, right))
    return right, up, forward


def _push_vertex(data, normal, position):
    data.append(
        [
            float(normal[0]),
            float(normal[1]),
            float(normal[2]),
            float(position[0]),
            float(position[1]),
            float(position[2]),
        ]
    )


def _add_frustum(data, p0, p1, r0, r1, sides=12):
    p0 = np.asarray(p0, dtype=np.float32)
    p1 = np.asarray(p1, dtype=np.float32)

    axis = p1 - p0
    if np.linalg.norm(axis) < 1e-6:
        return

    right, up, _ = _make_basis(axis)

    ring0 = []
    ring1 = []
    normals = []

    for i in range(sides):
        a = 2.0 * math.pi * i / sides
        radial = math.cos(a) * right + math.sin(a) * up
        radial = _normalize(radial)

        ring0.append(p0 + radial * r0)
        ring1.append(p1 + radial * r1)
        normals.append(radial)

    for i in range(sides):
        j = (i + 1) % sides

        _push_vertex(data, normals[i], ring0[i])
        _push_vertex(data, normals[i], ring1[i])
        _push_vertex(data, normals[j], ring1[j])

        _push_vertex(data, normals[i], ring0[i])
        _push_vertex(data, normals[j], ring1[j])
        _push_vertex(data, normals[j], ring0[j])


def _add_branch_recursive(segments, tips, rng, p0, direction, length, radius, depth):
    direction = _normalize(direction)

    right, up, _ = _make_basis(direction)

    # Bending kecil saja supaya cabang natural, bukan patah / tanduk.
    bend = (right * rng.uniform(-0.16, 0.16) + up * rng.uniform(-0.07, 0.10)) * length

    mid = p0 + direction * (length * 0.52) + bend * 0.20
    p1 = p0 + direction * length + bend * 0.32

    r_mid = radius * rng.uniform(0.72, 0.82)
    r_end = radius * rng.uniform(0.48, 0.60)

    segments.append((p0, mid, radius, r_mid))
    segments.append((mid, p1, r_mid, r_end))

    if depth <= 0 or radius < 0.035:
        tips.append(p1)
        return

    # Semakin kecil cabang, baru boleh bercabang.
    child_count = 2 if depth >= 2 else 1
    base_angle = rng.uniform(0.0, 2.0 * math.pi)

    for i in range(child_count):
        angle = (
            base_angle + (2.0 * math.pi * i / child_count) + rng.uniform(-0.35, 0.35)
        )

        outward = np.array(
            [math.cos(angle), 0.0, math.sin(angle)],
            dtype=np.float32,
        )

        # Cabang anak lebih melebar ke samping, tidak terlalu vertikal.
        child_up_bias = rng.uniform(-0.02, 0.12)
        child_length = length * rng.uniform(0.56, 0.70)

        if p1[1] > 4.05:
            child_up_bias -= rng.uniform(0.03, 0.07)
            child_length *= rng.uniform(0.86, 0.93)

        child_dir = _normalize(
            direction * rng.uniform(0.55, 0.72)
            + outward * rng.uniform(0.32, 0.55)
            + np.array([0.0, child_up_bias, 0.0], dtype=np.float32)
            + rng.normal(0.0, 0.04, 3).astype(np.float32)
        )

        _add_branch_recursive(
            segments,
            tips,
            rng,
            p1,
            child_dir,
            child_length,
            radius * rng.uniform(0.52, 0.64),
            depth - 1,
        )

    tips.append(p1)


def build_sakura_skeleton(seed=12):
    rng = np.random.default_rng(seed)
    segments = []
    tips = []

    # Batang dibuat lebih tinggi, tapi tidak ekstrem.
    trunk_points = [
        np.array([0.00, 0.00, 0.00], dtype=np.float32),
        np.array([0.05, 0.95, -0.02], dtype=np.float32),
        np.array([-0.04, 1.85, 0.04], dtype=np.float32),
        np.array([0.03, 2.65, 0.02], dtype=np.float32),
        np.array([0.00, 3.25, 0.04], dtype=np.float32),
    ]

    trunk_radii = [0.50, 0.43, 0.35, 0.27, 0.19]

    for i in range(len(trunk_points) - 1):
        segments.append(
            (
                trunk_points[i],
                trunk_points[i + 1],
                trunk_radii[i],
                trunk_radii[i + 1],
            )
        )

    # Akar lebih pendek supaya tidak terlalu ramai.
    for i in range(7):
        angle = 2.0 * math.pi * i / 7.0 + rng.uniform(-0.14, 0.14)
        outward = np.array([math.cos(angle), -0.04, math.sin(angle)], dtype=np.float32)

        start = np.array([0.0, 0.08, 0.0], dtype=np.float32)
        end = start + _normalize(outward) * rng.uniform(0.50, 0.82)
        end[1] = rng.uniform(0.00, 0.05)

        segments.append(
            (
                start,
                end,
                rng.uniform(0.12, 0.18),
                rng.uniform(0.055, 0.085),
            )
        )

    # Cabang utama dibuat seperti payung sakura.
    main_branch_count = 10

    for i in range(main_branch_count):
        angle = 2.0 * math.pi * i / main_branch_count + rng.uniform(-0.16, 0.16)

        # Cabang mulai dari tengah-atas, bukan terlalu bawah dan bukan terlalu tinggi.
        y = rng.uniform(1.80, 2.72)

        start = np.array(
            [
                rng.uniform(-0.04, 0.04),
                y,
                rng.uniform(-0.04, 0.04),
            ],
            dtype=np.float32,
        )

        outward = np.array(
            [math.cos(angle), 0.0, math.sin(angle)],
            dtype=np.float32,
        )

        # Naik sedikit lalu melebar. Ini yang bikin bentuk sakura lebih natural.
        direction = _normalize(
            outward * rng.uniform(1.00, 1.28)
            + np.array([0.0, rng.uniform(0.16, 0.32), 0.0], dtype=np.float32)
            + rng.normal(0.0, 0.035, 3).astype(np.float32)
        )

        _add_branch_recursive(
            segments,
            tips,
            rng,
            start,
            direction,
            rng.uniform(1.36, 1.88),
            rng.uniform(0.10, 0.155),
            depth=3,
        )

    return segments, tips


def _add_petal(data, center, right, up, length, width):
    p0 = center
    p1 = center + right * width + up * length * 0.45
    p2 = center + up * length * 1.15
    p3 = center - right * width + up * length * 0.45

    normal = _normalize(np.cross(p1 - p0, p2 - p0))

    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p1)
    _push_vertex(data, normal, p2)

    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p2)
    _push_vertex(data, normal, p3)

    back = -normal

    _push_vertex(data, back, p2)
    _push_vertex(data, back, p1)
    _push_vertex(data, back, p0)

    _push_vertex(data, back, p3)
    _push_vertex(data, back, p2)
    _push_vertex(data, back, p0)


def _add_canopy_card(data, center, right, up, width, height):
    p0 = center + up * height
    p1 = center + right * width
    p2 = center - up * height
    p3 = center - right * width

    normal = _normalize(np.cross(p1 - p0, p2 - p0))

    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p1)
    _push_vertex(data, normal, p2)
    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p2)
    _push_vertex(data, normal, p3)

    back = -normal
    _push_vertex(data, back, p2)
    _push_vertex(data, back, p1)
    _push_vertex(data, back, p0)
    _push_vertex(data, back, p3)
    _push_vertex(data, back, p2)
    _push_vertex(data, back, p0)


def generate_sakura_canopy_fill_data(seed=12, variant=0):
    rng = np.random.default_rng(seed + 400 + variant * 83)
    data = []

    if variant == 0:
        count = 5400
        crown_count = 1200
        size = (0.056, 0.128)
    else:
        count = 2600
        crown_count = 520
        size = (0.048, 0.108)

    vertical = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    for _ in range(count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = 3.58 * math.sqrt(rng.uniform(0.0, 1.0))
        height = 2.34 + (1.0 - (radius / 3.68) ** 1.68) * 1.48
        height += rng.normal(0.0, 0.32)

        if radius > 2.45 and rng.random() < 0.62:
            height -= rng.uniform(0.10, 0.42)
        elif rng.random() < 0.40:
            height += rng.uniform(0.26, 0.82)
        if radius < 1.65 and rng.random() < 0.70:
            height += rng.uniform(0.30, 0.96)

        lower_edge = 1.70 + max(0.0, radius - 2.35) * 0.10
        upper_edge = 5.08 - 0.07 * radius
        height = max(lower_edge, min(upper_edge, height))

        center = np.array(
            [
                math.cos(angle) * radius + rng.normal(0.0, 0.12),
                height,
                math.sin(angle) * radius * 0.92 + rng.normal(0.0, 0.12),
            ],
            dtype=np.float32,
        )

        card_angle = rng.uniform(0.0, 2.0 * math.pi)
        right_a = np.array(
            [math.cos(card_angle), 0.0, math.sin(card_angle)], dtype=np.float32
        )
        right_b = np.array([-right_a[2], 0.0, right_a[0]], dtype=np.float32)
        card_size = rng.uniform(size[0], size[1])

        _add_canopy_card(
            data,
            center,
            right_a,
            vertical,
            width=card_size * rng.uniform(0.70, 1.05),
            height=card_size * rng.uniform(0.45, 0.82),
        )
        _add_canopy_card(
            data,
            center + rng.normal(0.0, 0.018, 3).astype(np.float32),
            right_b,
            vertical,
            width=card_size * rng.uniform(0.55, 0.95),
            height=card_size * rng.uniform(0.42, 0.78),
        )

    # Lapisan atas tambahan untuk menutup ranting yang muncul di pucuk.
    for _ in range(crown_count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = 2.70 * math.sqrt(rng.uniform(0.0, 1.0))
        height = rng.uniform(4.05, 5.18) - (radius / 2.70) * rng.uniform(0.08, 0.34)

        center = np.array(
            [
                math.cos(angle) * radius * rng.uniform(0.90, 1.04)
                + rng.normal(0.0, 0.10),
                height + rng.normal(0.0, 0.08),
                math.sin(angle) * radius * 0.88 + rng.normal(0.0, 0.10),
            ],
            dtype=np.float32,
        )

        card_angle = rng.uniform(0.0, 2.0 * math.pi)
        right_a = np.array(
            [math.cos(card_angle), 0.0, math.sin(card_angle)], dtype=np.float32
        )
        right_b = np.array([-right_a[2], 0.0, right_a[0]], dtype=np.float32)
        card_size = rng.uniform(size[0] * 0.88, size[1] * 1.08)

        _add_canopy_card(
            data,
            center,
            right_a,
            vertical,
            width=card_size * rng.uniform(0.64, 1.04),
            height=card_size * rng.uniform(0.44, 0.84),
        )
        _add_canopy_card(
            data,
            center + rng.normal(0.0, 0.014, 3).astype(np.float32),
            right_b,
            vertical,
            width=card_size * rng.uniform(0.52, 0.90),
            height=card_size * rng.uniform(0.42, 0.76),
        )

    return np.array(data, dtype=np.float32)


def _add_blossom(data, rng, center, size):
    n = _normalize(rng.normal(0.0, 1.0, 3).astype(np.float32))
    right, up, _ = _make_basis(n)

    for i in range(5):
        angle = 2.0 * math.pi * i / 5.0 + rng.uniform(-0.10, 0.10)

        petal_dir = math.cos(angle) * right + math.sin(angle) * up
        petal_up = _normalize(petal_dir)
        petal_right = _normalize(np.cross(n, petal_up))
        petal_center = center + petal_up * size * 0.18

        _add_petal(
            data,
            petal_center,
            petal_right,
            petal_up,
            length=size * rng.uniform(0.55, 0.82),
            width=size * rng.uniform(0.18, 0.30),
        )


def generate_sakura_blossom_data(seed=12, variant=0):
    rng = np.random.default_rng(seed + 100 + variant * 91)
    _, tips = build_sakura_skeleton(seed=seed)

    data = []

    if variant == 0:
        blossoms_per_tip = (14, 20)
        spread = (0.18, 0.78)
        size = (0.028, 0.050)
        cloud_count = 4300
        crown_count = 2100
    else:
        blossoms_per_tip = (7, 10)
        spread = (0.05, 0.16)
        size = (0.023, 0.040)
        cloud_count = 1750
        crown_count = 860

    spread_min, spread_max = sorted(spread)

    for tip in tips:
        count = int(rng.integers(blossoms_per_tip[0], blossoms_per_tip[1] + 1))

        if tip[1] > 4.05:
            count += 4 if variant == 0 else 2
        if np.linalg.norm(tip[[0, 2]]) > 2.35:
            count += 2 if variant == 0 else 1

        for _ in range(count):
            offset = rng.normal(0.0, rng.uniform(spread_min, spread_max), 3).astype(
                np.float32
            )
            offset[1] *= 0.80 if tip[1] > 4.05 else 0.65
            if tip[1] > 4.05:
                offset[1] += rng.uniform(0.03, 0.16)

            center = tip + offset
            _add_blossom(data, rng, center, rng.uniform(size[0], size[1]))

    for _ in range(cloud_count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = 3.60 * math.sqrt(rng.uniform(0.0, 1.0))
        height = 2.40 + (1.0 - (radius / 3.68) ** 1.72) * 1.55
        height += rng.normal(0.0, 0.38)

        center = np.array(
            [
                math.cos(angle) * radius + rng.normal(0.0, 0.16),
                height,
                math.sin(angle) * radius * 0.92 + rng.normal(0.0, 0.16),
            ],
            dtype=np.float32,
        )

        lower_edge = 1.74 + max(0.0, radius - 2.35) * 0.10
        upper_edge = 4.92 - 0.08 * radius

        if radius > 2.45 and rng.random() < 0.58:
            center[1] -= rng.uniform(0.12, 0.48)
        elif radius < 1.55 and rng.random() < 0.52:
            center[1] += rng.uniform(0.18, 0.62)

        if center[1] > upper_edge:
            center[1] = upper_edge + rng.normal(0.0, 0.06)

        if center[1] < lower_edge:
            center[1] = lower_edge + rng.uniform(0.0, 0.22)

        _add_blossom(data, rng, center, rng.uniform(size[0], size[1]))

    # Gugus bunga tambahan di mahkota atas supaya ranting tidak menonjol keluar.
    for _ in range(crown_count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = 2.85 * math.sqrt(rng.uniform(0.0, 1.0))
        center = np.array(
            [
                math.cos(angle) * radius * rng.uniform(0.90, 1.04)
                + rng.normal(0.0, 0.12),
                rng.uniform(4.04, 5.28)
                - (radius / 2.85) * rng.uniform(0.10, 0.42)
                + rng.normal(0.0, 0.08),
                math.sin(angle) * radius * 0.88 + rng.normal(0.0, 0.12),
            ],
            dtype=np.float32,
        )

        _add_blossom(data, rng, center, rng.uniform(size[0] * 0.95, size[1] * 1.10))

    return np.array(data, dtype=np.float32)


def generate_sakura_wood_data(seed=12):
    segments, _ = build_sakura_skeleton(seed=seed)
    data = []

    for p0, p1, r0, r1 in segments:
        _add_frustum(data, p0, p1, r0, r1, sides=12)

    return np.array(data, dtype=np.float32)
