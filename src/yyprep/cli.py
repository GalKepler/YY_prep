from pathlib import Path

import pandas as pd
import typer

from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for
from yyprep.fmriprep.interface import create_fmriprep_workflow

app = typer.Typer(
    help="Convert DICOM directories to BIDS format and preprocess with fMRIPrep."
)


@app.command()
def dicom2bids(
    participants_csv: str = typer.Argument(
        ..., help="CSV file with subject/session/DICOM info"
    ),
    bids_dir: str = typer.Option(
        ..., "--bids-dir", help="Root output directory for BIDS dataset"
    ),
    heuristic: str = typer.Option(
        ..., "--heuristic", help="Path to heuristic Python file for heudiconv"
    ),
    heudiconv_template: str = typer.Option(
        "heudiconv -d '{dicom_directory}' -s {subject_id} -ss {session_id} "
        "-o {output_directory} -f {heuristic} -c dcm2niix",
        help="Template for heudiconv command.",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Pass --overwrite to heudiconv."
    ),
    skip_intendedfor: bool = typer.Option(
        False, "--skip-intendedfor", help="Skip updating IntendedFor fields."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print commands but do not run conversion."
    ),
):
    """
    Converts DICOMs to BIDS and updates fieldmaps for fMRIPrep.
    """
    df = pd.read_csv(participants_csv)

    if dry_run:
        typer.echo(
            "Dry run: would perform dicom2bids conversion and fmap IntendedFor updates."
        )
        return

    typer.echo("Running dicom2bids conversion...")
    convert_dicom_to_bids(
        df=df,
        heudiconv_cmd_template=heudiconv_template,
        overwrite=overwrite,
        heuristic=heuristic,
        bids_path=bids_dir,
    )
    if not skip_intendedfor:
        typer.echo("Updating IntendedFor fields...")
        update_intended_for(bids_dir, df)


@app.command()
def fmriprep(
    bids_dir: str = typer.Argument(..., help="Path to BIDS dataset directory"),
    output_dir: str = typer.Argument(..., help="Path to output directory"),
    participant_label: list[str] | None = None,
    session_id: list[str] | None = None,
    task_id: list[str] | None = None,
    output_spaces: list[str] | None = None,
    fs_license_file: str | None = None,
    work_dir: str | None = None,
    n_cpus: int | None = None,
    omp_nthreads: int | None = None,
    mem_gb: float | None = None,
    bids_filter_file: str | None = None,
    skip_bids_validation: bool = False,
    low_mem: bool = False,
    docker_image: str = "nipreps/fmriprep:latest",
    dry_run: bool = False,
):
    participant_label = typer.Option(
        None, "--participant-label", help="List of participant labels to process"
    )
    session_id = typer.Option(
        None, "--session-id", help="List of session IDs to process"
    )
    task_id = typer.Option(None, "--task-id", help="List of task IDs to process")
    output_spaces = typer.Option(
        None, "--output-spaces", help="Output spaces for resampling"
    )
    fs_license_file = typer.Option(
        None, "--fs-license-file", help="Path to FreeSurfer license file"
    )
    work_dir = typer.Option(
        None, "--work-dir", help="Working directory for temporary files"
    )
    n_cpus = typer.Option(None, "--n-cpus", help="Number of CPUs to use")
    omp_nthreads = typer.Option(
        None, "--omp-nthreads", help="Maximum number of threads per process"
    )
    mem_gb = typer.Option(None, "--mem-gb", help="Memory limit in GB")
    bids_filter_file = typer.Option(
        None, "--bids-filter-file", help="Path to BIDS filter file"
    )
    skip_bids_validation = typer.Option(
        False, "--skip-bids-validation", help="Skip BIDS validation"
    )
    low_mem = typer.Option(False, "--low-mem", help="Attempt to reduce memory usage")
    docker_image = typer.Option(
        "nipreps/fmriprep:latest", "--docker-image", help="Docker image to use"
    )
    dry_run = typer.Option(
        False, "--dry-run", help="Print command but do not run fMRIPrep"
    )
    """
    Run fMRIPrep preprocessing on BIDS dataset using Docker.
    """
    if dry_run:
        typer.echo("Dry run: would run fMRIPrep preprocessing.")
        return

    # Set default output spaces if not provided
    if output_spaces is None:
        output_spaces = ["MNI152NLin2009cAsym:res-2"]

    # Create work directory if specified
    if work_dir:
        Path(work_dir).mkdir(parents=True, exist_ok=True)

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    typer.echo(f"Running fMRIPrep on {bids_dir}...")

    # Create fMRIPrep workflow
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=output_dir,
        participant_label=participant_label,
        session_id=session_id,
        task_id=task_id,
        output_spaces=output_spaces,
        fs_license_file=fs_license_file,
        work_dir=work_dir,
        n_cpus=n_cpus,
        omp_nthreads=omp_nthreads,
        mem_gb=mem_gb,
        bids_filter_file=bids_filter_file,
        skip_bids_validation=skip_bids_validation,
        low_mem=low_mem,
        docker_image=docker_image,
    )

    try:
        result = workflow.run()
        typer.echo("fMRIPrep completed successfully!")
        if hasattr(result.outputs, "html_report") and result.outputs.html_report:
            typer.echo(f"HTML report: {result.outputs.html_report}")
    except Exception as e:
        typer.echo(f"fMRIPrep failed: {e}", err=True)
        raise typer.Exit(1) from e


def main():
    app()


if __name__ == "__main__":
    main()
