"""Where each CHSD artifact stands: reconstructed levels, museum decision and the reason for it."""

LEVELS = ("L1", "L2", "L3", "L4", "L5")


def artifact_status(name, rank, rows, cut_off_fraction, exhibit, min_mesh_f, museum_level="L3", tau="0.002"):
    """One row of the status table.

    rows: compare.collect() output for this artifact; rank: place in the main set, None if outside it;
    exhibit: its entry in museum/artifacts.json, or None.
    """
    by_level = {r["level"]: r for r in rows}
    shown = by_level.get(museum_level)
    mesh_f = shown[f"mesh_f@{tau}"] if shown else None
    done = len(rows) == len(LEVELS)

    if done:
        status = "Done"
    elif rows:
        status = "In progress" if rank is not None else "Partly run"
    else:
        status = "Not run" if rank is None else "Queued"

    if exhibit:
        museum, reason = "Yes", ""
    elif rank is None and not shown:
        museum = "No"
        reason = f"Outside the main set: object cut off by the frame in {cut_off_fraction:.0%} of the sample views"
    elif rank is not None and not done:
        museum, reason = "Pending", "Reconstruction not finished"
    elif mesh_f >= min_mesh_f:
        museum, reason = "Pending", "Passes the exhibit rule; export not run yet"
        if rank is None:
            reason = f"Passes the exhibit rule; cut off in {cut_off_fraction:.0%} of the sample views, team to decide"
    else:
        museum = "No"
        reason = (f"{museum_level} mesh F {mesh_f:.3f} is below {min_mesh_f}; "
                  f"{shown['registered']} of {shown['images']} photos in the model used")

    return {
        "rank": rank,
        "artifact": name,
        "set": "Cut off" if rank is None else "Main",
        "status": status,
        **{level: by_level[level][f"cloud_f@{tau}"] if level in by_level else None for level in LEVELS},
        "registered": shown["registered"] if shown else None,
        "mesh_f": mesh_f,
        "museum": museum,
        "museum_level": exhibit["level"] if exhibit else None,
        "museum_f": exhibit[f"f@{tau}"] if exhibit else None,
        "reason": reason,
    }
