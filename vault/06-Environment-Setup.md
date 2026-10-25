# Environment Setup

## Laptop (team machine)

- HP Envy x360 16", Intel Iris Xe graphics (**no NVIDIA / no CUDA**), 16 GB RAM, Windows (version to verify).
- Free space: C: 218 GB, D: 359 GB (2026-10-25).

## Data location (outside the repo)

```
D:\heritage3d-data\
  raw\          CHSDD_RGB.zip, CHSDD_depth.zip   (~54 GB)
  chsd\rgb\     extracted RGB                    (to verify size)
  chsd\depth\   extracted depth                  (to verify size)
  runs\         COLMAP/OpenMVS workspaces per artifact/level
```

Repository clone: `D:\heritage3d\` (code only).

## Tools (install status: not yet installed)

| Tool | Build | Source |
|---|---|---|
| COLMAP | Windows **no-CUDA** | https://github.com/colmap/colmap/releases |
| OpenMVS | Windows x64 | https://github.com/cdcseacave/openMVS/releases |
| 7-Zip | — | https://www.7-zip.org |
| Python | 3.11 or 3.12 | https://www.python.org |

Record installed versions here once installed.

## Cloud agent session

4 CPUs, 15 GB RAM, ~30 GB free disk, no GPU, ephemeral; zenodo.org and gitlab.com blocked by network policy. Used for code, docs, tests and the museum — not for full experiments.
