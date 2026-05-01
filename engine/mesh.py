from .texture import TextureManager
from .vao import VAO


class Mesh:
    def __init__(self, app):
        self.app = app
        self.texture = TextureManager(app.ctx)
        self.vao = VAO(app.ctx)

    def destroy(self):
        self.vao.destroy()
        self.texture.destroy()
