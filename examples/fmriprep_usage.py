"""
Example usage of the yyprep fMRIPrep interface.

This module demonstrates how to use the nipype-like interface for fMRIPrep
both programmatically and through the CLI.
"""

from pathlib import Path
import pandas as pd
from yyprep.fmriprep.interface import create_fmriprep_workflow, FMRIPrepInterface


def example_programmatic_usage():
    """Example of using the fMRIPrep interface programmatically."""

    # Define paths
    bids_dir = "/path/to/bids"
    output_dir = "/path/to/output"
    work_dir = "/path/to/work"

    # Example 1: Simple usage with create_fmriprep_workflow
    print("Example 1: Using create_fmriprep_workflow")

    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=output_dir,
        participant_label=["001", "002"],
        output_spaces=["MNI152NLin2009cAsym:res-2", "fsaverage:den-10k"],
        work_dir=work_dir,
        n_cpus=4,
        mem_mb=8000,
        skip_bids_validation=True,
    )

    # Run the workflow (commented out for example)
    # result = workflow.run()
    # print(f"Output directory: {result.outputs.output_dir}")

    # Example 2: Manual interface configuration
    print("\nExample 2: Manual interface configuration")

    interface = FMRIPrepInterface()

    # Set required inputs
    interface.inputs.bids_dir = bids_dir
    interface.inputs.output_dir = output_dir
    interface.inputs.analysis_level = "participant"

    # Set optional inputs
    interface.inputs.participant_label = ["001", "002"]
    interface.inputs.output_spaces = ["MNI152NLin2009cAsym:res-2"]
    interface.inputs.work_dir = work_dir
    interface.inputs.n_cpus = 4
    interface.inputs.mem_mb = 8000
    interface.inputs.skip_bids_validation = True
    interface.inputs.docker_image = "nipreps/fmriprep:23.2.1"

    # Run the interface (commented out for example)
    # result = interface.run()
    # print(f"Command executed: {result.runtime.cmdline}")


def example_with_csv_participants():
    """Example using participants from CSV (similar to dicom2bids workflow)."""

    # Load participants data
    participants_df = pd.DataFrame(
        {
            "subject_code": ["001", "002", "003"],
            "session_id": ["01", "01", "02"],
            "dicom_path": [
                "/data/dicoms/sub001_ses01",
                "/data/dicoms/sub002_ses01",
                "/data/dicoms/sub003_ses02",
            ],
        }
    )

    # Extract unique participant labels
    participant_labels = participants_df["subject_code"].unique().tolist()

    # Create workflow
    workflow = create_fmriprep_workflow(
        bids_dir="/path/to/bids",
        output_dir="/path/to/fmriprep_output",
        participant_label=participant_labels,
        output_spaces=["MNI152NLin2009cAsym:res-2"],
        work_dir="/path/to/work",
        fs_license_file="/path/to/license.txt",
    )

    print(f"Processing participants: {participant_labels}")
    # result = workflow.run()


def example_cli_commands():
    """Example CLI commands for reference."""

    print("Example CLI commands:")
    print()

    print("1. Basic fMRIPrep run:")
    print("yyprep fmriprep /path/to/bids /path/to/output \\")
    print("  --participant-label 001 002 \\")
    print("  --output-spaces MNI152NLin2009cAsym:res-2")
    print()

    print("2. Full pipeline (DICOM → BIDS → fMRIPrep):")
    print("# First, convert DICOM to BIDS")
    print("yyprep dicom2bids participants.csv \\")
    print("  --bids-dir /path/to/bids \\")
    print("  --heuristic /path/to/heuristic.py")
    print()
    print("# Then run fMRIPrep")
    print("yyprep fmriprep /path/to/bids /path/to/output \\")
    print("  --participant-label 001 002 \\")
    print("  --output-spaces MNI152NLin2009cAsym:res-2 \\")
    print("  --fs-license-file /path/to/license.txt \\")
    print("  --n-cpus 4 \\")
    print("  --mem-mb 8000")
    print()

    print("3. With additional options:")
    print("yyprep fmriprep /path/to/bids /path/to/output \\")
    print("  --participant-label 001 \\")
    print("  --session-id 01 02 \\")
    print("  --task-id rest \\")
    print("  --output-spaces MNI152NLin2009cAsym:res-2 fsaverage:den-10k \\")
    print("  --work-dir /path/to/work \\")
    print("  --skip-bids-validation \\")
    print("  --low-mem \\")
    print("  --docker-image nipreps/fmriprep:23.2.1")


if __name__ == "__main__":
    print("YYPrep fMRIPrep Interface Examples")
    print("=" * 40)

    example_programmatic_usage()
    print("\n" + "=" * 40)

    example_with_csv_participants()
    print("\n" + "=" * 40)

    example_cli_commands()
