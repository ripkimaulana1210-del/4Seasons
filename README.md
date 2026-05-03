# OpenGL Basic 3D - Seasonal Sakura Scene

Project grafika komputer berbasis Python, Pygame, dan ModernGL. Scene menampilkan taman sakura 3D dengan empat musim, siklus siang-malam, cuaca, audio, HUD, camera preset, dan efek transisi antar musim.

## Fitur Utama

- Empat musim: semi, panas, gugur, dingin.
- Transisi visual antar musim dengan perubahan suhu, warna, cuaca, dan atmosfer.
- Siklus siang-malam dengan matahari, bulan, bintang, awan, rainbow spring, milky way summer, cloud mood autumn, dan aurora musim dingin.
- Scene taman Jepang: pohon sakura, kolam, jembatan, desa kecil, taman, lentera, dan Gunung Fuji.
- Object scene tambahan: torii, shrine mini, koi, lily pad, stream dan waterfall kecil, stepping stones, perahu kecil, bamboo, pohon musiman, foreground plants, detail rumah, shrine offering, lampion jembatan, dan prop musiman.
- HUD in-game untuk musim, waktu, suhu, FPS, kamera, screenshot, audio, dan statistik culling.
- Camera preset, cinematic tour, orbit camera, fullscreen, dan screenshot export.
- Profiling overlay, adaptive quality, quality setting tersimpan, pause menu, fog musiman, contact shadow, shadow mapping sederhana, post-processing bloom/tone polish, scene editor mini, distance culling, particle musiman, water shader musiman, ambience procedural per musim, camera preset musiman, cinematic route per musim, dan instanced rendering untuk objek warna statis.

## Instalasi

Gunakan Python 3.11 atau versi yang kompatibel dengan dependency di `requirements.txt`.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan

```powershell
python main.py
```

Alternatif cepat di Windows:

```powershell
scripts\windows\setup.bat
scripts\windows\run.bat
```

## Kontrol

| Tombol | Fungsi |
| --- | --- |
| `W A S D` | Gerak kamera |
| `Q / E` | Turun / naik kamera |
| `Mouse` | Arah pandang |
| `Shift` | Gerak lebih cepat |
| `Ctrl` | Gerak lebih pelan |
| `Tab` | Toggle free camera / orbit camera |
| `Mouse wheel` | Zoom orbit camera |
| `1-4` | Pilih musim |
| `N / P` | Musim berikutnya / sebelumnya |
| `T` | Toggle time-lapse musim |
| `Y` | Toggle siklus hari |
| `L / O` | Set malam / pagi |
| `+ / -` | Ubah kecepatan time-lapse |
| `M` | Mute / unmute audio |
| `` ` `` | Toggle mouse grab |
| `F1` | Camera preset terbaik untuk musim aktif |
| `F2` | Simpan screenshot ke `docs/previews/` |
| `F3` | Toggle scene editor mini |
| `F4` | Toggle shadow mapping; saat editor aktif: dump transform object |
| `F5` | Camera preset sakura |
| `F6` | Camera preset jembatan |
| `F7` | Camera preset desa |
| `F8` | Camera preset Fuji |
| `F9` | Ganti quality `Low / Medium / High` |
| `F10` | Toggle profiling overlay |
| `C` | Toggle cinematic tour |
| `F11` | Toggle fullscreen |
| `F12` | Toggle post-processing |
| `Esc` | Pause / resume |
| `Q` | Keluar saat pause menu terbuka |

Scene editor mini aktif setelah `F3`:

| Tombol | Fungsi editor |
| --- | --- |
| `[ / ]` | Pilih object sebelumnya / berikutnya |
| `Arrow keys` | Geser object di sumbu X/Z |
| `PageUp / PageDown` | Geser object naik / turun |
| `F4` | Print transform object terpilih ke console |

## Struktur Project

```text
assets/
  audio/       Musik dan catatan audio.
  shaders/     GLSL shader.
  textures/    Texture PNG.
docs/
  previews/    Preview render dan output screenshot.
config/
  settings.json  Dibuat otomatis saat setting diubah.
engine/
  scene.py           Scene utama.
  scene_parts/       Bagian scene: environment, garden, village.
  model.py           Base model dan model renderable.
  season_controller.py
  scene_renderer.py
  shadow.py
  postprocess.py
  camera.py
  hud.py
  editor.py
  instancing.py
  quality.py
  settings.py
tools/
  validate_assets.py
  generate_textures.py
  optimize_textures.py
scripts/
  windows/      Helper setup, run, dan build Windows.
main.py
requirements.txt
```

## Validasi

```powershell
python -m compileall -q main.py engine tools
python tools\validate_assets.py
```

`tools/validate_assets.py` mengecek texture, shader, season config, dan referensi audio agar asset tidak putus.

Generate preview gallery empat musim:

```powershell
python tools\generate_season_previews.py
```
