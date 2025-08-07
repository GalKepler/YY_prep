# DICOM to BIDS Conversion

This guide covers converting DICOM files to BIDS (Brain Imaging Data Structure) format using yyprep.

## Overview

The DICOM to BIDS conversion in yyprep:

1. **Uses HeuDiConv** for the core conversion process
2. **Requires custom heuristics** to map DICOM series to BIDS filenames
3. **Automatically handles fieldmaps** by updating IntendedFor fields
4. **Supports batch processing** of multiple subjects and sessions

## Input Requirements

### Participant CSV File

Create a CSV file with columns for subject information:

```csv
subject_id,session_id,dicom_directory
001,baseline,/data/dicoms/sub-001/ses-baseline
001,followup,/data/dicoms/sub-001/ses-followup
002,baseline,/data/dicoms/sub-002/ses-baseline
002,followup,/data/dicoms/sub-002/ses-followup
```

**Required columns:**
- `subject_id`: BIDS subject identifier (without 'sub-' prefix)
- `session_id`: BIDS session identifier (without 'ses-' prefix)  
- `dicom_directory`: Path to directory containing DICOM files

### DICOM Directory Structure

Your DICOM directories should contain the raw DICOM files:

```
/data/dicoms/sub-001/ses-baseline/
├── series001_localizer/
├── series002_t1_mprage/
├── series003_rest_bold/
├── series004_fieldmap_mag/
└── series005_fieldmap_phase/
```

## Creating Heuristics

Heuristics define how DICOM series map to BIDS filenames. Here's a complete example:

```python
# heuristic.py
import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    """Create a key for the template"""
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
    
    Parameters
    ----------
    seqinfo : list
        List of sequence info objects from dcmstack
    
    Returns
    -------
    dict
        Dictionary mapping BIDS keys to series IDs
    """
    
    # BIDS templates for different data types
    t1w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w')
    t2w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T2w')
    
    # Functional scans
    func_rest = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-rest_run-{item:02d}_bold')
    func_task = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task}_run-{item:02d}_bold')
    
    # Fieldmaps
    fmap_magnitude = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_magnitude{item}')
    fmap_phasediff = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phasediff')
    fmap_phase1 = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phase1')
    fmap_phase2 = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phase2')
    
    # Diffusion
    dwi = create_key('sub-{subject}/ses-{session}/dwi/sub-{subject}_ses-{session}_dwi')
    
    # Initialize info dictionary
    info = {
        t1w: [], t2w: [], func_rest: [], func_task: [],
        fmap_magnitude: [], fmap_phasediff: [], fmap_phase1: [], fmap_phase2: [],
        dwi: []
    }
    
    # Process each sequence
    for idx, s in enumerate(seqinfo):
        protocol = s.protocol_name.lower()
        
        # Anatomical scans
        if 't1' in protocol and 'mprage' in protocol:
            info[t1w].append(s.series_id)
        elif 't2' in protocol:
            info[t2w].append(s.series_id)
        
        # Functional scans
        elif 'rest' in protocol and 'bold' in protocol:
            info[func_rest].append(s.series_id)
        elif 'task' in protocol and 'bold' in protocol:
            # Extract task name from protocol
            task_name = extract_task_name(protocol)
            if task_name:
                task_key = create_key(f'sub-{{subject}}/ses-{{session}}/func/sub-{{subject}}_ses-{{session}}_task-{task_name}_run-{{item:02d}}_bold')
                if task_key not in info:
                    info[task_key] = []
                info[task_key].append(s.series_id)
        
        # Fieldmaps
        elif 'fieldmap' in protocol or 'fmap' in protocol:
            if 'magnitude' in protocol:
                info[fmap_magnitude].append(s.series_id)
            elif 'phasediff' in protocol:
                info[fmap_phasediff].append(s.series_id)
            elif 'phase1' in protocol:
                info[fmap_phase1].append(s.series_id)
            elif 'phase2' in protocol:
                info[fmap_phase2].append(s.series_id)
        
        # Diffusion
        elif 'dwi' in protocol or 'dti' in protocol:
            info[dwi].append(s.series_id)
    
    return info

def extract_task_name(protocol_name):
    """Extract task name from protocol"""
    # Custom logic to extract task name
    # Example: "task_nback_bold" -> "nback"
    parts = protocol_name.split('_')
    for i, part in enumerate(parts):
        if part == 'task' and i + 1 < len(parts):
            return parts[i + 1]
    return None
```

### Heuristic Best Practices

1. **Use descriptive protocol names** in your MRI sequences
2. **Test with a single subject** before processing batches
3. **Handle multiple runs** by using the `{item:02d}` placeholder
4. **Include all scan types** you plan to analyze
5. **Validate BIDS compliance** using the BIDS validator

## Command Line Usage

### Basic Conversion

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /path/to/output/bids \
    --heuristic /path/to/heuristic.py
```

### Advanced Options

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /path/to/output/bids \
    --heuristic /path/to/heuristic.py \
    --heudiconv-template "heudiconv -d '{dicom_directory}' -s {subject_id} -ss {session_id} -o {output_directory} -f {heuristic} -c dcm2niix --bids" \
    --overwrite \
    --skip-intendedfor \
    --dry-run
```

**Options:**
- `--heudiconv-template`: Custom HeuDiConv command template
- `--overwrite`: Allow overwriting existing files
- `--skip-intendedfor`: Skip automatic fieldmap IntendedFor updates
- `--dry-run`: Preview commands without executing

## Python API Usage

```python
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for

# Load participant data
df = pd.read_csv('participants.csv')

# Run conversion
convert_dicom_to_bids(
    df=df,
    bids_dir='/path/to/output/bids',
    heuristic='/path/to/heuristic.py',
    heudiconv_template="heudiconv -d '{dicom_directory}' -s {subject_id} -ss {session_id} -o {output_directory} -f {heuristic} -c dcm2niix --bids",
    overwrite=False,
    dry_run=False
)

# Update fieldmap IntendedFor fields
update_intended_for('/path/to/output/bids', df)
```

## Fieldmap Handling

yyprep automatically updates fieldmap `IntendedFor` fields to reference functional scans:

### Supported Fieldmap Types

1. **Magnitude + Phase Difference**: Single phasediff with magnitude image(s)
2. **Two Phase Images**: Separate phase1 and phase2 images
3. **Magnitude Only**: For distortion correction without B0 mapping

### IntendedFor Logic

The automatic IntendedFor update:
- Links fieldmaps to **functional scans in the same session**
- Uses **acquisition time proximity** when multiple fieldmaps exist
- Supports **custom matching rules** via the participant CSV

### Custom IntendedFor

Add `intended_for` column to your CSV for custom associations:

```csv
subject_id,session_id,dicom_directory,intended_for
001,baseline,/data/dicoms/sub-001/ses-baseline,"func/sub-001_ses-baseline_task-rest_bold.nii.gz"
```

## Validation

### BIDS Validator

Always validate your BIDS dataset:

```bash
# Install bids-validator
npm install -g bids-validator

# Validate dataset
bids-validator /path/to/output/bids
```

### Manual Inspection

Check key files:
- `dataset_description.json`: Dataset metadata
- `participants.tsv`: Participant information
- Anatomical files: `sub-*/ses-*/anat/*.nii.gz`
- Functional files: `sub-*/ses-*/func/*.nii.gz`
- Fieldmaps: `sub-*/ses-*/fmap/*.json` (check IntendedFor)

## Troubleshooting

### Common Issues

**HeuDiConv errors:**
- Check heuristic syntax with `python heuristic.py`
- Verify DICOM directory paths exist
- Ensure dcm2niix is installed and accessible

**Missing files:**
- Update heuristic to handle all protocol names
- Check DICOM series organization
- Use HeuDiConv's dry-run mode: `heudiconv ... --dry-run`

**IntendedFor issues:**
- Verify functional scans were converted
- Check fieldmap JSON files for proper IntendedFor arrays
- Use `--skip-intendedfor` to debug conversion separately

**BIDS validation errors:**
- Use descriptive and consistent naming in protocols
- Ensure required JSON metadata is present
- Check file naming conventions match BIDS spec

### Getting Detailed Logs

Enable verbose logging:

```bash
export HEUDICONV_LOG_LEVEL=DEBUG
yyprep dicom2bids participants.csv --bids-dir /path/to/bids --heuristic heuristic.py
```

## Next Steps

- Learn about [fMRIPrep integration](fmriprep.md) for preprocessing your BIDS data
- Explore [custom heuristics](heuristics.md) for complex acquisition protocols
- Check [example workflows](workflows.md) for complete pipelines
