# Tools

Utility scripts are grouped by purpose:

- `assets/`: texture generation and PNG optimization.
- `audio/`: seasonal audio placeholders and manifests.
- `previews/`: scene preview, denah sector, and gallery generation.
- `validation/`: asset, shader, season, and audio reference checks.

Run scripts from the project root, for example:

```powershell
python tools\validation\validate_assets.py
python tools\previews\generate_season_previews.py
python tools\previews\generate_sector_previews.py --prefix scene_map
```
