import math

from ..data.scene_config import HOUSE_SPECS, SCENE_LAYOUT
from ..models import (
    AtmosphereSunDisc,
    AuroraBand,
    CloudLayer,
    ColorCube,
    ColorPlane,
    FireflyGlow,
    FloatingPetals,
    FujiPeak,
    FujiSnowcap,
    IceSurface,
    IslandGrass,
    IslandMound,
    NightGlow,
    PondRock,
    RainDrop,
    SakuraBlossomDeep,
    SakuraBlossomLight,
    SakuraCanopyDeep,
    SakuraCanopyLight,
    SakuraWood,
    MoonDisc,
    SkyDome,
    SunDisc,
    TexturedCube,
    TexturedGableRoof,
    TexturedPlane,
    TransitionCube,
    WaterReflection,
    WaterSurface,
    WindStreak,
)


class SceneVillageBridgeMixin:
    def add_bridge(self, app):
        add = self.add_object

        deck_base_color = (0.46, 0.28, 0.14)
        deck_highlight = (0.60, 0.38, 0.20)
        deck_shadow = (0.20, 0.12, 0.07)
        rail_color = (0.78, 0.18, 0.12)
        rail_shadow = (0.42, 0.10, 0.08)
        footing_color = (0.44, 0.41, 0.38)
        post_cap_color = (0.90, 0.70, 0.38)

        pond_radius_scale = SCENE_LAYOUT["pond"]["radius_scale"]
        island_radius_scale = SCENE_LAYOUT["island"]["radius_scale"]

        start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
        end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)

        y_base = 0.16
        arch_height = 0.88
        bridge_width = 1.30
        segments = 20
        plank_count = 5
        plank_gap = 0.03
        plank_full_width = (bridge_width - plank_gap * (plank_count - 1)) / plank_count

        def bridge_point(t):
            inv_t = 1.0 - t
            x = (
                inv_t * inv_t * start[0]
                + 2.0 * inv_t * t * control[0]
                + t * t * end[0]
            )
            z = (
                inv_t * inv_t * start[1]
                + 2.0 * inv_t * t * control[1]
                + t * t * end[1]
            )
            y = y_base + math.sin(math.pi * t) * arch_height
            return (x, y, z)

        def bridge_frame(a, b):
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            dz = b[2] - a[2]
            horizontal = math.sqrt(dx * dx + dz * dz)
            yaw = math.degrees(math.atan2(dx, dz))
            pitch = -math.degrees(math.atan2(dy, horizontal + 1e-6))
            lat_x = -dz / (horizontal + 1e-6)
            lat_z = dx / (horizontal + 1e-6)
            return horizontal, yaw, pitch, lat_x, lat_z

        points = [bridge_point(i / segments) for i in range(segments + 1)]

        # Pondasi batu di awal dan akhir jembatan supaya transisinya lebih rapi.
        for idx, point in ((0, points[0]), (segments - 1, points[-1])):
            ref_a = points[idx]
            ref_b = points[idx + 1]
            _, yaw, _, lat_x, lat_z = bridge_frame(ref_a, ref_b)

            add(
                ColorCube(
                    app,
                    pos=(point[0], point[1] - 0.10, point[2]),
                    rot=(0, yaw, 0),
                    scale=(bridge_width * 0.34, 0.08, 0.24),
                    color=(0.30, 0.22, 0.15),
                )
            )

            for side in (-1, 1):
                side_offset = side * bridge_width * 0.48
                add(
                    ColorCube(
                        app,
                        pos=(
                            point[0] + lat_x * side_offset,
                            point[1] - 0.02,
                            point[2] + lat_z * side_offset,
                        ),
                        rot=(0, yaw, 0),
                        scale=(0.18, 0.12, 0.24),
                        color=footing_color,
                    )
                )

        # Deck berlapis dengan balok bawah agar jembatan lebih terasa tebal.
        for i in range(segments):
            p0 = points[i]
            p1 = points[i + 1]

            xm = (p0[0] + p1[0]) * 0.5
            ym = (p0[1] + p1[1]) * 0.5
            zm = (p0[2] + p1[2]) * 0.5

            horizontal, yaw, pitch, lat_x, lat_z = bridge_frame(p0, p1)
            seg_len = horizontal * 0.52 + 0.06

            add(
                ColorCube(
                    app,
                    pos=(xm, ym - 0.07, zm),
                    rot=(pitch, yaw, 0),
                    scale=(bridge_width * 0.45, 0.03, seg_len + 0.03),
                    color=deck_shadow,
                )
            )

            for beam_offset in (-0.26, 0.26):
                add(
                    ColorCube(
                        app,
                        pos=(
                            xm + lat_x * beam_offset,
                            ym - 0.12,
                            zm + lat_z * beam_offset,
                        ),
                        rot=(pitch, yaw, 0),
                        scale=(0.055, 0.05, seg_len),
                        color=(0.16, 0.10, 0.06),
                    )
                )

            add(
                ColorCube(
                    app,
                    pos=(xm, ym - 0.04, zm),
                    rot=(pitch, yaw, 0),
                    scale=(bridge_width * 0.40, 0.018, 0.05),
                    color=(0.28, 0.18, 0.10),
                )
            )

            for plank_idx in range(plank_count):
                offset = (
                    -bridge_width * 0.5
                    + plank_full_width * 0.5
                    + plank_idx * (plank_full_width + plank_gap)
                )
                plank_color = (
                    deck_highlight if plank_idx in (1, 3) else deck_base_color
                )
                tone = 0.025 * math.sin(i * 1.3 + plank_idx * 0.8)
                plank_color = tuple(
                    max(0.0, min(1.0, channel + tone)) for channel in plank_color
                )

                add(
                    ColorCube(
                        app,
                        pos=(
                            xm + lat_x * offset,
                            ym + 0.01,
                            zm + lat_z * offset,
                        ),
                        rot=(pitch, yaw, 0),
                        scale=(plank_full_width * 0.5, 0.032, seg_len),
                        color=plank_color,
                    )
                )

            for side in (-1, 1):
                rail_offset = side * bridge_width * 0.48
                rail_x = xm + lat_x * rail_offset
                rail_z = zm + lat_z * rail_offset

                add(
                    ColorCube(
                        app,
                        pos=(rail_x, ym + 0.10, rail_z),
                        rot=(pitch, yaw, 0),
                        scale=(0.055, 0.035, seg_len + 0.03),
                        color=rail_shadow,
                    )
                )

                add(
                    ColorCube(
                        app,
                        pos=(rail_x, ym + 0.42, rail_z),
                        rot=(pitch, yaw, 0),
                        scale=(0.028, 0.028, seg_len + 0.01),
                        color=rail_shadow,
                    )
                )

                add(
                    ColorCube(
                        app,
                        pos=(rail_x, ym + 0.64, rail_z),
                        rot=(pitch, yaw, 0),
                        scale=(0.04, 0.03, seg_len + 0.04),
                        color=rail_color,
                    )
                )

        # Tiang pagar dengan ujung lebih tinggi di kedua sisi masuk.
        for i, point in enumerate(points):
            if i == 0:
                ref_a = points[0]
                ref_b = points[1]
            elif i == len(points) - 1:
                ref_a = points[-2]
                ref_b = points[-1]
            else:
                ref_a = points[i - 1]
                ref_b = points[i + 1]

            _, yaw, _, lat_x, lat_z = bridge_frame(ref_a, ref_b)
            post_half_height = 0.40 if i in (0, len(points) - 1) else 0.34
            cap_scale = 0.09 if i in (0, len(points) - 1) else 0.07

            for side in (-1, 1):
                post_offset = side * bridge_width * 0.48
                px = point[0] + lat_x * post_offset
                pz = point[2] + lat_z * post_offset

                add(
                    ColorCube(
                        app,
                        pos=(px, point[1] + post_half_height, pz),
                        rot=(0, yaw, 0),
                        scale=(0.045, post_half_height, 0.045),
                        color=rail_color,
                    )
                )

                add(
                    ColorCube(
                        app,
                        pos=(px, point[1] + post_half_height * 2.0 + 0.05, pz),
                        rot=(0, yaw, 0),
                        scale=(cap_scale, 0.04, cap_scale),
                        color=post_cap_color,
                    )
                )
