# Quick Start Guide

This guide will get you up and running with yyprep in just a few minutes.

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher
- Docker (for fMRIPrep functionality)
- dcm2niix installed
- Access to your DICOM data

## Installation

Install yyprep using pip:

```bash
pip install yyprep
```

For development installation:

```bash
git clone https://github.com/GalKepler/yyprep.git
cd yyprep
pip install -e ".[test]"
```

## Step 1: Prepare Your Data

Create a CSV file with your participant information:

```csv
subject_id,session_id,dicom_directory
001,baseline,/path/to/dicoms/sub-001/ses-baseline
001,followup,/path/to/dicoms/sub-001/ses-followup
002,baseline,/path/to/dicoms/sub-002/ses-baseline
```

## Step 2: Convert DICOM to BIDS

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /path/to/output/bids \
    --heuristic /path/to/your_heuristic.py
```

This command will:
- Convert DICOM files to BIDS format using HeuDiConv
- Automatically update fieldmap IntendedFor fields
- Create a valid BIDS dataset ready for analysis

### Example Heuristic

Create a simple heuristic file (`heuristic.py`):

```python
import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where"""
    
    # Define templates for different scan types
    t1w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w')
    func_task_rest = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-rest_bold')
    fmap_magnitude = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_magnitude')
    fmap_phasediff = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phasediff')
    
    info = {t1w: [], func_task_rest: [], fmap_magnitude: [], fmap_phasediff: []}
    
    for s in seqinfo:
        if 'T1' in s.protocol_name:
            info[t1w] = [s.series_id]
        elif 'rest' in s.protocol_name.lower():
            info[func_task_rest].append(s.series_id)
        elif 'fieldmap' in s.protocol_name.lower():
            if 'magnitude' in s.protocol_name.lower():
                info[fmap_magnitude].append(s.series_id)
            elif 'phase' in s.protocol_name.lower():
                info[fmap_phasediff].append(s.series_id)
    
    return info
```

## Step 3: Run fMRIPrep Preprocessing

Once you have a BIDS dataset, run fMRIPrep preprocessing:

```bash
yyprep fmriprep /path/to/bids /path/to/output participant \
    --participant-label 001 002 \
    --output-spaces MNI152NLin2009cAsym:res-2 \
    --fs-license-file /path/to/freesurfer/license.txt
```

## Step 4: Complete Pipeline (Optional)

You can also run both steps in sequence or use the Python API:

### Python API Example

```python
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for
from yyprep.fmriprep.interface import create_fmriprep_workflow

# Step 1: Convert DICOM to BIDS
df = pd.read_csv('participants.csv')
convert_dicom_to_bids(
    df=df,
    bids_dir='/path/to/bids',
    heuristic='/path/to/heuristic.py',
    heudiconv_template="heudiconv -d '{dicom_directory}' -s {subject_id} -ss {session_id} -o {output_directory} -f {heuristic} -c dcm2niix"
)

# Step 2: Update fieldmaps
update_intended_for('/path/to/bids', df)

# Step 3: Run fMRIPrep
workflow = create_fmriprep_workflow(
    bids_dir='/path/to/bids',
    output_dir='/path/to/fmriprep_output',
    participant_label=['001', '002'],
    output_spaces=['MNI152NLin2009cAsym:res-2'],
    fs_license_file='/path/to/freesurfer/license.txt'
)
result = workflow.run()
```

## Next Steps

- Learn more about [DICOM to BIDS conversion](dicom2bids.md)
- Explore [fMRIPrep integration options](fmriprep.md)
- Check out the [complete CLI reference](cli.md)
- Browse [example notebooks and scripts](https://github.com/GalKepler/yyprep/tree/main/examples)

## Common Issues

### Docker Permission Issues
If you encounter Docker permission issues:

```bash
sudo usermod -aG docker $USER
# Then log out and log back in
```

### Memory Issues
For large datasets, increase Docker memory limits:

```bash
# Increase work directory space
yyprep fmriprep /path/to/bids /path/to/output participant \
    --work-dir /path/to/large/work/dir \
    --mem-mb 16000
```

### FreeSurfer License
Download a FreeSurfer license from: https://surfer.nmr.mgh.harvard.edu/registration.html
