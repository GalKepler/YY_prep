"""
Simplified nipype-like interface for fMRIPrep using fmriprep-docker.

This module provides a nipype-compatible interface for running fMRIPrep
by leveraging the existing fmriprep-docker package.
"""

import subprocess
from pathlib import Path

from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    File,
    TraitedSpec,
    isdefined,
    traits,
)


class FMRIPrepInputSpec(BaseInterfaceInputSpec):
    """Input specification for FMRIPrep interface."""

    # Required inputs
    bids_dir = File(
        exists=True,
        mandatory=True,
        desc="Root directory of BIDS dataset",
    )

    output_dir = traits.Str(
        mandatory=True,
        desc="Output directory for fMRIPrep derivatives",
    )

    # Optional inputs
    participant_label = traits.List(
        traits.Str(),
        desc="List of participant identifiers to process",
    )

    session_id = traits.List(
        traits.Str(),
        desc="Select specific sessions to be processed",
    )

    task_id = traits.List(
        traits.Str(),
        desc="Select specific tasks to be processed",
    )

    # Common fMRIPrep options
    output_spaces = traits.List(
        traits.Str(),
        desc="Standard and non-standard spaces to resample images to",
    )

    skip_bids_validation = traits.Bool(
        False,
        usedefault=True,
        desc="Skip BIDS validation",
    )

    fs_license_file = File(
        exists=True,
        desc="Path to FreeSurfer license file",
    )

    work_dir = traits.Str(
        desc="Working directory for fMRIPrep",
    )

    n_cpus = traits.Int(
        desc="Number of CPUs to use",
    )

    omp_nthreads = traits.Int(
        desc="Maximum number of threads per process",
    )

    mem_gb = traits.Float(
        desc="Upper bound memory limit for fMRIPrep processes in GB",
    )

    low_mem = traits.Bool(
        False,
        usedefault=True,
        desc="Attempt to reduce memory usage",
    )

    bids_filter_file = File(
        exists=True,
        desc="Path to BIDS filter file for selecting specific data",
    )

    # fmriprep-docker specific options
    docker_version = traits.Str(
        "latest",
        usedefault=True,
        desc="fMRIPrep Docker image version",
    )

    verbose = traits.Bool(
        False,
        usedefault=True,
        desc="Enable verbose output",
    )


class FMRIPrepOutputSpec(TraitedSpec):
    """Output specification for FMRIPrep interface."""

    output_dir = traits.Str(
        desc="Output directory containing fMRIPrep derivatives",
    )

    work_dir = traits.Str(
        desc="Working directory used by fMRIPrep",
    )


class FMRIPrepInterface(BaseInterface):
    """
    Simplified nipype interface for fMRIPrep using fmriprep-docker.

    This interface wraps the fmriprep-docker command-line tool to provide
    a nipype-compatible interface for running fMRIPrep.

    Examples
    --------
    >>> from yyprep.fmriprep import FMRIPrepInterface
    >>> fmriprep = FMRIPrepInterface()
    >>> fmriprep.inputs.bids_dir = '/path/to/bids'
    >>> fmriprep.inputs.output_dir = '/path/to/output'
    >>> fmriprep.inputs.participant_label = ['001', '002']
    >>> result = fmriprep.run()
    """

    input_spec = FMRIPrepInputSpec
    output_spec = FMRIPrepOutputSpec

    def __init__(self, **kwargs):
        """Initialize the interface."""
        super().__init__(**kwargs)
        self._check_fmriprep_docker()

    def _check_fmriprep_docker(self):
        """Check if fmriprep-docker is available."""
        try:
            subprocess.run(
                ["fmriprep-docker", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise RuntimeError(
                "fmriprep-docker is not available. Please install it with: "
                "pip install fmriprep-docker"
            ) from exc

    def _format_command(self) -> list[str]:
        """Format the fmriprep-docker command."""
        cmd = ["fmriprep-docker"]

        # Add required arguments
        cmd.extend(
            [str(self.inputs.bids_dir), str(self.inputs.output_dir), "participant"]
        )

        # Add participant labels
        if isdefined(self.inputs.participant_label):
            for participant in self.inputs.participant_label:
                cmd.extend(["--participant-label", participant])

        # Add session IDs
        if isdefined(self.inputs.session_id):
            for session in self.inputs.session_id:
                cmd.extend(["--session-id", session])

        # Add task IDs
        if isdefined(self.inputs.task_id):
            for task in self.inputs.task_id:
                cmd.extend(["--task-id", task])

        # Add output spaces
        if isdefined(self.inputs.output_spaces):
            cmd.extend(["--output-spaces"] + self.inputs.output_spaces)

        # Skip BIDS validation
        if self.inputs.skip_bids_validation:
            cmd.append("--skip_bids_validation")

        # Add FreeSurfer license
        if isdefined(self.inputs.fs_license_file):
            cmd.extend(["--fs-license-file", str(self.inputs.fs_license_file)])

        # Add work directory
        if isdefined(self.inputs.work_dir):
            cmd.extend(["--work-dir", str(self.inputs.work_dir)])

        # Add performance options
        if isdefined(self.inputs.n_cpus):
            cmd.extend(["--n_cpus", str(self.inputs.n_cpus)])

        if isdefined(self.inputs.omp_nthreads):
            cmd.extend(["--omp-nthreads", str(self.inputs.omp_nthreads)])

        if isdefined(self.inputs.mem_gb):
            cmd.extend(["--mem_gb", str(self.inputs.mem_gb)])

        if self.inputs.low_mem:
            cmd.append("--low-mem")

        # Add BIDS filter file
        if isdefined(self.inputs.bids_filter_file):
            cmd.extend(["--bids-filter-file", str(self.inputs.bids_filter_file)])

        # Add Docker version
        if (
            isdefined(self.inputs.docker_version)
            and self.inputs.docker_version != "latest"
        ):
            cmd.extend(
                ["--docker-image", f"nipreps/fmriprep:{self.inputs.docker_version}"]
            )

        # Add verbose flag
        if self.inputs.verbose:
            cmd.append("--verbose")

        return cmd

    def _run_interface(self, runtime):
        """Run the fmriprep-docker command."""
        # Create output directory if it doesn't exist
        Path(self.inputs.output_dir).mkdir(parents=True, exist_ok=True)

        # Create work directory if specified
        if isdefined(self.inputs.work_dir):
            Path(self.inputs.work_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._format_command()

        # Log the command
        runtime.cmdline = " ".join(cmd)

        # Run the command
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(Path.cwd())
        )

        runtime.returncode = result.returncode
        runtime.stdout = result.stdout
        runtime.stderr = result.stderr

        if result.returncode != 0:
            raise RuntimeError(
                f"fMRIPrep failed with return code {result.returncode}\n"
                f"Command: {runtime.cmdline}\n"
                f"Stdout: {result.stdout}\n"
                f"Stderr: {result.stderr}"
            )

        return runtime

    def _list_outputs(self):
        """List expected outputs."""
        outputs = self._outputs().get()

        if isdefined(self.inputs.output_dir):
            outputs["output_dir"] = str(self.inputs.output_dir)

        if isdefined(self.inputs.work_dir):
            outputs["work_dir"] = str(self.inputs.work_dir)

        return outputs


def create_fmriprep_workflow(
    bids_dir: str | Path,
    output_dir: str | Path,
    participant_label: list[str] | None = None,
    work_dir: str | Path | None = None,
    **kwargs,
) -> FMRIPrepInterface:
    """
    Create a pre-configured fMRIPrep interface.

    Parameters
    ----------
    bids_dir : str or Path
        Path to BIDS dataset directory
    output_dir : str or Path
        Path to output directory
    participant_label : list of str, optional
        List of participant labels to process
    work_dir : str or Path, optional
        Working directory for temporary files
    **kwargs
        Additional arguments to pass to FMRIPrepInterface

    Returns
    -------
    FMRIPrepInterface
        Configured fMRIPrep interface

    Examples
    --------
    >>> workflow = create_fmriprep_workflow(
    ...     bids_dir="/path/to/bids",
    ...     output_dir="/path/to/output",
    ...     participant_label=["001", "002"],
    ...     output_spaces=["MNI152NLin2009cAsym:res-2"]
    ... )
    >>> result = workflow.run()
    """
    interface = FMRIPrepInterface()

    # Set required inputs
    interface.inputs.bids_dir = str(bids_dir)
    interface.inputs.output_dir = str(output_dir)

    # Set optional inputs
    if participant_label is not None:
        interface.inputs.participant_label = participant_label

    if work_dir is not None:
        interface.inputs.work_dir = str(work_dir)

    # Set additional kwargs
    for key, value in kwargs.items():
        if hasattr(interface.inputs, key):
            setattr(interface.inputs, key, value)
        else:
            raise ValueError(f"Unknown input parameter: {key}")

    return interface
