from .core import BaseModelColor, BaseModelEmissiveTexture, BaseModelTexture


class TexturedPlane(BaseModelTexture):
    def __init__(
        self,
        app,
        vao_name="textured_plane",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="grass",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class TexturedCube(BaseModelTexture):
    def __init__(
        self,
        app,
        vao_name="textured_cube",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="wall",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class TexturedGableRoof(BaseModelTexture):
    def __init__(
        self,
        app,
        vao_name="textured_gable_roof",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="roof",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class EmissiveTexturedPlane(BaseModelEmissiveTexture):
    def __init__(
        self,
        app,
        vao_name="emissive_textured_plane",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="white",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class ColorCube(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 1.0, 1.0),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class ColorPlane(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="color_plane",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 1.0, 1.0),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class GableRoof(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="gable_roof",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.46, 0.16, 0.11),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)
