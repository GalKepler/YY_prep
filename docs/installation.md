# Installation

## System Requirements

Before installing yyprep, ensure your system meets these requirements:

- **Python**: 3.10 or higher
- **Operating System**: Linux, macOS, or Windows (with WSL2 recommended)
- **Docker**: Required for fMRIPrep functionality
- **Memory**: At least 8GB RAM (16GB+ recommended for fMRIPrep)
- **Storage**: Sufficient space for BIDS data and fMRIPrep outputs

## Dependencies

yyprep requires several external tools:

### Required
- **dcm2niix**: DICOM to NIfTI conversion
- **Docker**: Container runtime for fMRIPrep

### Optional but Recommended
- **FreeSurfer license**: Required for fMRIPrep surface reconstruction
- **Git**: For development installation

## Installation Methods

### Method 1: Stable Release (Recommended)

Install the latest stable release from PyPI:

```bash
pip install yyprep
```

Or using uv (faster):

```bash
uv add yyprep
```

### Method 2: Development Installation

For the latest features or to contribute to development:

```bash
# Clone the repository
git clone https://github.com/GalKepler/yyprep.git
cd yyprep

# Install in development mode
pip install -e ".[test]"
```

### Method 3: Conda Environment (Recommended for Research)

Create an isolated environment for neuroimaging work:

```bash
# Create conda environment
conda create -n yyprep python=3.11
conda activate yyprep

# Install dcm2niix via conda
conda install -c conda-forge dcm2niix

# Install yyprep
pip install yyprep
```

## External Dependencies Setup

### Installing dcm2niix

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install dcm2niix
```

**On macOS:**
```bash
brew install dcm2niix
```

**On Windows:**
Download from: https://github.com/rordenlab/dcm2niix/releases

**Via Conda (all platforms):**
```bash
conda install -c conda-forge dcm2niix
```

### Installing Docker

**On Ubuntu:**
```bash
# Install Docker
sudo apt update
sudo apt install docker.io

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

**On macOS:**
Download Docker Desktop from: https://www.docker.com/products/docker-desktop

**On Windows:**
Download Docker Desktop from: https://www.docker.com/products/docker-desktop

### FreeSurfer License

1. Register at: https://surfer.nmr.mgh.harvard.edu/registration.html
2. Download the `license.txt` file
3. Note the path for use with fMRIPrep commands

## Verification

Verify your installation:

```bash
# Check yyprep installation
yyprep --help

# Check dcm2niix
dcm2niix -h

# Check Docker
docker --version

# Test Docker permissions (should not require sudo)
docker run hello-world
```

## Optional: HeuDiConv Installation

While not strictly required (yyprep can use any HeuDiConv installation), you may want to install HeuDiConv in the same environment:

```bash
pip install heudiconv
```

## Troubleshooting

### Common Issues

**"yyprep command not found"**
- Ensure the installation completed successfully
- Check if `~/.local/bin` is in your PATH
- Try running `python -m yyprep` instead

**Docker permission denied**
- Add your user to the docker group: `sudo usermod -aG docker $USER`
- Log out and log back in
- Restart Docker service: `sudo systemctl restart docker`

**dcm2niix not found**
- Install dcm2niix using your package manager
- Ensure it's in your PATH: `which dcm2niix`

**Memory errors during fMRIPrep**
- Increase Docker memory limits in Docker Desktop settings
- Use `--mem-mb` option to limit memory usage
- Use `--low-mem` flag for low-memory systems

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search [existing issues](https://github.com/GalKepler/yyprep/issues)
3. Create a new issue with:
   - Your OS and Python version
   - Complete error message
   - Steps to reproduce the problem

## Next Steps

- Follow the [Quick Start Guide](quickstart.md) to run your first conversion
- Read about [DICOM to BIDS conversion](dicom2bids.md)
- Explore [fMRIPrep integration](fmriprep.md)
