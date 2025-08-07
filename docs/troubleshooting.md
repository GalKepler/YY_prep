# Troubleshooting

This guide helps you resolve common issues when using yyprep.

## General Troubleshooting

### Getting Help

Before diving into specific issues:

1. **Check the logs**: yyprep provides detailed logging
2. **Verify your setup**: Ensure all dependencies are installed
3. **Test with minimal examples**: Start with a single subject
4. **Check system resources**: Monitor CPU, memory, and disk usage

### Verbose Logging

Enable detailed logging to diagnose issues:

```bash
# Command line
yyprep fmriprep /data/bids /data/derivatives participant \
    --verbose-count 2 \
    --stop-on-first-crash

# Environment variable for HeuDiConv
export HEUDICONV_LOG_LEVEL=DEBUG
```

```python
# Python logging
import logging
logging.basicConfig(level=logging.DEBUG)

# yyprep with debugging
from yyprep.fmriprep.interface import create_fmriprep_workflow

workflow = create_fmriprep_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    participant_label=['001'],
    verbose_count=2,
    stop_on_first_crash=True
)
```

## Installation Issues

### pip install failures

**Problem**: `pip install yyprep` fails

**Solutions**:

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -v yyprep

# Try installing dependencies separately
pip install typer pandas nipype
pip install yyprep

# Use conda for difficult dependencies
conda install -c conda-forge dcm2niix
pip install yyprep
```

### Module import errors

**Problem**: `ImportError: No module named 'yyprep'`

**Solutions**:

```bash
# Check installation
pip list | grep yyprep

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall in current environment
pip uninstall yyprep
pip install yyprep

# For development installation
cd /path/to/yyprep
pip install -e .
```

### dcm2niix not found

**Problem**: `dcm2niix: command not found`

**Solutions**:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install dcm2niix

# macOS
brew install dcm2niix

# Conda (all platforms)
conda install -c conda-forge dcm2niix

# Verify installation
which dcm2niix
dcm2niix -h
```

## Docker Issues

### Docker permission denied

**Problem**: `permission denied while trying to connect to Docker daemon`

**Solutions**:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then test
docker run hello-world

# Alternative: run with sudo (not recommended)
sudo yyprep fmriprep ...

# Check Docker is running
sudo systemctl status docker
sudo systemctl start docker
```

### Docker out of memory

**Problem**: Docker containers killed due to memory limits

**Solutions**:

```bash
# Increase Docker memory in Docker Desktop
# Settings > Resources > Advanced > Memory

# Use low-memory mode
yyprep fmriprep /data/bids /data/derivatives participant \
    --low-mem \
    --mem-mb 8000

# Monitor Docker memory usage
docker stats
```

### Docker disk space issues

**Problem**: `No space left on device`

**Solutions**:

```bash
# Clean up Docker
docker system prune -a

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Check Docker disk usage
docker system df

# Change Docker data directory (advanced)
# Edit /etc/docker/daemon.json:
{
  "data-root": "/path/to/larger/disk"
}
```

## DICOM to BIDS Issues

### HeuDiConv errors

**Problem**: HeuDiConv fails with various errors

**Solutions**:

```bash
# Test heuristic syntax
python heuristic.py

# Run HeuDiConv directly for debugging
heudiconv -d '/path/to/dicoms' -s 001 -ss baseline \
    -o /output/bids -f heuristic.py -c dcm2niix --dry-run

# Check DICOM directory structure
ls -la /path/to/dicoms/

# Verify DICOM files are valid
dcm2niix -o /tmp /path/to/dicoms/series001/
```

### Heuristic issues

**Problem**: Heuristic doesn't match expected files

**Solutions**:

```python
# Debug heuristic with print statements
def infotodict(seqinfo):
    # Add debugging
    for i, s in enumerate(seqinfo):
        print(f"Series {i}: {s.protocol_name}, {s.series_description}")
    
    # Your heuristic logic here
    return info

# Test with minimal heuristic
def infotodict(seqinfo):
    t1w = create_key('sub-{subject}/anat/sub-{subject}_T1w')
    info = {t1w: []}
    
    for s in seqinfo:
        if 't1' in s.protocol_name.lower():
            info[t1w].append(s.series_id)
    
    return info
```

### Missing IntendedFor fields

**Problem**: Fieldmaps not linked to functional scans

**Solutions**:

```python
# Manual IntendedFor update
from yyprep.dicom2bids.intended_for import update_intended_for
import pandas as pd

df = pd.read_csv('participants.csv')
update_intended_for('/path/to/bids', df)

# Check fieldmap JSON files
import json
fmap_json = '/path/to/bids/sub-001/ses-baseline/fmap/sub-001_ses-baseline_phasediff.json'
with open(fmap_json) as f:
    metadata = json.load(f)
    print(f"IntendedFor: {metadata.get('IntendedFor', 'Not found')}")

# Skip IntendedFor if problematic
yyprep dicom2bids participants.csv \
    --bids-dir /path/to/bids \
    --heuristic heuristic.py \
    --skip-intendedfor
```

## fMRIPrep Issues

### FreeSurfer license errors

**Problem**: `ERROR: You must now purchase a license`

**Solutions**:

```bash
# Download license from https://surfer.nmr.mgh.harvard.edu/registration.html
# Save as license.txt and specify path

yyprep fmriprep /data/bids /data/derivatives participant \
    --fs-license-file /path/to/license.txt

# Check license file format
cat /path/to/license.txt
# Should contain: your_email_address, license_number, *key

# Set environment variable
export FREESURFER_LICENSE=/path/to/license.txt
```

### BIDS validation errors

**Problem**: fMRIPrep refuses to run due to BIDS errors

**Solutions**:

```bash
# Install and run BIDS validator
npm install -g bids-validator
bids-validator /path/to/bids

# Common fixes:
# 1. Add dataset_description.json
cat > /path/to/bids/dataset_description.json << EOF
{
    "Name": "My Dataset",
    "BIDSVersion": "1.8.0"
}
EOF

# 2. Add participants.tsv
echo -e "participant_id\nsub-001\nsub-002" > /path/to/bids/participants.tsv

# 3. Fix file naming
# Ensure files follow BIDS naming conventions
```

### fMRIPrep crashes

**Problem**: fMRIPrep exits with error codes

**Solutions**:

```bash
# Run with crash debugging
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 \
    --stop-on-first-crash \
    --work-dir /persistent/work \
    --write-graph

# Check work directory for crash files
ls /persistent/work/fmriprep_wf/*/crash*

# Reduce resource usage
yyprep fmriprep /data/bids /data/derivatives participant \
    --low-mem \
    --mem-mb 8000 \
    --omp-nthreads 2 \
    --n-cpus 4

# Try processing single subject
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001
```

### Anatomical processing failures

**Problem**: T1w preprocessing fails

**Solutions**:

```bash
# Try different skull-stripping template
yyprep fmriprep /data/bids /data/derivatives participant \
    --skull-strip-template OASIS30ANTs

# Skip FreeSurfer if problematic
yyprep fmriprep /data/bids /data/derivatives participant \
    --fs-no-reconall

# Use existing FreeSurfer results
yyprep fmriprep /data/bids /data/derivatives participant \
    --fs-subjects-dir /path/to/subjects
```

### Functional processing failures

**Problem**: BOLD preprocessing fails

**Solutions**:

```bash
# Skip problematic data types
yyprep fmriprep /data/bids /data/derivatives participant \
    --ignore fieldmaps

# Force specific distortion correction
yyprep fmriprep /data/bids /data/derivatives participant \
    --use-syn-sdc \
    --force-syn

# Process specific tasks only
yyprep fmriprep /data/bids /data/derivatives participant \
    --task-id rest

# Custom BIDS filter
cat > filter.json << EOF
{
    "bold": {
        "task": ["rest"],
        "run": [1]
    }
}
EOF

yyprep fmriprep /data/bids /data/derivatives participant \
    --bids-filter-file filter.json
```

## Performance Issues

### Slow processing

**Problem**: Processing takes too long

**Solutions**:

```bash
# Optimize resource allocation
yyprep fmriprep /data/bids /data/derivatives participant \
    --n-cpus 12 \
    --omp-nthreads 8 \
    --mem-mb 32000

# Use faster work directory (SSD)
yyprep fmriprep /data/bids /data/derivatives participant \
    --work-dir /fast/ssd/work

# Process subjects in parallel
# Terminal 1:
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 &

# Terminal 2:
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 002 &
```

### Memory issues

**Problem**: Out of memory errors

**Solutions**:

```bash
# Enable low-memory mode
yyprep fmriprep /data/bids /data/derivatives participant \
    --low-mem

# Reduce memory allocation
yyprep fmriprep /data/bids /data/derivatives participant \
    --mem-mb 8000

# Process one subject at a time
for subject in 001 002 003; do
    yyprep fmriprep /data/bids /data/derivatives participant \
        --participant-label $subject
done

# Monitor memory usage
htop
# or
watch -n 5 'free -h'
```

## Data Issues

### Missing data

**Problem**: Expected files not found

**Solutions**:

```bash
# Check BIDS dataset structure
tree /path/to/bids -L 3

# Verify required files exist
ls /path/to/bids/sub-001/anat/
ls /path/to/bids/sub-001/func/

# Check file permissions
ls -la /path/to/bids/sub-001/

# Re-run conversion if needed
yyprep dicom2bids participants.csv \
    --bids-dir /path/to/bids \
    --heuristic heuristic.py \
    --overwrite
```

### Corrupted files

**Problem**: Files appear corrupted or incomplete

**Solutions**:

```bash
# Check file integrity
file /path/to/bids/sub-001/anat/sub-001_T1w.nii.gz

# Verify NIfTI files
fslhd /path/to/bids/sub-001/anat/sub-001_T1w.nii.gz

# Re-convert problematic files
yyprep dicom2bids participants.csv \
    --bids-dir /path/to/bids \
    --heuristic heuristic.py \
    --overwrite

# Check original DICOM files
dcm2niix -o /tmp /path/to/original/dicoms/
```

## Network Issues

### Download failures

**Problem**: Can't download required templates/containers

**Solutions**:

```bash
# Check internet connectivity
ping 8.8.8.8

# Set proxy if needed
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080

# Pre-download Docker images
docker pull nipreps/fmriprep:latest

# Manual template download (if needed)
mkdir -p ~/.cache/templateflow
# Download templates manually to this directory
```

## Environment Issues

### Python path problems

**Problem**: Wrong Python/packages being used

**Solutions**:

```bash
# Check Python environment
which python
which pip
python -c "import sys; print(sys.path)"

# Activate correct environment
conda activate yyprep
# or
source /path/to/venv/bin/activate

# Verify yyprep installation
python -c "import yyprep; print(yyprep.__file__)"

# Reinstall if needed
pip uninstall yyprep
pip install yyprep
```

### File permission issues

**Problem**: Permission denied errors

**Solutions**:

```bash
# Check and fix permissions
ls -la /path/to/data/
chmod -R 755 /path/to/data/

# Fix ownership if needed
sudo chown -R $USER:$USER /path/to/data/

# Run with proper permissions
umask 022  # Set default permissions
yyprep dicom2bids ...
```

## System-Specific Issues

### macOS Issues

```bash
# Install Xcode command line tools
xcode-select --install

# Use Homebrew for dependencies
brew install dcm2niix

# Docker Desktop configuration
# Increase memory and disk limits in preferences
```

### Windows/WSL Issues

```bash
# Use WSL2 for best compatibility
wsl --set-default-version 2

# Install Docker Desktop with WSL2 backend
# Mount Windows drives properly
# Use /mnt/c/path/to/data instead of C:\path\to\data

# Set up proper file permissions
sudo mount -t drvfs C: /mnt/c -o metadata,uid=1000,gid=1000
```

### HPC/Cluster Issues

```bash
# Load required modules
module load singularity
module load python

# Set up proper environment
export SINGULARITYENV_TEMPLATEFLOW_HOME=/scratch/templateflow
export SINGULARITYENV_FREESURFER_LICENSE=/home/user/license.txt

# Use scratch space for work directory
yyprep fmriprep /data/bids /data/derivatives participant \
    --work-dir $SCRATCH/fmriprep_work
```

## Getting Additional Help

### Gathering Information for Bug Reports

When reporting issues, include:

```bash
# System information
uname -a
python --version
docker --version

# yyprep version
yyprep --version

# Environment details
pip list | grep -E "(yyprep|nipype|fmriprep)"

# Error logs
# Copy complete error messages and stack traces

# Minimal example
# Provide smallest possible example that reproduces the issue
```

### Where to Get Help

1. **GitHub Issues**: https://github.com/GalKepler/yyprep/issues
2. **GitHub Discussions**: https://github.com/GalKepler/yyprep/discussions
3. **fMRIPrep Community**: https://neurostars.org/tags/fmriprep
4. **HeuDiConv Issues**: https://github.com/nipy/heudiconv/issues

### Creating Effective Bug Reports

Include these sections in your bug report:

```markdown
## Environment
- OS: [Ubuntu 22.04 / macOS 13.0 / Windows 11]
- Python version: [3.11.0]
- yyprep version: [0.1.0]
- Docker version: [20.10.17]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]

## Error Message
```
[Complete error message and stack trace]
```

## Additional Context
[Any additional information that might be helpful]
```

## Prevention

### Best Practices to Avoid Issues

1. **Start small**: Test with one subject before batch processing
2. **Validate early**: Check BIDS compliance before fMRIPrep
3. **Monitor resources**: Keep an eye on CPU, memory, and disk usage
4. **Keep logs**: Save output logs for debugging
5. **Use version control**: Track your heuristics and configurations
6. **Document your setup**: Record working configurations
7. **Regular cleanup**: Remove old work directories and Docker images

### Testing Setup

```bash
# Test basic functionality
yyprep --help
yyprep dicom2bids --help
yyprep fmriprep --help

# Test with dry run
yyprep dicom2bids test_participants.csv \
    --bids-dir /tmp/test_bids \
    --heuristic test_heuristic.py \
    --dry-run

# Test minimal fMRIPrep run
yyprep fmriprep /path/to/test/bids /tmp/test_output participant \
    --participant-label 001 \
    --fs-license-file /path/to/license.txt \
    --dry-run
```
