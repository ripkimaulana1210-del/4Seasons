import math

from pyglm import glm

from .atmosphere import SunDisc
from .core import _lerp_vec3, _transition_local_progress
from .primitives import ColorCube


class TransitionCube(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 0, 0),
        end_pos=None,
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        end_scale=None,
        color=(1.0, 1.0, 1.0),
        end_color=None,
        progress_start=0.0,
        progress_end=1.0,
        pulse=0.0,
        use_eased=True,
    ):
        self.start_pos = glm.vec3(pos)
        self.end_pos = glm.vec3(end_pos if end_pos is not None else pos)
        self.start_scale = glm.vec3(scale)
        self.end_scale = glm.vec3(end_scale if end_scale is not None else scale)
        self.start_color = glm.vec3(color)
        self.end_color = glm.vec3(end_color if end_color is not None else color)
        self.progress_start = progress_start
        self.progress_end = progress_end
        self.pulse = pulse
        self.use_eased = use_eased
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        progress = _transition_local_progress(
            self.app,
            self.progress_start,
            self.progress_end,
            self.use_eased,
        )
        pulse = 1.0
        if self.pulse:
            pulse += math.sin(self.app.time * math.tau * 1.7 + self.phase_offset()) * self.pulse

        self.pos = _lerp_vec3(self.start_pos, self.end_pos, progress)
        self.scale = _lerp_vec3(self.start_scale, self.end_scale, progress) * pulse
        self.color = _lerp_vec3(self.start_color, self.end_color, progress)
        self.m_model = self.get_model_matrix()
        super().update()

    def phase_offset(self):
        return self.start_pos.x * 0.37 + self.start_pos.z * 0.23 + self.progress_start * 5.0


class TransitionDisc(SunDisc):
    def __init__(
        self,
        app,
        vao_name="sun_disc",
        pos=(0, 0, 0),
        end_pos=None,
        rot=(90, 0, 0),
        scale=(1, 1, 1),
        end_scale=None,
        color=(1.0, 1.0, 1.0),
        end_color=None,
        alpha_start=0.0,
        alpha_peak=0.18,
        alpha_end=0.0,
        progress_start=0.0,
        progress_peak=None,
        progress_end=1.0,
        pulse=0.0,
        use_eased=True,
    ):
        self.start_pos = glm.vec3(pos)
        self.end_pos = glm.vec3(end_pos if end_pos is not None else pos)
        self.start_scale = glm.vec3(scale)
        self.end_scale = glm.vec3(end_scale if end_scale is not None else scale)
        self.start_color = glm.vec3(color)
        self.end_color = glm.vec3(end_color if end_color is not None else color)
        self.alpha_start = alpha_start
        self.alpha_peak = alpha_peak
        self.alpha_end = alpha_end
        self.progress_start = progress_start
        self.progress_peak = progress_peak if progress_peak is not None else (progress_start + progress_end) * 0.5
        self.progress_end = progress_end
        self.pulse = pulse
        self.use_eased = use_eased
        super().__init__(app, vao_name=vao_name, pos=pos, rot=rot, scale=scale, color=color, alpha=alpha_start)

    def update(self):
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            progress = 1.0
        else:
            progress = transition["eased"] if self.use_eased else transition["progress"]

        total = _transition_local_progress(
            self.app,
            self.progress_start,
            self.progress_end,
            self.use_eased,
        )
        if progress <= self.progress_peak:
            alpha_t = _transition_local_progress(
                self.app,
                self.progress_start,
                self.progress_peak,
                self.use_eased,
            )
            self.alpha = self.alpha_start + (self.alpha_peak - self.alpha_start) * alpha_t
        else:
            alpha_t = _transition_local_progress(
                self.app,
                self.progress_peak,
                self.progress_end,
                self.use_eased,
            )
            self.alpha = self.alpha_peak + (self.alpha_end - self.alpha_peak) * alpha_t

        pulse = 1.0
        if self.pulse:
            pulse += math.sin(self.app.time * math.tau * 1.2 + self.start_pos.x * 0.2 + self.start_pos.z * 0.3) * self.pulse

        self.pos = _lerp_vec3(self.start_pos, self.end_pos, total)
        self.scale = _lerp_vec3(self.start_scale, self.end_scale, total) * pulse
        self.color = _lerp_vec3(self.start_color, self.end_color, total)
        self.m_model = self.get_model_matrix()
        super().update()


class RainDrop(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 6, 0),
        rot=(18, 0, -12),
        scale=(0.010, 0.42, 0.010),
        color=(0.58, 0.76, 0.88),
        fall_distance=7.0,
        speed=0.34,
        phase=0.0,
        drift=(0.45, 0.0, -0.28),
    ):
        self.base_pos = glm.vec3(pos)
        self.fall_distance = fall_distance
        self.speed = speed
        self.phase = phase
        self.drift = glm.vec3(drift)
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        progress = (self.app.time * self.speed + self.phase) % 1.0
        self.pos = glm.vec3(
            self.base_pos.x + self.drift.x * progress,
            self.base_pos.y - self.fall_distance * progress,
            self.base_pos.z + self.drift.z * progress,
        )
        self.m_model = self.get_model_matrix()
        super().update()


class DriftParticle(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 4, 0),
        rot=(0, 0, 0),
        scale=(0.035, 0.006, 0.020),
        color=(1.0, 0.72, 0.88),
        fall_distance=4.0,
        drift=(1.0, 0.0, -0.45),
        speed=0.09,
        phase=0.0,
        spin_speed=90.0,
        sway=0.22,
    ):
        self.base_pos = glm.vec3(pos)
        self.base_rot = glm.vec3([glm.radians(a) for a in rot])
        self.fall_distance = fall_distance
        self.drift = glm.vec3(drift)
        self.speed = speed
        self.phase = phase
        self.spin_speed = glm.radians(spin_speed)
        self.sway = sway
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        speed_boost = self.app.season_controller.get_blended_season().get("particle_speed_boost", 1.0)
        progress = (self.app.time * self.speed * speed_boost + self.phase) % 1.0
        wave = math.sin((progress + self.phase) * math.tau)
        cross = math.cos((progress * 1.7 + self.phase) * math.tau)
        self.pos = glm.vec3(
            self.base_pos.x + self.drift.x * (progress - 0.5) + self.sway * 0.18 * cross,
            self.base_pos.y - self.fall_distance * progress + self.sway * 0.08 * wave,
            self.base_pos.z + self.drift.z * (progress - 0.5) + self.sway * 0.12 * wave,
        )
        self.rot = glm.vec3(
            self.base_rot.x + wave * 0.20,
            self.base_rot.y + self.spin_speed * progress,
            self.base_rot.z + cross * 0.30,
        )
        self.m_model = self.get_model_matrix()
        super().update()


class WindStreak(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 2, 0),
        rot=(0, 64, 0),
        scale=(0.34, 0.012, 0.018),
        color=(0.86, 0.94, 0.95),
        travel=(1.4, 0.0, -0.55),
        speed=0.18,
        phase=0.0,
        bob=0.16,
    ):
        self.base_pos = glm.vec3(pos)
        self.travel = glm.vec3(travel)
        self.speed = speed
        self.phase = phase
        self.bob = bob
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        boost = self.app.season_controller.get_blended_season().get("wind_motion_boost", 1.0)
        progress = (self.app.time * self.speed * boost + self.phase) % 1.0
        wave = math.sin((progress + self.phase) * math.tau)
        self.pos = glm.vec3(
            self.base_pos.x + self.travel.x * boost * (progress - 0.5),
            self.base_pos.y + self.bob * boost * wave,
            self.base_pos.z + self.travel.z * boost * (progress - 0.5),
        )
        self.m_model = self.get_model_matrix()
        super().update()
