import math

from pyglm import glm
import pygame as pg

from .data.scene_config import CAMERA_PRESETS

FOV = 62
NEAR = 0.1
FAR = 100.0
MOUSE_SENS = 0.04


class Camera:
    def __init__(self, app, position=(0.0, 2.35, 15.6), look_lr=270.0, look_ud=4.4):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]

        self.position = glm.vec3(position)
        self.world_up = glm.vec3(0, 1, 0)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.look_lr = look_lr
        self.look_ud = look_ud

        self.use_orbit = False
        self.orbit_target = glm.vec3(0, 0.8, 0)
        self.orbit_radius = 10.0
        self.cinematic_enabled = False
        self.cinematic_duration = 22.0
        self.preset_name = "free"

        self.m_proj = self.get_projection_matrix()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        self.look_lr += rel_x * MOUSE_SENS
        self.look_ud -= rel_y * MOUSE_SENS
        self.look_ud = max(-89.0, min(89.0, self.look_ud))

    def update_camera_vectors(self):
        yaw = glm.radians(self.look_lr)
        pitch = glm.radians(self.look_ud)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)
        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def look_at(self, target):
        target = glm.vec3(target)
        direction = glm.normalize(target - self.position)
        self.look_lr = math.degrees(math.atan2(direction.z, direction.x))
        self.look_ud = math.degrees(math.asin(max(-1.0, min(1.0, direction.y))))
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self):
        keys = pg.key.get_pressed()
        velocity = 0.02 * self.app.delta_time
        if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
            velocity = 0.05 * self.app.delta_time
        elif keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
            velocity = 0.004 * self.app.delta_time

        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_q]:
            self.position -= self.up * velocity
        if keys[pg.K_e]:
            self.position += self.up * velocity

    def update_orbit(self):
        keys = pg.key.get_pressed()
        rotate_speed = 0.05 * self.app.delta_time
        if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
            rotate_speed = 0.10 * self.app.delta_time
        elif keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
            rotate_speed = 0.02 * self.app.delta_time

        if keys[pg.K_LEFT]:
            self.look_lr += rotate_speed
        if keys[pg.K_RIGHT]:
            self.look_lr -= rotate_speed
        if keys[pg.K_UP]:
            self.look_ud += rotate_speed
        if keys[pg.K_DOWN]:
            self.look_ud -= rotate_speed

        rel_x, rel_y = pg.mouse.get_rel()
        self.look_lr += rel_x * MOUSE_SENS
        self.look_ud -= rel_y * MOUSE_SENS
        self.look_ud = max(-89.0, min(89.0, self.look_ud))

        theta = glm.radians(self.look_lr)
        phi = glm.radians(self.look_ud)
        x = self.orbit_radius * glm.cos(phi) * glm.cos(theta)
        y = self.orbit_radius * glm.sin(phi)
        z = self.orbit_radius * glm.cos(phi) * glm.sin(theta)

        self.position = self.orbit_target + glm.vec3(x, y, z)
        self.forward = glm.normalize(self.orbit_target - self.position)
        self.right = glm.normalize(glm.cross(self.forward, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.forward))
        self.m_view = self.get_view_matrix()

    def update(self):
        if self.cinematic_enabled:
            self.update_cinematic()
            return

        if self.use_orbit:
            self.update_orbit()
        else:
            self.move()
            self.rotate()
            self.update_camera_vectors()
            self.m_view = self.get_view_matrix()

    def set_default(self):
        self.cinematic_enabled = False
        self.preset_name = "orbit" if self.use_orbit else "free"
        self.position = glm.vec3(0.0, 2.35, 15.6)
        self.orbit_target = glm.vec3(0, 2.7, 0)
        self.orbit_radius = 14.2
        if self.use_orbit:
            self.look_lr = 90.0
            self.look_ud = 11.0
        else:
            self.look_lr = 270.0
            self.look_ud = 4.4
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def set_preset(self, name):
        preset = CAMERA_PRESETS.get(name)
        if preset is None:
            return

        self.cinematic_enabled = False
        self.use_orbit = False
        self.preset_name = name
        self.position = glm.vec3(preset["position"])
        self.look_at(preset["target"])
        pg.mouse.get_rel()

    def toggle_cinematic(self):
        self.cinematic_enabled = not self.cinematic_enabled
        self.use_orbit = False
        self.preset_name = "cinematic" if self.cinematic_enabled else "free"
        pg.mouse.get_rel()

    def set_season_preset(self):
        name = self.app.season_controller.current.get("camera_preset")
        if name:
            self.set_preset(name)

    def cinematic_route(self):
        return self.app.season_controller.current.get(
            "cinematic_route",
            ("sakura", "bridge", "village", "fuji"),
        )

    def cinematic_point(self, index):
        names = self.cinematic_route()
        preset = CAMERA_PRESETS[names[index % len(names)]]
        return glm.vec3(preset["position"]), glm.vec3(preset["target"])

    def update_cinematic(self):
        segment_count = len(self.cinematic_route())
        progress = (self.app.time / self.cinematic_duration) % 1.0
        segment = min(segment_count - 1, int(progress * segment_count))
        local_t = progress * segment_count - segment
        eased = local_t * local_t * (3.0 - 2.0 * local_t)

        start_pos, start_target = self.cinematic_point(segment)
        end_pos, end_target = self.cinematic_point(segment + 1)
        self.position = start_pos * (1.0 - eased) + end_pos * eased
        target = start_target * (1.0 - eased) + end_target * eased
        self.look_at(target)

    def resize(self, win_size):
        self.aspect_ratio = win_size[0] / win_size[1]
        self.m_proj = self.get_projection_matrix()
        self.m_view = self.get_view_matrix()

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
