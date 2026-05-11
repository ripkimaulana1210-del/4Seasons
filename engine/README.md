# Engine Folder Map

```text
core/       Runtime utama: app, camera, settings, paths, quality, light.
rendering/  OpenGL pipeline: shader, texture, VAO/VBO, shadow, postprocess, renderer, instancing.
systems/    Sistem non-render: season controller, transition manager, audio.
ui/         HUD dan scene editor.
scenes/     Scene utama.
scene_parts/Komponen penyusun map: environment, garden, village, seasonal/object details.
models/     Base model dan renderable objects.
seasons/    Dictionary konfigurasi tiap musim.
data/       Konfigurasi scene, camera preset, quality, transition preset.
geometry/   Mesh/procedural geometry generator.
```

File kecil di root `engine` seperti `app.py`, `scene.py`, `model.py`, `paths.py`,
`season_controller.py`, dan `season_transition_manager.py` hanya compatibility
facade agar import lama tetap bisa jalan.
