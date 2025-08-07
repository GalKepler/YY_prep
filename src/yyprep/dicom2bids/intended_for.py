import json
from pathlib import Path

import pandas as pd
from bids.layout import BIDSLayout


def update_intended_for(df: pd.DataFrame, bids_path: Path | str):
    """
    Update the 'IntendedFor' field in BIDS fmap JSON files based on the provided DataFrame.

    Parameters
    ----------
    bids_path : Path | str
        Path to the BIDS dataset.
    df : pd.DataFrame
        DataFrame containing the mapping information.
    """
    layout = BIDSLayout(bids_path, validate=True)

    for _, row in df.iterrows():
        subject = row["subject_code"]
        session = row.get("session_id", None)

        fmaps = layout.get(
            subject=subject, session=session, datatype="fmap", extension="json"
        )
        funcs_to_include = layout.get(
            subject=subject, session=session, datatype="func", extension="nii.gz"
        )
        funcs_to_include = [
            f.path.replace(str(bids_path) + "/", "") for f in funcs_to_include
        ]
        funcs_addition = [f"bids::{addition}" for addition in funcs_to_include]

        for fmap in fmaps:
            fmap_json = fmap.path
            with open(fmap_json) as f:
                data = json.load(f)
            fmap_intended_for = data.get("IntendedFor", [])
            fmap_intended_for = list(set(fmap_intended_for + funcs_addition))
            data["IntendedFor"] = fmap_intended_for
            with open(fmap_json, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Updated {fmap_json} with IntendedFor: {fmap_intended_for}")
