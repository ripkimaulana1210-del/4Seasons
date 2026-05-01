class SceneRenderer:
    def __init__(self, app):
        self.app = app
        self.scene = app.scene

    def render(self):
        self.scene = self.app.scene
        self.scene.update()
        for obj in self.scene.objects:
            obj.render()

    def destroy(self):
        return None
