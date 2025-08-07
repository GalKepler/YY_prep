import typer
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for

app = typer.Typer(
    help="Convert DICOM directories to BIDS format and update IntendedFor fields for fMRIPrep."
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


def main():
    app()


if __name__ == "__main__":
    main()
