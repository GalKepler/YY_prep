# YY Preprocessing Documentation

Welcome to the documentation for **yyprep** - a comprehensive tool for DICOM to BIDS conversion and fMRIPrep preprocessing, developed for Prof. Yaara Yeshurun's Lab.

## What is yyprep?

YY Preprocessing (`yyprep`) is a Python package that streamlines neuroimaging data preprocessing workflows by providing:

- **DICOM to BIDS conversion** using HeuDiConv with automatic fieldmap handling
- **fMRIPrep preprocessing** through a simplified nipype-compatible interface
- **Unified command-line interface** for complete preprocessing pipelines
- **Python API** for programmatic workflow control

## Quick Start

### Installation
```bash
pip install yyprep
```

### Basic Usage
```bash
# Convert DICOM to BIDS
yyprep dicom2bids participants.csv --bids-dir /path/to/bids --heuristic heuristic.py

# Run fMRIPrep preprocessing
yyprep fmriprep /path/to/bids /path/to/output participant --participant-label 001 002
```

## Documentation Sections

### Getting Started
- [Installation](installation.md) - Setup and requirements
- [Quick Start Guide](quickstart.md) - Get up and running in minutes
- [Configuration](configuration.md) - Setup and customization

### User Guide
- [DICOM to BIDS Conversion](dicom2bids.md) - Convert your DICOM data to BIDS format
- [fMRIPrep Integration](fmriprep.md) - Preprocess your BIDS data with fMRIPrep
- [Command Line Interface](cli.md) - Complete CLI reference
- [Python API](api.md) - Use yyprep in your Python scripts

### Advanced Topics
- [Heuristics](heuristics.md) - Custom DICOM conversion rules
- [Workflows](workflows.md) - Creating custom preprocessing pipelines
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

### Development
- [Contributing](contributing.md) - How to contribute to the project
- [API Reference](api_reference.md) - Detailed API documentation
- [Release Notes](history.md) - Version history and changes

## Examples

Explore complete examples in our [examples directory](https://github.com/GalKepler/yyprep/tree/main/examples):

- **Complete Jupyter Notebook**: `tzlil_preprocessing.ipynb` - End-to-end preprocessing workflow
- **Python Script**: `fmriprep_usage.py` - fMRIPrep integration examples

## Features

✅ **DICOM to BIDS Conversion**
- Automated conversion using HeuDiConv
- Custom heuristic support
- Automatic fieldmap IntendedFor handling

✅ **fMRIPrep Integration**
- Nipype-compatible interface
- Docker-based execution via fmriprep-docker
- Comprehensive parameter support

✅ **Unified CLI**
- Single command for complete pipelines
- Flexible parameter configuration
- Dry-run capabilities

✅ **Python API**
- Programmatic workflow control
- Integration with existing pipelines
- Jupyter notebook support

## Support

- **Issues**: [GitHub Issues](https://github.com/GalKepler/yyprep/issues)
- **Discussions**: [GitHub Discussions](https://github.com/GalKepler/yyprep/discussions)
- **Documentation**: This documentation site
