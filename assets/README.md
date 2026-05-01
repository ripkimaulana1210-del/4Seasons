# Assets

Project assets are grouped by type:

- `audio/`: background music and audio notes.
- `shaders/`: GLSL shader source files.
- `textures/`: PNG textures loaded by `engine.texture.TextureManager`.

Seasonal ground textures:

- `spring_grass.png`: fresh spring grass.
- `flower_meadow.png`: spring garden patches with small flowers.
- `petal_ground.png`: spring yard grass with scattered petals.
- `summer_grass.png`: deep summer grass.
- `dry_grass.png`: sun-dried summer yard.
- `autumn_grass.png`: muted autumn grass.
- `leaf_litter.png`: fallen leaves for autumn gardens.
- `snow.png`: winter ground and garden cover.

Seasonal road textures:

- `road.png`: neutral road.
- `sunbaked_road.png`: hot summer road.
- `leafy_road.png`: autumn road with leaf scatter.
- `icy_road.png`: winter road with icy streaks.

Extra material textures:

- `mossy_stone.png`: stone with moss patches.
- `bark_dark.png`: dark bark texture for future wood/tree materials.

Sky and atmosphere textures:

- `cloud_soft.png`: soft clustered cloud layer.
- `cloud_streak.png`: long thin drifting cloud layer.
- `moon_disc.png`: transparent moon sprite.
- `aurora_band.png`: transparent aurora ribbon for winter nights.

Atmosphere shaders:

- `sky_shader.vert` / `sky_shader.frag`: procedural sky gradient, dusk glow, and stars.
- `emissive_texture.vert` / `emissive_texture.frag`: transparent unlit texture sprites for clouds, moon, and aurora.

Material shaders:

- `foliage_shader.vert` / `foliage_shader.frag`: animated foliage lighting for sakura canopy, blossoms, and floating petals.
- `ice_shader.vert` / `ice_shader.frag`: crystalline winter ice overlay with cracks, fresnel glow, and night shimmer.
