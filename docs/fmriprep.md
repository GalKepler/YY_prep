# fMRIPrep Integration

This guide covers using yyprep's fMRIPrep integration for preprocessing BIDS datasets.

## Overview

yyprep provides a simplified interface to fMRIPrep that:

- **Uses fmriprep-docker** for reliable containerized execution
- **Provides nipype-compatible interface** for workflow integration
- **Supports all major fMRIPrep options** through both CLI and Python API
- **Handles Docker management** automatically

## Prerequisites

### Required Setup

1. **Docker installed and running**
2. **FreeSurfer license** (for surface reconstruction)
3. **Valid BIDS dataset** (created with yyprep or other tools)
4. **Sufficient computational resources** (8GB+ RAM, multiple CPU cores)

### FreeSurfer License

Download from: https://surfer.nmr.mgh.harvard.edu/registration.html

Save as `license.txt` and note the path for fMRIPrep commands.

## Command Line Usage

### Basic Preprocessing

```bash
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 \
    --fs-license-file /path/to/license.txt
```

### Complete Example with Common Options

```bash
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 003 \
    --output-spaces MNI152NLin2009cAsym:res-2 T1w fsnative \
    --fs-license-file /path/to/license.txt \
    --work-dir /tmp/fmriprep_work \
    --mem-mb 16000 \
    --omp-nthreads 8 \
    --n-cpus 12 \
    --low-mem \
    --skull-strip-template OASIS30ANTs \
    --output-layout bids \
    --write-graph \
    --stop-on-first-crash
```

### Session-Specific Processing

```bash
# Process specific sessions
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 \
    --session-id baseline followup \
    --fs-license-file /path/to/license.txt

# Process specific tasks
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 \
    --task-id rest nback \
    --fs-license-file /path/to/license.txt
```

### Advanced Options

```bash
# Custom BIDS filtering
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 \
    --bids-filter-file /path/to/filter.json \
    --fs-license-file /path/to/license.txt

# Resource management
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 \
    --mem-mb 32000 \
    --omp-nthreads 16 \
    --n-cpus 24 \
    --fs-license-file /path/to/license.txt
```

## Python API Usage

### Basic Workflow

```python
from yyprep.fmriprep.interface import create_fmriprep_workflow

# Create and run workflow
workflow = create_fmriprep_workflow(
    bids_dir='/path/to/bids',
    output_dir='/path/to/output',
    participant_label=['001', '002'],
    fs_license_file='/path/to/license.txt'
)

result = workflow.run()
```

### Advanced Configuration

```python
from yyprep.fmriprep.interface import create_fmriprep_workflow

workflow = create_fmriprep_workflow(
    # Required parameters
    bids_dir='/path/to/bids',
    output_dir='/path/to/output',
    fs_license_file='/path/to/license.txt',
    
    # Participant selection
    participant_label=['001', '002', '003'],
    session_id=['baseline', 'followup'],
    task_id=['rest', 'nback'],
    
    # Output configuration
    output_spaces=['MNI152NLin2009cAsym:res-2', 'T1w', 'fsnative'],
    output_layout='bids',
    
    # Resource management
    work_dir='/scratch/fmriprep_work',
    mem_mb=32000,
    omp_nthreads=16,
    n_cpus=24,
    
    # Processing options
    skull_strip_template='OASIS30ANTs',
    low_mem=True,
    use_aroma=True,
    force_bbr=True,
    
    # Advanced options
    bids_filter_file='/path/to/filter.json',
    dummy_scans=5,
    random_seed=12345,
    
    # Debugging
    write_graph=True,
    stop_on_first_crash=True,
    verbose_count=2
)

# Run the workflow
result = workflow.run()
print(f"Workflow completed with return code: {result.returncode}")
```

### Nipype Integration

```python
from nipype import Workflow, Node
from yyprep.fmriprep.interface import FMRIPrepInterface

# Create fMRIPrep node
fmriprep_node = Node(
    FMRIPrepInterface(),
    name='fmriprep'
)

# Set inputs
fmriprep_node.inputs.bids_dir = '/path/to/bids'
fmriprep_node.inputs.output_dir = '/path/to/output'
fmriprep_node.inputs.participant_label = ['001', '002']
fmriprep_node.inputs.fs_license_file = '/path/to/license.txt'
fmriprep_node.inputs.output_spaces = ['MNI152NLin2009cAsym:res-2']

# Create workflow and add node
workflow = Workflow(name='preprocessing', base_dir='/tmp/work')
workflow.add_nodes([fmriprep_node])

# Run workflow
workflow.run()
```

## Configuration Options

### Participant Selection

```bash
# Specific participants
--participant-label 001 002 003

# Specific sessions
--session-id baseline followup

# Specific tasks
--task-id rest nback stroop
```

### Output Spaces

Common output space configurations:

```bash
# Standard volume spaces
--output-spaces MNI152NLin2009cAsym MNI152NLin6Asym

# With specific resolution
--output-spaces MNI152NLin2009cAsym:res-2

# Include native and surface spaces
--output-spaces T1w MNI152NLin2009cAsym:res-2 fsnative fsaverage

# Multiple templates
--output-spaces MNI152NLin2009cAsym MNI152NLin6Asym OASIS30ANTs
```

### Resource Management

```bash
# Memory limits
--mem-mb 16000          # 16GB memory limit

# CPU configuration  
--n-cpus 12            # Total CPU cores
--omp-nthreads 8       # OpenMP threads

# Low memory mode
--low-mem              # Enable low-memory mode
```

### Processing Options

```bash
# Skull stripping
--skull-strip-template OASIS30ANTs
--skull-strip-fixed-seed

# Surface reconstruction
--fs-subjects-dir /path/to/subjects
--fs-no-reconall

# Distortion correction
--use-syn-sdc
--force-syn

# ICA-AROMA
--use-aroma

# Fieldmap handling
--ignore fieldmaps
--fmap-bspline
--fmap-no-demean
```

## BIDS Filter Files

Create custom filter files to process specific data:

### Example Filter File

```json
{
    "bold": {
        "task": ["rest", "nback"],
        "run": [1, 2]
    },
    "t1w": {
        "acquisition": null
    },
    "fmap": {
        "suffix": ["phasediff", "magnitude1", "magnitude2"]
    }
}
```

### Usage

```bash
yyprep fmriprep /path/to/bids /path/to/output participant \
    --bids-filter-file filter.json \
    --fs-license-file license.txt
```

## Output Structure

fMRIPrep creates BIDS derivatives with this structure:

```
output/
├── dataset_description.json
├── desc-aparcaseg_dseg.tsv
├── desc-aseg_dseg.tsv
├── logs/
├── sub-001/
│   ├── anat/
│   │   ├── sub-001_desc-preproc_T1w.nii.gz
│   │   ├── sub-001_desc-brain_mask.nii.gz
│   │   ├── sub-001_dseg.nii.gz
│   │   └── sub-001_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5
│   ├── func/
│   │   ├── sub-001_task-rest_space-T1w_desc-preproc_bold.nii.gz
│   │   ├── sub-001_task-rest_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz
│   │   ├── sub-001_task-rest_desc-confounds_timeseries.tsv
│   │   └── sub-001_task-rest_space-T1w_boldref.nii.gz
│   └── figures/
└── sub-002/
    └── ...
```

## Quality Control

### HTML Reports

fMRIPrep generates individual HTML reports:

```
output/sub-001.html
output/sub-002.html
```

Open these in a web browser to review preprocessing quality.

### Key QC Metrics

1. **Registration quality**: Check alignment between spaces
2. **Motion parameters**: Review confounds files for excessive motion
3. **Brain extraction**: Verify skull-stripping quality
4. **Distortion correction**: Check fieldmap-based corrections

### Confounds Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load confounds
confounds = pd.read_csv('output/sub-001/func/sub-001_task-rest_desc-confounds_timeseries.tsv', sep='\t')

# Plot motion parameters
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Translation
confounds[['trans_x', 'trans_y', 'trans_z']].plot(ax=axes[0])
axes[0].set_title('Translation Parameters')
axes[0].set_ylabel('mm')

# Rotation  
confounds[['rot_x', 'rot_y', 'rot_z']].plot(ax=axes[1])
axes[1].set_title('Rotation Parameters')
axes[1].set_ylabel('radians')

plt.tight_layout()
plt.show()
```

## Troubleshooting

### Common Issues

**Docker permission errors:**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Memory issues:**
```bash
# Increase Docker memory limits in Docker Desktop
# Or use --low-mem flag
yyprep fmriprep /path/to/bids /path/to/output participant --low-mem
```

**FreeSurfer license errors:**
```bash
# Ensure license file exists and is readable
ls -la /path/to/license.txt
cat /path/to/license.txt
```

**BIDS validation errors:**
```bash
# Check BIDS compliance first
bids-validator /path/to/bids
```

### Debugging Options

```bash
# Verbose output
yyprep fmriprep /path/to/bids /path/to/output participant \
    --verbose-count 2 \
    --write-graph \
    --stop-on-first-crash

# Keep work directory for inspection
yyprep fmriprep /path/to/bids /path/to/output participant \
    --work-dir /persistent/work/dir \
    --stop-on-first-crash
```

### Resource Monitoring

Monitor resource usage during processing:

```bash
# Monitor Docker containers
docker stats

# Monitor system resources
htop

# Check disk space
df -h
```

## Performance Optimization

### Resource Allocation

- **CPU cores**: Use `--n-cpus` to match your system
- **Memory**: Allocate 2-4GB per CPU core with `--mem-mb`
- **OpenMP threads**: Set `--omp-nthreads` to 1/2 of CPU cores
- **Work directory**: Use fast storage (SSD) for `--work-dir`

### Parallel Processing

```bash
# Process multiple subjects in parallel (separate commands)
# Subject 001
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 &

# Subject 002  
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 002 &

# Wait for completion
wait
```

## Next Steps

- Review [CLI reference](cli.md) for complete option details
- Explore [workflow examples](workflows.md) for integration patterns
- Check [troubleshooting guide](troubleshooting.md) for specific issues
