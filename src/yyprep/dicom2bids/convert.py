import subprocess
from typing import Union
import pandas as pd
from pathlib import Path


def convert_dicom_to_bids(
    df: pd.DataFrame,
    heudiconv_cmd_template: Path | str,
    heuristic: Path | str,
    bids_path: Path | str,
    overwrite: bool = False,
):  # noqa: E501, UP007
    """
    Convert DICOM files to BIDS format using Heudiconv.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing DICOM file information.
    heudiconv_cmd_template : Path | str
        Template for the Heudiconv command.
    heuristic : Path | str
        Heuristic file for the conversion.
    bids_path : Path | str
        Output directory for BIDS files.
    overwrite : bool, optional
        If True, overwrite existing BIDS files, by default False
    """
    heudiconv_cmd_template = Path(heudiconv_cmd_template)
    if not heudiconv_cmd_template.exists():
        raise FileNotFoundError(f"Heudiconv command template not found: {heudiconv_cmd_template}")
    if not Path(heuristic).exists():
        raise FileNotFoundError(f"Heuristic file not found: {heuristic}")
    for _, row in df.iterrows():
        subject_code = row["subject_code"]
        dicom_path = Path(row["dicom_path"])
        session_id = row["session_id"]
        cmd = heudiconv_cmd_template.format(
            dicom_directory=dicom_path,
            subject_id=subject_code,
            session_id=session_id,
            output_directory=bids_path,
            heuristic=heuristic,
        )
        if overwrite:
            cmd += " --overwrite"
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
