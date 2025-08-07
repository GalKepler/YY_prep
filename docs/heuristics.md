# Custom Heuristics Guide

This guide covers creating and customizing heuristics for DICOM to BIDS conversion using HeuDiConv.

## Overview

Heuristics are Python files that define how DICOM series should be mapped to BIDS filenames. They are the core component that tells HeuDiConv which DICOM series corresponds to which type of scan (T1w, BOLD, fieldmaps, etc.).

## Basic Heuristic Structure

Every heuristic file must contain two main functions:

```python
def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    \"\"\"Create a key for the template\"\"\"
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    \"\"\"Heuristic evaluator for determining which runs belong where\"\"\"
    # Your logic here
    return info
```

## Understanding DICOM Sequence Information

The `seqinfo` parameter contains information about each DICOM series. Key attributes include:

```python
def infotodict(seqinfo):
    # Print sequence information for debugging
    for idx, s in enumerate(seqinfo):
        print(f\"Series {idx}:\")
        print(f\"  Protocol: {s.protocol_name}\")
        print(f\"  Series description: {s.series_description}\")
        print(f\"  Sequence name: {s.sequence_name}\")
        print(f\"  Series ID: {s.series_id}\")
        print(f\"  Images in series: {s.nimages}\")
        print(f\"  TR: {s.TR}\")
        print(f\"  TE: {s.TE}\")
        print(f\"  Dimensions: {s.dim1} x {s.dim2} x {s.dim3}\")
        print()
```

## Simple Heuristic Example

Here's a basic heuristic for a simple study design:

```python
# simple_heuristic.py
import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    \"\"\"Simple heuristic for basic study design.\"\"\"
    
    # Define BIDS templates
    t1w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w')
    func_rest = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-rest_bold')
    
    # Initialize info dictionary
    info = {t1w: [], func_rest: []}
    
    # Process each sequence
    for s in seqinfo:
        protocol = s.protocol_name.lower()
        
        if 't1' in protocol and 'mprage' in protocol:
            info[t1w].append(s.series_id)
        elif 'rest' in protocol and 'bold' in protocol:
            info[func_rest].append(s.series_id)
    
    return info
```

## Comprehensive Heuristic Example

Here's a more comprehensive heuristic that handles multiple scan types:

```python
# comprehensive_heuristic.py
import os
import re

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    \"\"\"Comprehensive heuristic for multi-modal neuroimaging study.\"\"\"
    
    # Anatomical templates
    t1w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w')
    t2w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T2w')
    flair = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR')
    
    # Functional templates (with run numbers)
    func_rest = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-rest_run-{item:02d}_bold')
    func_nback = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-nback_run-{item:02d}_bold')
    func_faces = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-faces_run-{item:02d}_bold')
    
    # Fieldmap templates
    fmap_magnitude = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_magnitude{item}')
    fmap_phasediff = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phasediff')
    fmap_phase1 = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phase1')
    fmap_phase2 = create_key('sub-{subject}/ses-{session}/fmap/sub-{subject}_ses-{session}_phase2')
    
    # Diffusion template
    dwi = create_key('sub-{subject}/ses-{session}/dwi/sub-{subject}_ses-{session}_dwi')
    
    # Perfusion template
    asl = create_key('sub-{subject}/ses-{session}/perf/sub-{subject}_ses-{session}_asl')
    
    # Initialize info dictionary
    info = {
        t1w: [], t2w: [], flair: [],
        func_rest: [], func_nback: [], func_faces: [],
        fmap_magnitude: [], fmap_phasediff: [], fmap_phase1: [], fmap_phase2: [],
        dwi: [], asl: []
    }
    
    # Process each sequence
    for idx, s in enumerate(seqinfo):
        protocol = s.protocol_name.lower()
        series_desc = s.series_description.lower()
        
        # Anatomical scans
        if ('t1' in protocol or 't1' in series_desc) and 'mprage' in protocol:
            info[t1w].append(s.series_id)
        elif ('t2' in protocol or 't2' in series_desc) and 'space' in protocol:
            info[t2w].append(s.series_id)
        elif 'flair' in protocol or 'flair' in series_desc:
            info[flair].append(s.series_id)
        
        # Functional scans
        elif 'bold' in protocol or 'bold' in series_desc:
            if 'rest' in protocol or 'rest' in series_desc:
                info[func_rest].append(s.series_id)
            elif 'nback' in protocol or 'nback' in series_desc:
                info[func_nback].append(s.series_id)
            elif 'faces' in protocol or 'faces' in series_desc:
                info[func_faces].append(s.series_id)
        
        # Fieldmaps
        elif 'fieldmap' in protocol or 'fmap' in protocol or 'gre_field_mapping' in protocol:
            if 'magnitude' in protocol or 'magnitude' in series_desc:
                info[fmap_magnitude].append(s.series_id)
            elif 'phasediff' in protocol or 'phasediff' in series_desc:
                info[fmap_phasediff].append(s.series_id)
            elif 'phase1' in protocol or 'phase1' in series_desc:
                info[fmap_phase1].append(s.series_id)
            elif 'phase2' in protocol or 'phase2' in series_desc:
                info[fmap_phase2].append(s.series_id)
        
        # Diffusion
        elif 'dwi' in protocol or 'dti' in protocol or 'diffusion' in protocol:
            info[dwi].append(s.series_id)
        
        # Arterial Spin Labeling
        elif 'asl' in protocol or 'pcasl' in protocol or 'pasl' in protocol:
            info[asl].append(s.series_id)
    
    return info
```

## Advanced Heuristic Features

### Handling Multiple Runs

For studies with multiple runs of the same task:

```python
def infotodict(seqinfo):
    # Templates with run numbers
    func_task = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task}_run-{item:02d}_bold')
    
    info = {}
    task_counts = {}
    
    for s in seqinfo:
        protocol = s.protocol_name.lower()
        
        # Extract task name
        if 'task' in protocol:
            task_match = re.search(r'task[_-](\w+)', protocol)
            if task_match:
                task_name = task_match.group(1)
                
                # Create key for this specific task
                task_key = create_key(f'sub-{{subject}}/ses-{{session}}/func/sub-{{subject}}_ses-{{session}}_task-{task_name}_run-{{item:02d}}_bold')
                
                if task_key not in info:
                    info[task_key] = []
                
                info[task_key].append(s.series_id)
    
    return info
```

### Session-Specific Logic

For studies with different protocols across sessions:

```python
def infotodict(seqinfo):
    # Get session from first sequence (assumes consistent session info)
    session = seqinfo[0].session_id if seqinfo else 'unknown'
    
    info = {}
    
    # Session-specific templates
    if session == 'baseline':
        # Baseline session includes anatomical and resting state
        t1w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w')
        func_rest = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-rest_bold')
        info = {t1w: [], func_rest: []}
        
    elif session == 'task':
        # Task session only includes functional scans
        func_nback = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-nback_bold')
        func_faces = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-faces_bold')
        info = {func_nback: [], func_faces: []}
    
    # Continue with sequence processing...
    for s in seqinfo:
        # Your logic here
        pass
    
    return info
```

### Custom Metadata Extraction

Extract additional metadata for BIDS sidecar files:

```python
def create_key(template, outtype=('nii.gz', 'json'), annotation_classes=None):
    \"\"\"Create key with JSON sidecar support\"\"\"
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    \"\"\"Heuristic with custom metadata extraction\"\"\"
    
    # Standard processing...
    info = {}
    
    # Extract custom metadata
    for s in seqinfo:
        if 'task' in s.protocol_name.lower():
            # Extract task parameters from protocol name
            if 'TE=' in s.protocol_name:
                te_match = re.search(r'TE=(\d+\.?\d*)', s.protocol_name)
                if te_match:
                    custom_te = float(te_match.group(1))
                    # Store metadata for later use
                    s.custom_metadata = {'EchoTime': custom_te}
    
    return info

def custom_callable(dcmdata, outdir):
    \"\"\"Custom function to add metadata to JSON files\"\"\"
    import json
    from pathlib import Path
    
    # Find JSON files and add custom metadata
    json_files = Path(outdir).glob('**/*.json')
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            metadata = json.load(f)
        
        # Add custom fields
        metadata['CustomProcessing'] = 'yyprep'
        metadata['ProcessingDate'] = str(pd.Timestamp.now().date())
        
        with open(json_file, 'w') as f:
            json.dump(metadata, f, indent=2)
```

## Specialized Heuristics

### Multi-Echo BOLD

For multi-echo functional data:

```python
def infotodict(seqinfo):
    \"\"\"Heuristic for multi-echo BOLD data\"\"\"
    
    # Multi-echo template
    func_multiecho = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task}_echo-{echo}_bold')
    
    info = {}
    
    for s in seqinfo:
        protocol = s.protocol_name.lower()
        
        if 'bold' in protocol and 'echo' in protocol:
            # Extract task and echo number
            task_match = re.search(r'task[_-](\w+)', protocol)
            echo_match = re.search(r'echo[_-]?(\d+)', protocol)
            
            if task_match and echo_match:
                task = task_match.group(1)
                echo = echo_match.group(1)
                
                key_template = f'sub-{{subject}}/ses-{{session}}/func/sub-{{subject}}_ses-{{session}}_task-{task}_echo-{echo}_bold'
                key = create_key(key_template)
                
                if key not in info:
                    info[key] = []
                
                info[key].append(s.series_id)
    
    return info
```

### Phase-Encoding Direction Specific

For datasets with different phase encoding directions:

```python
def infotodict(seqinfo):
    \"\"\"Heuristic handling different phase encoding directions\"\"\"
    
    # Templates for different PE directions
    func_ap = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task}_dir-AP_bold')
    func_pa = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task}_dir-PA_bold')
    
    info = {}
    
    for s in seqinfo:
        protocol = s.protocol_name.lower()
        
        if 'bold' in protocol:
            # Determine phase encoding direction
            if 'ap' in protocol or 'anteriorposterior' in protocol:
                pe_dir = 'AP'
                template = func_ap
            elif 'pa' in protocol or 'posterioranterior' in protocol:
                pe_dir = 'PA'
                template = func_pa
            else:
                continue  # Skip if PE direction unclear
            
            # Extract task
            task_match = re.search(r'task[_-](\w+)', protocol)
            if task_match:
                task = task_match.group(1)
                key_template = f'sub-{{subject}}/ses-{{session}}/func/sub-{{subject}}_ses-{{session}}_task-{task}_dir-{pe_dir}_bold'
                key = create_key(key_template)
                
                if key not in info:
                    info[key] = []
                
                info[key].append(s.series_id)
    
    return info
```

## Testing Your Heuristic

### Dry Run Testing

Always test your heuristic with HeuDiConv's dry run mode:

```bash
# Test heuristic without converting
heudiconv -d '/path/to/dicoms/{subject}' -s 001 -ss baseline \\
    -o /tmp/test_output -f your_heuristic.py --dry-run

# Check the output to see what would be created
```

### Python Testing

Test your heuristic logic directly in Python:

```python
# test_heuristic.py
import sys
sys.path.append('.')  # Add current directory to path

from your_heuristic import infotodict, create_key

# Mock sequence info for testing
class MockSeqInfo:
    def __init__(self, protocol_name, series_description, series_id):
        self.protocol_name = protocol_name
        self.series_description = series_description
        self.series_id = series_id

# Create test data
test_seqinfo = [
    MockSeqInfo('T1_MPRAGE_1mm', 'T1_MPRAGE_1mm', 2),
    MockSeqInfo('task_rest_bold', 'task_rest_bold', 5),
    MockSeqInfo('task_nback_bold', 'task_nback_bold', 8),
    MockSeqInfo('gre_field_mapping_magnitude1', 'gre_field_mapping_magnitude1', 10),
    MockSeqInfo('gre_field_mapping_phasediff', 'gre_field_mapping_phasediff', 11),
]

# Test heuristic
info = infotodict(test_seqinfo)

# Print results
for key, series_ids in info.items():
    if series_ids:  # Only print non-empty entries
        print(f\"{key}: {series_ids}\")
```

## Best Practices

### 1. Use Descriptive Protocol Names

Work with your MRI technician to use descriptive protocol names:

```
Good: task_rest_bold_2mm_TR2000
Bad: localizer_001

Good: T1_MPRAGE_1mm_sagittal
Bad: sag_t1

Good: gre_field_mapping_magnitude1
Bad: field_map_1
```

### 2. Handle Edge Cases

```python
def infotodict(seqinfo):
    info = {}
    
    for s in seqinfo:
        # Handle empty or None protocol names
        if not s.protocol_name:
            continue
            
        protocol = s.protocol_name.lower().strip()
        
        # Skip localizers and scouts
        if any(skip in protocol for skip in ['localizer', 'scout', 'calibration']):
            continue
        
        # Your main logic here
        pass
    
    return info
```

### 3. Validate BIDS Compliance

Ensure your heuristic creates BIDS-compliant filenames:

```python
def validate_bids_filename(filename):
    \"\"\"Check if filename follows BIDS conventions\"\"\"
    import re
    
    # Check for required sub- prefix
    if not filename.startswith('sub-'):
        return False, \"Missing sub- prefix\"
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', filename.replace('.nii.gz', '')):
        return False, \"Invalid characters in filename\"
    
    return True, \"Valid BIDS filename\"

# Use in your heuristic
def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    
    # Validate template creates BIDS-compliant names
    test_filename = template.format(subject='001', session='01', item=1, task='test')
    is_valid, message = validate_bids_filename(test_filename)
    
    if not is_valid:
        raise ValueError(f\"Template creates invalid BIDS filename: {message}\")
    
    return template.format(**locals())
```

### 4. Document Your Heuristic

Add comprehensive documentation:

```python
\"\"\"
Custom heuristic for Memory Study

Study Design:
- 2 sessions: baseline, followup
- Tasks: rest (2 runs), memory (3 runs), faces (1 run)
- Anatomical: T1w, T2w
- Fieldmaps: magnitude + phasediff

Protocol Naming Convention:
- Anatomical: T1_MPRAGE_1mm, T2_SPACE_1mm
- Functional: task_{taskname}_bold_run{X}
- Fieldmaps: gre_field_mapping_{magnitude1|phasediff}

Author: Your Name
Date: 2025-08-07
Version: 1.0
\"\"\"

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    # Implementation...
    pass

def infotodict(seqinfo):
    \"\"\"
    Heuristic for Memory Study DICOM to BIDS conversion.
    
    Expected protocol names:
    - T1_MPRAGE_1mm -> anat/T1w
    - T2_SPACE_1mm -> anat/T2w  
    - task_rest_bold_run1 -> func/task-rest_run-01_bold
    - task_memory_bold_run1 -> func/task-memory_run-01_bold
    - gre_field_mapping_magnitude1 -> fmap/magnitude1
    - gre_field_mapping_phasediff -> fmap/phasediff
    \"\"\"
    # Implementation...
    pass
```

## Troubleshooting Heuristics

### Common Issues

1. **No files converted**: Check protocol name matching logic
2. **Wrong file organization**: Verify BIDS template strings
3. **Missing runs**: Ensure run numbering logic is correct
4. **Fieldmap issues**: Check magnitude/phase identification

### Debugging Tips

```python
def infotodict(seqinfo):
    # Add debugging output
    print(f\"Processing {len(seqinfo)} sequences\")
    
    for i, s in enumerate(seqinfo):
        print(f\"Sequence {i}: '{s.protocol_name}' -> Series {s.series_id}\")
    
    # Your heuristic logic...
    info = {}
    
    # Print final mapping
    print(\"\\nFinal mapping:\")
    for key, series_ids in info.items():
        if series_ids:
            print(f\"  {key}: {series_ids}\")
    
    return info
```

Remember to remove debugging output before production use!

## Next Steps

- Test your heuristic with the [Quick Start Guide](quickstart.md)
- Learn about [DICOM to BIDS conversion](dicom2bids.md) 
- Explore [complete workflows](workflows.md) using your custom heuristic
