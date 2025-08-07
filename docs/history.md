# Release History

This page documents the release history and changes for yyprep.

## Version 0.1.0 (2025-08-07)

🎉 **Initial Release**

This is the first official release of yyprep, a comprehensive tool for DICOM to BIDS conversion and fMRIPrep preprocessing.

### Features

#### DICOM to BIDS Conversion
- **HeuDiConv Integration**: Seamless conversion using HeuDiConv with custom heuristics
- **Automatic Fieldmap Handling**: Intelligent IntendedFor field updates for fieldmaps
- **Batch Processing**: Process multiple subjects and sessions efficiently
- **Custom Templates**: Flexible HeuDiConv command templates
- **Dry Run Support**: Preview conversions before execution

#### fMRIPrep Integration
- **Nipype Interface**: Full nipype-compatible interface for workflow integration
- **Docker Management**: Automatic Docker container handling via fmriprep-docker
- **Comprehensive Options**: Support for all major fMRIPrep parameters including:
  - Output spaces configuration
  - Resource management (CPU, memory, threads)
  - Processing options (ICA-AROMA, skull stripping, etc.)
  - Advanced options (BIDS filtering, random seeds, etc.)

#### Command Line Interface
- **Unified CLI**: Single command-line tool for both conversion and preprocessing
- **Typer Framework**: Modern, intuitive command-line interface
- **Comprehensive Help**: Detailed help text and examples for all commands

#### Python API
- **Programmatic Access**: Full Python API for script integration
- **Workflow Creation**: Helper functions for creating preprocessing workflows
- **Error Handling**: Robust error handling and logging

### Supported Platforms
- Linux (Ubuntu 20.04+, CentOS 7+)
- macOS (10.15+)
- Windows (with WSL2)

### Dependencies
- Python 3.10+
- HeuDiConv
- dcm2niix
- Docker
- fmriprep-docker
- nipype
- typer
- pandas

### Installation
```bash
pip install yyprep
```

### Basic Usage

**DICOM to BIDS:**
```bash
yyprep dicom2bids participants.csv --bids-dir /data/bids --heuristic heuristic.py
```

**fMRIPrep Preprocessing:**
```bash
yyprep fmriprep /data/bids /data/derivatives participant --participant-label 001 002 --fs-license-file license.txt
```

### Documentation
- Comprehensive documentation with examples
- Quick start guide
- API reference
- Troubleshooting guide

### Known Limitations
- Requires Docker for fMRIPrep functionality
- FreeSurfer license required for surface reconstruction
- Large memory requirements for processing (8GB+ recommended)

### Contributors
- Gal Kepler (@GalKepler) - Lead Developer

---

## Development Releases

### Pre-release Development

Prior to the 0.1.0 release, yyprep was developed internally for Prof. Yaara Yeshurun's Lab at Tel Aviv University. Key development milestones included:

- **Core Architecture**: Established modular design with separate dicom2bids and fmriprep modules
- **CLI Development**: Created Typer-based command-line interface
- **fMRIPrep Integration**: Developed nipype-compatible interface for fMRIPrep
- **Documentation**: Created comprehensive documentation site
- **Testing**: Established test suite and CI/CD pipeline

---

## Upcoming Features

### Planned for 0.2.0
- [ ] **Enhanced BIDS Validation**: Built-in BIDS validation before processing
- [ ] **Progress Monitoring**: Real-time progress tracking for long-running processes
- [ ] **Template Management**: Automatic TemplateFlow template management
- [ ] **Quality Control**: Automated QC report generation
- [ ] **HPC Integration**: Better support for high-performance computing environments

### Future Roadmap
- [ ] **GUI Interface**: Web-based graphical interface for non-technical users
- [ ] **Cloud Support**: Integration with cloud computing platforms
- [ ] **Additional Pipelines**: Support for additional preprocessing pipelines (QSIPrep, ASLPrep)
- [ ] **Database Integration**: Optional database backend for large studies
- [ ] **Advanced Monitoring**: Resource usage monitoring and optimization recommendations

---

## Migration Guide

### From Development Versions

If you were using pre-release development versions:

1. **Update Installation**:
   ```bash
   pip uninstall yyprep
   pip install yyprep
   ```

2. **Check Configuration**: Review your heuristic files and configurations
3. **Test Workflows**: Run test conversions to ensure compatibility
4. **Update Scripts**: Update any custom scripts to use the new API

### Breaking Changes
No breaking changes in this initial release.

---

## Support

### Getting Help
- **Documentation**: https://github.com/GalKepler/yyprep/docs
- **Issues**: https://github.com/GalKepler/yyprep/issues
- **Discussions**: https://github.com/GalKepler/yyprep/discussions

### Reporting Issues
When reporting issues, please include:
- yyprep version (`yyprep --version`)
- Operating system and version
- Python version
- Complete error messages
- Minimal example to reproduce the issue

### Contributing
We welcome contributions! See our [Contributing Guide](contributing.md) for details on how to get started.

---

## Acknowledgments

### Special Thanks
- **Prof. Yaara Yeshurun** - For providing the research context and requirements
- **The fMRIPrep Team** - For creating the excellent fMRIPrep preprocessing pipeline
- **The HeuDiConv Team** - For the robust DICOM to BIDS conversion tool
- **The Nipype Community** - For the powerful workflow framework

### Built With
yyprep builds upon several excellent open-source projects:
- [fMRIPrep](https://fmriprep.org/) - Functional MRI preprocessing pipeline
- [HeuDiConv](https://heudiconv.readthedocs.io/) - DICOM to BIDS converter
- [Nipype](https://nipype.readthedocs.io/) - Neuroimaging workflow framework
- [Typer](https://typer.tiangolo.com/) - Modern CLI framework
- [Docker](https://www.docker.com/) - Containerization platform

---

*For the complete commit history, see the [GitHub repository](https://github.com/GalKepler/yyprep/commits/main).*
