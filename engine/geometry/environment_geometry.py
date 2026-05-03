import math
import numpy as np


def _normalize(v):
    v = np.asarray(v, dtype=np.float32)
    n = float(np.linalg.norm(v))
    if n < 1e-6:
        return np.array([0.0, 1.0, 0.0], dtype=np.float32)
    return v / n


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


def _push_double_sided_tri(data, p0, p1, p2):
    normal = _normalize(np.cross(p1 - p0, p2 - p0))

    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p1)
    _push_vertex(data, normal, p2)

    back = -normal
    _push_vertex(data, back, p2)
    _push_vertex(data, back, p1)
    _push_vertex(data, back, p0)


def _push_double_sided_quad(data, p0, p1, p2, p3):
    _push_double_sided_tri(data, p0, p1, p2)
    _push_double_sided_tri(data, p0, p2, p3)


def _push_vertex_uv(data, normal, position, uv):
    data.append(
        [
            float(normal[0]),
            float(normal[1]),
            float(normal[2]),
            float(position[0]),
            float(position[1]),
            float(position[2]),
            float(uv[0]),
            float(uv[1]),
        ]
    )


def _water_uv(point, radius):
    return (
        float((point[0] / radius) * 0.5 + 0.5),
        float((point[2] / radius) * 0.5 + 0.5),
    )


def generate_water_surface_data(radius=4.8, rings=36, sectors=128):
    """Circular pond only. Everything outside this mesh remains land."""
    data = []
    normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    center = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    # Inner fan. Winding is chosen to face upward even when CULL_FACE is on.
    inner_radius = radius / rings
    for s in range(sectors):
        a0 = 2.0 * math.pi * s / sectors
        a1 = 2.0 * math.pi * (s + 1) / sectors
        p0 = np.array([math.cos(a0) * inner_radius, 0.0, math.sin(a0) * inner_radius], dtype=np.float32)
        p1 = np.array([math.cos(a1) * inner_radius, 0.0, math.sin(a1) * inner_radius], dtype=np.float32)

        _push_vertex_uv(data, normal, center, _water_uv(center, radius))
        _push_vertex_uv(data, normal, p1, _water_uv(p1, radius))
        _push_vertex_uv(data, normal, p0, _water_uv(p0, radius))

    # Outer rings.
    for r in range(1, rings):
        r0 = radius * r / rings
        r1 = radius * (r + 1) / rings

        for s in range(sectors):
            a0 = 2.0 * math.pi * s / sectors
            a1 = 2.0 * math.pi * (s + 1) / sectors

            p00 = np.array([math.cos(a0) * r0, 0.0, math.sin(a0) * r0], dtype=np.float32)
            p01 = np.array([math.cos(a1) * r0, 0.0, math.sin(a1) * r0], dtype=np.float32)
            p10 = np.array([math.cos(a0) * r1, 0.0, math.sin(a0) * r1], dtype=np.float32)
            p11 = np.array([math.cos(a1) * r1, 0.0, math.sin(a1) * r1], dtype=np.float32)

            # Two triangles, upward winding.
            _push_vertex_uv(data, normal, p00, _water_uv(p00, radius))
            _push_vertex_uv(data, normal, p01, _water_uv(p01, radius))
            _push_vertex_uv(data, normal, p11, _water_uv(p11, radius))

            _push_vertex_uv(data, normal, p00, _water_uv(p00, radius))
            _push_vertex_uv(data, normal, p11, _water_uv(p11, radius))
            _push_vertex_uv(data, normal, p10, _water_uv(p10, radius))

    return np.array(data, dtype=np.float32)


def _island_height(radius, max_radius):
    t = max(0.0, min(1.0, radius / max_radius))
    dome = (1.0 - t * t) ** 0.65
    return 0.02 + 0.30 * dome


def generate_island_mound_data(radius=1.45, rings=9, sectors=96):
    data = []
    points = []

    for r in range(rings + 1):
        ring_radius = radius * r / rings
        ring = []
        for s in range(sectors):
            angle = 2.0 * math.pi * s / sectors
            x = math.cos(angle) * ring_radius
            z = math.sin(angle) * ring_radius
            y = _island_height(ring_radius, radius)
            ring.append(np.array([x, y, z], dtype=np.float32))
        points.append(ring)

    center = np.array([0.0, _island_height(0.0, radius), 0.0], dtype=np.float32)

    for s in range(sectors):
        nxt = (s + 1) % sectors
        p1 = points[1][s]
        p2 = points[1][nxt]
        normal = _normalize(np.cross(p1 - center, p2 - center))
        if normal[1] < 0.0:
            normal = -normal
        _push_vertex(data, normal, center)
        _push_vertex(data, normal, p1)
        _push_vertex(data, normal, p2)

    for r in range(1, rings):
        for s in range(sectors):
            nxt = (s + 1) % sectors
            p0 = points[r][s]
            p1 = points[r + 1][s]
            p2 = points[r + 1][nxt]
            p3 = points[r][nxt]

            normal_a = _normalize(np.cross(p1 - p0, p2 - p0))
            normal_b = _normalize(np.cross(p2 - p0, p3 - p0))
            if normal_a[1] < 0.0:
                normal_a = -normal_a
            if normal_b[1] < 0.0:
                normal_b = -normal_b

            _push_vertex(data, normal_a, p0)
            _push_vertex(data, normal_a, p1)
            _push_vertex(data, normal_a, p2)

            _push_vertex(data, normal_b, p0)
            _push_vertex(data, normal_b, p2)
            _push_vertex(data, normal_b, p3)

    side_bottom_y = -0.04
    for s in range(sectors):
        nxt = (s + 1) % sectors
        top0 = points[rings][s]
        top1 = points[rings][nxt]
        bot0 = np.array([top0[0], side_bottom_y, top0[2]], dtype=np.float32)
        bot1 = np.array([top1[0], side_bottom_y, top1[2]], dtype=np.float32)
        side_normal = _normalize(np.array([top0[0], 0.0, top0[2]], dtype=np.float32))

        _push_vertex(data, side_normal, bot0)
        _push_vertex(data, side_normal, top0)
        _push_vertex(data, side_normal, top1)

        _push_vertex(data, side_normal, bot0)
        _push_vertex(data, side_normal, top1)
        _push_vertex(data, side_normal, bot1)

    return np.array(data, dtype=np.float32)


def _add_grass_blade(data, base, angle, height, width, lean):
    right = np.array([math.cos(angle), 0.0, math.sin(angle)], dtype=np.float32)
    forward = np.array([-math.sin(angle), 0.0, math.cos(angle)], dtype=np.float32)

    p0 = base - right * width
    p1 = base + right * width
    p2 = base + forward * lean + np.array([0.0, height, 0.0], dtype=np.float32)

    _push_double_sided_tri(data, p0, p1, p2)


def generate_island_grass_data(seed=21, count=950, radius=1.86):
    rng = np.random.default_rng(seed)
    data = []

    for _ in range(count):
        ring_radius = math.sqrt(rng.uniform(0.18 * 0.18, radius * radius))
        angle = rng.uniform(0.0, 2.0 * math.pi)
        x = math.cos(angle) * ring_radius
        z = math.sin(angle) * ring_radius
        y = _island_height(ring_radius, radius) + 0.018

        base = np.array([x, y, z], dtype=np.float32)
        blades = int(rng.integers(2, 5))

        for _ in range(blades):
            blade_angle = angle + rng.uniform(-1.4, 1.4)
            _add_grass_blade(
                data,
                base + rng.normal(0.0, 0.018, 3).astype(np.float32),
                blade_angle,
                height=rng.uniform(0.075, 0.19),
                width=rng.uniform(0.006, 0.014),
                lean=rng.uniform(0.015, 0.085),
            )

    return np.array(data, dtype=np.float32)


def generate_rock_data(lat_steps=8, lon_steps=14):
    data = []

    for i in range(lat_steps):
        theta0 = math.pi * i / lat_steps
        theta1 = math.pi * (i + 1) / lat_steps

        for j in range(lon_steps):
            phi0 = 2.0 * math.pi * j / lon_steps
            phi1 = 2.0 * math.pi * (j + 1) / lon_steps

            def point(theta, phi):
                x = math.sin(theta) * math.cos(phi)
                y = math.cos(theta) * 0.68
                z = math.sin(theta) * math.sin(phi)
                p = np.array([x, y, z], dtype=np.float32)
                p[1] = max(p[1], -0.42)
                p[0] *= 1.0 + 0.10 * math.sin(phi * 3.0)
                p[2] *= 0.85 + 0.08 * math.cos(phi * 2.0)
                return p

            p0 = point(theta0, phi0)
            p1 = point(theta1, phi0)
            p2 = point(theta1, phi1)
            p3 = point(theta0, phi1)

            normal_a = _normalize(np.cross(p1 - p0, p2 - p0))
            normal_b = _normalize(np.cross(p2 - p0, p3 - p0))

            _push_vertex(data, normal_a, p0)
            _push_vertex(data, normal_a, p1)
            _push_vertex(data, normal_a, p2)

            _push_vertex(data, normal_b, p0)
            _push_vertex(data, normal_b, p2)
            _push_vertex(data, normal_b, p3)

    return np.array(data, dtype=np.float32)


def generate_gable_roof_data():
    data = []

    left_front = np.array([-1.0, 0.0, 1.0], dtype=np.float32)
    right_front = np.array([1.0, 0.0, 1.0], dtype=np.float32)
    ridge_front = np.array([0.0, 1.0, 1.0], dtype=np.float32)
    left_back = np.array([-1.0, 0.0, -1.0], dtype=np.float32)
    right_back = np.array([1.0, 0.0, -1.0], dtype=np.float32)
    ridge_back = np.array([0.0, 1.0, -1.0], dtype=np.float32)

    _push_double_sided_quad(data, left_front, ridge_front, ridge_back, left_back)
    _push_double_sided_quad(data, ridge_front, right_front, right_back, ridge_back)
    _push_double_sided_tri(data, left_front, right_front, ridge_front)
    _push_double_sided_tri(data, right_back, left_back, ridge_back)
    _push_double_sided_quad(data, right_front, left_front, left_back, right_back)

    return np.array(data, dtype=np.float32)


def generate_sun_disc_data(sectors=96):
    data = []
    normal = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    center = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    for s in range(sectors):
        a0 = 2.0 * math.pi * s / sectors
        a1 = 2.0 * math.pi * (s + 1) / sectors
        p0 = np.array([math.cos(a0), math.sin(a0), 0.0], dtype=np.float32)
        p1 = np.array([math.cos(a1), math.sin(a1), 0.0], dtype=np.float32)

        _push_vertex(data, normal, center)
        _push_vertex(data, normal, p0)
        _push_vertex(data, normal, p1)

    return np.array(data, dtype=np.float32)


def generate_water_reflection_data(seed=52, count=520, inner_radius=2.05, outer_radius=4.55):
    rng = np.random.default_rng(seed)
    data = []
    normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    for _ in range(count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = math.sqrt(rng.uniform(inner_radius * inner_radius, outer_radius * outer_radius))
        center = np.array(
            [
                math.cos(angle) * radius * rng.uniform(0.72, 1.04),
                0.052 + rng.uniform(-0.004, 0.004),
                math.sin(angle) * radius,
            ],
            dtype=np.float32,
        )

        streak_angle = rng.normal(0.0, 0.20)
        right = np.array([math.cos(streak_angle), 0.0, math.sin(streak_angle)], dtype=np.float32)
        forward = np.array([-right[2], 0.0, right[0]], dtype=np.float32)
        half_len = rng.uniform(0.018, 0.095)
        half_width = rng.uniform(0.003, 0.010)

        p0 = center - right * half_len - forward * half_width
        p1 = center + right * half_len - forward * half_width
        p2 = center + right * half_len + forward * half_width
        p3 = center - right * half_len + forward * half_width

        _push_vertex(data, normal, p0)
        _push_vertex(data, normal, p1)
        _push_vertex(data, normal, p2)
        _push_vertex(data, normal, p0)
        _push_vertex(data, normal, p2)
        _push_vertex(data, normal, p3)

    return np.array(data, dtype=np.float32)


def _add_double_sided_petal(data, center, right, forward, length, width):
    p0 = center - right * width - forward * length * 0.35
    p1 = center + right * width - forward * length * 0.35
    p2 = center + forward * length
    p3 = center - right * width * 0.55 + forward * length * 0.15

    normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    back = -normal

    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p1)
    _push_vertex(data, normal, p2)
    _push_vertex(data, normal, p0)
    _push_vertex(data, normal, p2)
    _push_vertex(data, normal, p3)

    _push_vertex(data, back, p2)
    _push_vertex(data, back, p1)
    _push_vertex(data, back, p0)
    _push_vertex(data, back, p3)
    _push_vertex(data, back, p2)
    _push_vertex(data, back, p0)


def generate_floating_petal_data(seed=44, count=260, inner_radius=1.75, outer_radius=4.55):
    rng = np.random.default_rng(seed)
    data = []

    for _ in range(count):
        # Keep petals inside the circular pond but outside the island.
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = math.sqrt(rng.uniform(inner_radius * inner_radius, outer_radius * outer_radius))
        center = np.array(
            [
                math.cos(angle) * radius,
                0.045 + rng.uniform(-0.004, 0.006),
                math.sin(angle) * radius,
            ],
            dtype=np.float32,
        )

        petal_angle = rng.uniform(0.0, 2.0 * math.pi)
        right = np.array([math.cos(petal_angle), 0.0, math.sin(petal_angle)], dtype=np.float32)
        forward = np.array([-math.sin(petal_angle), 0.0, math.cos(petal_angle)], dtype=np.float32)

        _add_double_sided_petal(
            data,
            center,
            right,
            forward,
            length=rng.uniform(0.035, 0.080),
            width=rng.uniform(0.012, 0.028),
        )

    return np.array(data, dtype=np.float32)


def _fuji_profile(radius_ratio):
    t = max(0.0, min(1.0, radius_ratio))
    cone = max(0.0, 1.0 - t ** 0.96)
    return cone ** 1.48


def _fuji_surface_point(radius, angle, max_radius=1.0, peak_height=1.0, lift=0.0):
    t = radius / max_radius if max_radius > 1e-6 else 0.0
    radial_x = 0.96 + 0.05 * math.sin(angle * 2.0)
    radial_z = 1.00 + 0.04 * math.cos(angle * 3.0)
    x = math.cos(angle) * radius * radial_x
    z = math.sin(angle) * radius * radial_z
    y = lift + peak_height * _fuji_profile(t)
    y += 0.035 * peak_height * math.sin(angle * 4.0 + radius * 3.0) * t * (1.0 - t)
    return np.array([x, y, z], dtype=np.float32)


def generate_fuji_peak_data(radius=1.0, height=1.0, rings=16, sectors=88):
    data = []
    z = 0.0
    points = [
        np.array([-radius * 1.18, 0.00, z], dtype=np.float32),
        np.array([-radius * 0.84, height * 0.22, z], dtype=np.float32),
        np.array([-radius * 0.52, height * 0.50, z], dtype=np.float32),
        np.array([-radius * 0.22, height * 0.78, z], dtype=np.float32),
        np.array([0.00, height, z], dtype=np.float32),
        np.array([radius * 0.26, height * 0.76, z], dtype=np.float32),
        np.array([radius * 0.56, height * 0.46, z], dtype=np.float32),
        np.array([radius * 0.88, height * 0.20, z], dtype=np.float32),
        np.array([radius * 1.20, 0.00, z], dtype=np.float32),
    ]
    base = np.array([0.0, 0.0, z], dtype=np.float32)

    for left, right in zip(points, points[1:]):
        _push_double_sided_tri(data, base, left, right)

    return np.array(data, dtype=np.float32)


def generate_fuji_snowcap_data(radius=1.0, height=1.0, rings=7, sectors=88):
    data = []
    z = 0.004
    peak = np.array([0.00, height * 1.01, z], dtype=np.float32)
    left = np.array([-radius * 0.34, height * 0.66, z], dtype=np.float32)
    mid_left = np.array([-radius * 0.14, height * 0.70, z], dtype=np.float32)
    center = np.array([0.00, height * 0.58, z], dtype=np.float32)
    mid_right = np.array([radius * 0.16, height * 0.69, z], dtype=np.float32)
    right = np.array([radius * 0.38, height * 0.64, z], dtype=np.float32)

    _push_double_sided_tri(data, peak, left, mid_left)
    _push_double_sided_tri(data, peak, mid_left, center)
    _push_double_sided_tri(data, peak, center, mid_right)
    _push_double_sided_tri(data, peak, mid_right, right)

    return np.array(data, dtype=np.float32)
