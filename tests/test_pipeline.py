import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import load_config
from heritage3d.pipeline import dense_commands, parse_model_analyzer, run_stage, sparse_commands

ANALYZER = """I20261030 10:00:00.000000 1 model.cc:1] Cameras: 1
I20261030 10:00:00.000000 1 model.cc:1] Images: 92
I20261030 10:00:00.000000 1 model.cc:1] Registered images: 90
I20261030 10:00:00.000000 1 model.cc:1] Points: 12345
I20261030 10:00:00.000000 1 model.cc:1] Observations: 67890
I20261030 10:00:00.000000 1 model.cc:1] Mean track length: 5.499
I20261030 10:00:00.000000 1 model.cc:1] Mean observations per image: 754.3
I20261030 10:00:00.000000 1 model.cc:1] Mean reprojection error: 0.512px
"""


def test_parse_model_analyzer():
    stats = parse_model_analyzer(ANALYZER)
    assert stats["cameras"] == 1 and stats["images"] == 92 and stats["registered_images"] == 90
    assert stats["points"] == 12345 and stats["mean_reprojection_error_px"] == 0.512
    assert stats["mean_track_length"] == 5.499 and stats["mean_observations_per_image"] == 754.3


def test_commands_use_cpu_and_config_settings(tmp_path):
    settings = load_config()["pipeline"]
    sparse = dict(sparse_commands("colmap", tmp_path, Path("rgb"), tmp_path / "images.txt", settings))
    extractor = [str(x) for x in sparse["feature_extractor"]]
    assert extractor[extractor.index("--FeatureExtraction.use_gpu") + 1] == "0"
    assert extractor[extractor.index("--ImageReader.camera_model") + 1] == settings["camera_model"]
    matcher = [str(x) for x in sparse[settings["matcher"]]]
    assert matcher[matcher.index("--FeatureMatching.use_gpu") + 1] == "0"
    names = [n for n, _ in dense_commands("colmap", tmp_path, Path("rgb"), tmp_path / "sparse" / "0", settings)]
    assert names == ["image_undistorter", "InterfaceCOLMAP", "DensifyPointCloud", "ReconstructMesh", "TextureMesh"]


def test_run_stage_records_time_memory_and_log(tmp_path):
    code = "x = bytearray(50 * 1024 * 1024); print('done')"
    result = run_stage("probe", [sys.executable, "-c", code], tmp_path / "logs" / "probe.log")
    assert result["returncode"] == 0 and result["seconds"] >= 0
    assert "done" in (tmp_path / "logs" / "probe.log").read_text(encoding="utf-8")
    if sys.platform == "win32":
        assert result["peak_memory_mb"] >= 50


def test_run_stage_reports_failure(tmp_path):
    result = run_stage("fail", [sys.executable, "-c", "raise SystemExit(3)"], tmp_path / "fail.log")
    assert result["returncode"] == 3
