# Environment Setup

## Laptop (team machine)

- HP Envy x360 16", Intel Core i7-1255U (12 threads), Intel Iris Xe graphics (**no NVIDIA / no CUDA**), 15.72 GB RAM, Windows 11 x64 (verified from the OpenMVS banner, 2026-10-25).
- Free space: C: 218 GB, D: 359 GB (2026-10-25).

## Data location (outside the repo)

```
D:\heritage3d-data\
  raw\          CHSDD_RGB.zip, CHSDD_depth.zip   (~54 GB)
  chsd\rgb\     extracted RGB                    (to verify size)
  chsd\depth\   extracted depth                  (to verify size)
  runs\         COLMAP/OpenMVS workspaces per artifact/level
```

Repository clone: `D:\heritage3d\` (code only), Python venv at `D:\heritage3d\.venv` (verified 2026-10-25).

## Tools (installed and verified on the laptop, 2026-10-25)

| Tool | Version | Location | Source |
|---|---|---|---|
| COLMAP | 4.2.1 (commit bd1fcf6, **without GPU support**) | `C:\tools\colmap\COLMAP.bat` | `colmap-x64-windows-nocuda.zip`, https://github.com/colmap/colmap/releases/tag/4.2.1 |
| OpenMVS | 2.4.0 (build Jan 20 2026) | `C:\tools\openmvs\vc17\x64\Release\` | `OpenMVS_Windows_x64.zip`, https://github.com/cdcseacave/openMVS/releases/tag/v2.4.0 |
| Python | 3.13.15 | system install, venv in repo | python.org |
| pytest | 9.1.1 | venv | PyPI |
| 7-Zip | to verify | — | https://www.7-zip.org |

Both tool folders are on the user PATH: `colmap -h` and `DensifyPointCloud --help` work from any folder.
Python 3.13 is kept: Open3D 0.20.0 ships wheels for 3.10–3.14 (checked on PyPI).

Check before each experiment session: `python scripts/check_env.py --out <run folder>\environment.json`.

Verified on the laptop 2026-10-25: `pytest tests` → 12 passed; `check_env.py` → COLMAP 4.2.1 (gpu: false), OpenMVS 2.4.0, all 5 OpenMVS tools on PATH, hardware i7-1255U / 12 logical CPUs / 15.72 GB.

## Agent

- 2026-10-25 → 2026-10-29: Claude Code **cloud** session (no GPU, limited disk, Zenodo/GitLab blocked). Wrote code and docs; the team ran laptop commands and pasted output.
- From 2026-10-29: Claude Code **locally on the laptop** in `D:\heritage3d`. The agent runs tools and experiments directly.
