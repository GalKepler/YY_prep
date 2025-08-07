# YY Preprocessing



A simple Python pipeline to convert DICOM directories to BIDS format and preprocess them using fMRIPrep. Provides an easy-to-use CLI built with Typer.

Package written specifically for the in-house use in Prof. Yaara Yeshurun's Lab.

## Overview

|  |  | 
|--------|-------------|
| Docs | [![Documentation Status](https://readthedocs.org/projects/yy-prep/badge/?version=latest)](https://yy-prep.readthedocs.io/en/latest/?version=latest)
| Tests, CI | [![CI](https://github.com/GalKepler/YY_prep/actions/workflows/test.yml/badge.svg)](https://github.com/GalKepler/YY_prep/actions)
| Version | [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)  ![PyPI version](https://img.shields.io/pypi/v/yyprep.svg)
| License | [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Features

This tool helps you:

- 🔄 **Convert DICOM to BIDS**: Seamlessly convert DICOM sessions to the BIDS standard using HeuDiConv
- 🗂️ **Update fieldmaps**: Automatically update `IntendedFor` fields in BIDS fieldmap JSON files for fMRIPrep compatibility
- 📊 **CSV integration**: Integrate with your own data structure using a user-generated CSV file
- ⚡ **Modern CLI**: Run the workflow with a single, modern, tab-completing command-line interface built with Typer
- 🔬 **fMRIPrep integration**: Run fMRIPrep preprocessing with a nipype-like interface using Docker
- 🏗️ **Heuristic support**: Use predefined or custom heuristics for flexible DICOM conversion
- 🐳 **Docker ready**: Built-in Docker support for fMRIPrep execution

## Quick Start

### Installation

**Recommended**: Install in a virtual environment.

```bash
# Install from PyPI
pip install yyprep

# Or install from source for development
git clone https://github.com/GalKepler/yyprep.git
cd yyprep
pip install -e .
```

### Basic Usage

1. **Prepare your data**: Create a CSV file with your participant information:

| subject_code | session_id | dicom_path |
|--------|-------------|---------|
| 001 | 001 | /path/to/dicom_directory |
| 002 | 001 | /path/to/dicom_directory |


2. **Run the conversion**:

```bash
yyprep dicom2bids participants.csv \
  --bids-dir /path/to/output/bids \
  --heuristic /path/to/your/heuristic.py
```

3. **Run fMRIPrep preprocessing**:

```bash
yyprep fmriprep /path/to/output/bids /path/to/fmriprep_output \
  --participant-label 001 002 \
  --output-spaces MNI152NLin2009cAsym:res-2
```

That's it! Your DICOM data will be converted to BIDS format and preprocessed with fMRIPrep.

## Detailed Usage

### Command Line Interface

The package provides two main commands:

#### DICOM to BIDS Conversion

The `yyprep dicom2bids` command converts DICOM files to BIDS format:

```bash
yyprep dicom2bids [OPTIONS] PARTICIPANTS_CSV
```

**Required Arguments:**
- `PARTICIPANTS_CSV`: Path to CSV file containing subject/session/DICOM information

**Options:**
- `--bids-dir`: Root output directory for BIDS dataset (required)
- `--heuristic`: Path to heuristic Python file for heudiconv (required)
- `--heudiconv-template`: Custom template for heudiconv command (optional)
- `--overwrite`: Pass --overwrite to heudiconv (default: False)
- `--skip-intendedfor`: Skip updating IntendedFor fields (default: False)
- `--dry-run`: Print commands but do not run conversion (default: False)

#### fMRIPrep Preprocessing

The `yyprep fmriprep` command runs fMRIPrep preprocessing:

```bash
yyprep fmriprep [OPTIONS] BIDS_DIR OUTPUT_DIR
```

**Required Arguments:**
- `BIDS_DIR`: Path to BIDS dataset directory
- `OUTPUT_DIR`: Path to output directory for fMRIPrep derivatives

**Options:**
- `--participant-label`: List of participant labels to process
- `--session-id`: List of session IDs to process
- `--task-id`: List of task IDs to process
- `--output-spaces`: Output spaces for resampling (default: MNI152NLin2009cAsym:res-2)
- `--fs-license-file`: Path to FreeSurfer license file
- `--work-dir`: Working directory for temporary files
- `--n-cpus`: Number of CPUs to use
- `--omp-nthreads`: Maximum number of threads per process
- `--mem-gb`: Memory limit in GB
- `--bids-filter-file`: Path to BIDS filter file for selecting specific data
- `--skip-bids-validation`: Skip BIDS validation
- `--low-mem`: Attempt to reduce memory usage
- `--docker-image`: Docker image to use (default: nipreps/fmriprep:latest)
- `--dry-run`: Print command but do not run fMRIPrep

### CSV Format

Your participants CSV should include the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `subject_code` | Subject identifier | `001` |
| `session_id` | Session identifier | `01`, `baseline` |
| `dicom_path` | Path to DICOM directory | `/data/dicoms/sub001_ses01` |

### Heuristics

The package includes built-in heuristics for common scanning protocols. You can also provide your own heuristic file:

```python
from yyprep.utils import get_heuristics

# Get available built-in heuristics
heuristics = get_heuristics()
print(heuristics)  # {'tzlil': '/path/to/tzlil_heuristic.py'}

# Use a built-in heuristic
heuristic_path = heuristics['tzlil']
```

### Python API

You can also use yyprep programmatically:

```python
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for

# Load your data
df = pd.read_csv('participants.csv')

# Convert DICOM to BIDS (using default heudiconv template)
convert_dicom_to_bids(
    df=df,
    heuristic='/path/to/heuristic.py',
    bids_path='/path/to/output/bids',
    overwrite=False
)

# Or with a custom heudiconv template
convert_dicom_to_bids(
    df=df,
    heuristic='/path/to/heuristic.py',
    bids_path='/path/to/output/bids',
    heudiconv_cmd_template="heudiconv -d '{dicom_directory}' -s {subject_id} ...",
    overwrite=False
)

# Update IntendedFor fields
update_intended_for('/path/to/output/bids', df)

# Run fMRIPrep preprocessing
from yyprep.fmriprep.interface import create_fmriprep_workflow

workflow = create_fmriprep_workflow(
    bids_dir='/path/to/output/bids',
    output_dir='/path/to/fmriprep_output',
    participant_label=['001', '002'],
    output_spaces=['MNI152NLin2009cAsym:res-2'],
    work_dir='/path/to/work',
    omp_nthreads=8,  # Number of OpenMP threads
    bids_filter_file='/path/to/filter.json'  # Custom BIDS filter
)
result = workflow.run()
```

## Examples

Check out the `examples/` directory for complete examples:

- `tzlil_preprocessing.ipynb`: Complete notebook showing the preprocessing workflow
- `fmriprep_usage.py`: Examples of using the fMRIPrep interface programmatically

## Requirements

- Python 3.10+
- HeuDiConv
- dcm2niix
- fmriprep-docker (for fMRIPrep)
- Dependencies: typer, pandas, nipype, fmriprep-docker

## Development

### Setting up for development

```bash
git clone https://github.com/GalKepler/yyprep.git
cd yyprep
pip install -e ".[test]"
```

### Running tests

```bash
pytest
```

### Code formatting and linting

```bash
ruff check .
ruff format .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate and follow the existing code style.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{yyprep,
  author = {Kepler, Gal},
  title = {YY Preprocessing: DICOM to BIDS conversion and fMRIPrep preparation},
  url = {https://github.com/GalKepler/yyprep},
  version = {0.1.0},
  year = {2025}
}
```

## Support

- 📖 **Documentation**: https://yyprep.readthedocs.io
- 🐛 **Bug reports**: https://github.com/GalKepler/yyprep/issues
- 💬 **Questions**: Open an issue on GitHub

## Acknowledgments

- Built for Prof. Yaara Yeshurun's Lab
- Uses HeuDiConv for DICOM to BIDS conversion
- Integrates with the fMRIPrep preprocessing pipeline

