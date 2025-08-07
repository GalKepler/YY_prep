# Command Line Interface (CLI) Reference

This page provides a complete reference for yyprep's command-line interface.

## Overview

yyprep provides two main commands:

- `yyprep dicom2bids`: Convert DICOM files to BIDS format
- `yyprep fmriprep`: Preprocess BIDS data with fMRIPrep

## Global Options

```bash
yyprep --help                 # Show help
yyprep --version              # Show version information
```

## dicom2bids Command

Convert DICOM files to BIDS format using HeuDiConv.

### Syntax

```bash
yyprep dicom2bids PARTICIPANTS_CSV [OPTIONS]
```

### Arguments

**PARTICIPANTS_CSV** (required)
: Path to CSV file containing participant information with columns:
  - `subject_id`: Subject identifier (without 'sub-' prefix)
  - `session_id`: Session identifier (without 'ses-' prefix)
  - `dicom_directory`: Path to DICOM files

### Options

**--bids-dir PATH** (required)
: Root output directory for BIDS dataset

**--heuristic PATH** (required)
: Path to heuristic Python file for HeuDiConv

**--heudiconv-template TEXT**
: Template for HeuDiConv command
: Default: `"heudiconv -d '{dicom_directory}' -s {subject_id} -ss {session_id} -o {output_directory} -f {heuristic} -c dcm2niix"`

**--overwrite / --no-overwrite**
: Pass --overwrite flag to HeuDiConv
: Default: False

**--skip-intendedfor / --no-skip-intendedfor**
: Skip updating fieldmap IntendedFor fields
: Default: False

**--dry-run / --no-dry-run**
: Print commands but do not execute conversion
: Default: False

### Examples

#### Basic Usage

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /data/bids \
    --heuristic heuristic.py
```

#### Custom HeuDiConv Template

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /data/bids \
    --heuristic heuristic.py \
    --heudiconv-template "heudiconv -d '{dicom_directory}' -s {subject_id} -ss {session_id} -o {output_directory} -f {heuristic} -c dcm2niix --bids"
```

#### Dry Run

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /data/bids \
    --heuristic heuristic.py \
    --dry-run
```

#### Skip IntendedFor Updates

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /data/bids \
    --heuristic heuristic.py \
    --skip-intendedfor
```

## fmriprep Command

Run fMRIPrep preprocessing on BIDS datasets.

### Syntax

```bash
yyprep fmriprep BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL [OPTIONS]
```

### Arguments

**BIDS_DIR** (required)
: Path to BIDS dataset directory

**OUTPUT_DIR** (required)
: Path to output directory for fMRIPrep derivatives

**ANALYSIS_LEVEL** (required)
: Level of analysis to perform. Choices: `participant`, `group`

### Participant Selection

**--participant-label TEXT [TEXT ...]**
: Space-separated list of participant identifiers (without 'sub-' prefix)
: Example: `--participant-label 001 002 003`

**--session-id TEXT [TEXT ...]**
: Space-separated list of session identifiers (without 'ses-' prefix)
: Example: `--session-id baseline followup`

**--task-id TEXT [TEXT ...]**
: Space-separated list of task identifiers
: Example: `--task-id rest nback stroop`

### Output Configuration

**--output-spaces TEXT [TEXT ...]**
: Space-separated list of output spaces
: Examples:
  - `--output-spaces MNI152NLin2009cAsym`
  - `--output-spaces MNI152NLin2009cAsym:res-2 T1w fsnative`

**--output-layout TEXT**
: Organization of outputs. Choices: `bids`, `legacy`
: Default: `bids`

### Resource Management

**--work-dir PATH**
: Working directory for intermediate files
: Default: System temporary directory

**--mem-mb INTEGER**
: Maximum memory usage in MB
: Example: `--mem-mb 16000` (16GB)

**--omp-nthreads INTEGER**
: Number of OpenMP threads
: Example: `--omp-nthreads 8`

**--n-cpus INTEGER**
: Total number of CPU cores to use
: Example: `--n-cpus 12`

**--low-mem / --no-low-mem**
: Enable low-memory mode
: Default: False

### FreeSurfer Options

**--fs-license-file PATH** (required)
: Path to FreeSurfer license file

**--fs-subjects-dir PATH**
: Path to existing FreeSurfer subjects directory

**--fs-no-reconall / --no-fs-no-reconall**
: Skip FreeSurfer surface reconstruction
: Default: False

### Processing Options

**--skull-strip-template TEXT**
: Template for skull stripping
: Choices: `OASIS30ANTs`, `NKI`
: Default: `OASIS30ANTs`

**--skull-strip-fixed-seed / --no-skull-strip-fixed-seed**
: Use fixed seed for skull stripping
: Default: False

**--use-aroma / --no-use-aroma**
: Enable ICA-AROMA denoising
: Default: False

**--use-syn-sdc / --no-use-syn-sdc**
: Use SyN-based susceptibility distortion correction
: Default: False

**--force-syn / --no-force-syn**
: Force SyN-based distortion correction
: Default: False

**--force-bbr / --no-force-bbr**
: Force boundary-based registration
: Default: False

### Fieldmap Options

**--ignore TEXT [TEXT ...]**
: Ignore specific data types
: Example: `--ignore fieldmaps`

**--fmap-bspline / --no-fmap-bspline**
: Use B-spline interpolation for fieldmaps
: Default: False

**--fmap-no-demean / --no-fmap-no-demean**
: Skip demeaning fieldmaps
: Default: False

### Advanced Options

**--bids-filter-file PATH**
: Path to JSON file for custom BIDS dataset filtering
: Example: `--bids-filter-file filter.json`

**--dummy-scans INTEGER**
: Number of dummy scans to remove
: Example: `--dummy-scans 5`

**--random-seed INTEGER**
: Random seed for reproducible results
: Example: `--random-seed 12345`

**--md-only-boilerplate / --no-md-only-boilerplate**
: Only generate markdown boilerplate
: Default: False

### Debugging Options

**--write-graph / --no-write-graph**
: Write workflow graph
: Default: False

**--stop-on-first-crash / --no-stop-on-first-crash**
: Stop workflow on first crash
: Default: False

**--verbose-count INTEGER**
: Verbosity level (0-3)
: Default: 0

### Examples

#### Basic fMRIPrep Run

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 \
    --fs-license-file /opt/freesurfer/license.txt
```

#### Complete Preprocessing Pipeline

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 003 \
    --output-spaces MNI152NLin2009cAsym:res-2 T1w fsnative \
    --fs-license-file /opt/freesurfer/license.txt \
    --work-dir /scratch/fmriprep_work \
    --mem-mb 32000 \
    --omp-nthreads 16 \
    --n-cpus 24 \
    --use-aroma \
    --skull-strip-template OASIS30ANTs \
    --output-layout bids \
    --write-graph \
    --verbose-count 1
```

#### Session-Specific Processing

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 \
    --session-id baseline followup \
    --task-id rest nback \
    --fs-license-file /opt/freesurfer/license.txt
```

#### Low-Memory Processing

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 \
    --fs-license-file /opt/freesurfer/license.txt \
    --low-mem \
    --mem-mb 8000 \
    --omp-nthreads 4 \
    --n-cpus 4
```

#### Custom BIDS Filtering

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 \
    --bids-filter-file custom_filter.json \
    --fs-license-file /opt/freesurfer/license.txt
```

#### Debugging Mode

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 \
    --fs-license-file /opt/freesurfer/license.txt \
    --work-dir /persistent/work \
    --write-graph \
    --stop-on-first-crash \
    --verbose-count 2
```

## Configuration Files

### BIDS Filter File Format

Create a JSON file to filter BIDS datasets:

```json
{
    "bold": {
        "task": ["rest", "nback"],
        "run": [1, 2],
        "session": ["baseline"]
    },
    "t1w": {
        "acquisition": null
    },
    "fmap": {
        "suffix": ["phasediff", "magnitude1"]
    }
}
```

### HeuDiConv Template Variables

Available variables for `--heudiconv-template`:

- `{dicom_directory}`: Path to DICOM files
- `{subject_id}`: Subject identifier
- `{session_id}`: Session identifier  
- `{output_directory}`: BIDS output directory
- `{heuristic}`: Path to heuristic file

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `130`: Interrupted by user (Ctrl+C)

## Environment Variables

**HEUDICONV_LOG_LEVEL**
: Set HeuDiConv logging level
: Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`

**DOCKER_HOST**
: Docker daemon connection string

**FREESURFER_LICENSE**
: Path to FreeSurfer license (alternative to `--fs-license-file`)

## Examples by Use Case

### Research Lab Workflow

```bash
# 1. Convert DICOM to BIDS
yyprep dicom2bids participants.csv \
    --bids-dir /lab/data/bids \
    --heuristic /lab/scripts/heuristic.py

# 2. Preprocess with fMRIPrep
yyprep fmriprep /lab/data/bids /lab/data/derivatives participant \
    --participant-label 001 002 003 \
    --output-spaces MNI152NLin2009cAsym:res-2 \
    --fs-license-file /lab/software/license.txt \
    --use-aroma
```

### High-Performance Computing

```bash
# Submit as SLURM job
#!/bin/bash
#SBATCH --job-name=fmriprep
#SBATCH --cpus-per-task=24
#SBATCH --mem=64G
#SBATCH --time=24:00:00

yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label $SLURM_ARRAY_TASK_ID \
    --fs-license-file $HOME/license.txt \
    --n-cpus $SLURM_CPUS_PER_TASK \
    --mem-mb 64000 \
    --work-dir $SCRATCH/fmriprep_work
```

### Quality Control

```bash
# Generate detailed reports
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 \
    --fs-license-file license.txt \
    --write-graph \
    --verbose-count 2 \
    --work-dir /persistent/work
```

## Getting Help

For additional help:

```bash
# Command-specific help
yyprep dicom2bids --help
yyprep fmriprep --help

# Version information
yyprep --version

# Online documentation
# Visit: https://github.com/GalKepler/yyprep
```
