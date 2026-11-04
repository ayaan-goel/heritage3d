from heritage3d.status import LEVELS, artifact_status


def rows(mesh_f=0.99, levels=LEVELS):
    return [{"level": l, "images": 92, "registered": 61, "cloud_f@0.002": 0.9, "mesh_f@0.002": mesh_f} for l in levels]


def test_exhibited_artifact_has_no_reason():
    row = artifact_status("a", 3, rows(), 0.0, {"level": "L3", "f@0.002": 0.98}, 0.95)
    assert (row["status"], row["museum"], row["museum_level"], row["reason"]) == ("Done", "Yes", "L3", "")


def test_failed_artifact_gets_measured_reason():
    row = artifact_status("a", 3, rows(mesh_f=0.5), 0.0, None, 0.95)
    assert row["museum"] == "No"
    assert "0.500 is below 0.95" in row["reason"] and "61 of 92" in row["reason"]


def test_passing_artifact_without_export_is_pending():
    assert artifact_status("a", 3, rows(), 0.0, None, 0.95)["museum"] == "Pending"


def test_partly_run_and_queued_main_set_artifacts():
    partly = artifact_status("a", 3, rows(levels=("L5", "L3")), 0.0, None, 0.95)
    assert (partly["status"], partly["museum"], partly["L1"], partly["L3"]) == ("In progress", "Pending", None, 0.9)
    assert artifact_status("a", 3, [], 0.0, None, 0.95)["status"] == "Queued"


def test_cut_off_artifact_is_not_run():
    row = artifact_status("a", None, [], 0.15, None, 0.95)
    assert (row["set"], row["status"], row["museum"]) == ("Cut off", "Not run", "No")
    assert "15%" in row["reason"]


def test_cut_off_artifact_run_at_the_museum_level():
    passed = artifact_status("a", None, rows(levels=("L3",)), 0.15, None, 0.95)
    assert (passed["set"], passed["status"], passed["museum"]) == ("Cut off", "Partly run", "Pending")
    assert "15%" in passed["reason"]
    failed = artifact_status("a", None, rows(mesh_f=0.5, levels=("L3",)), 0.15, None, 0.95)
    assert failed["museum"] == "No" and "0.500 is below 0.95" in failed["reason"]
