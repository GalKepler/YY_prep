# Python API Reference

This page provides comprehensive documentation for using yyprep's Python API.

## Overview

The yyprep Python API provides programmatic access to:

- **DICOM to BIDS conversion** functions
- **fMRIPrep preprocessing** interfaces  
- **Workflow management** utilities
- **Integration with nipype** pipelines

## Installation

```python
pip install yyprep
```

## Basic Usage

```python
import yyprep
import pandas as pd

# Import specific modules
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for
from yyprep.fmriprep.interface import create_fmriprep_workflow
```

## DICOM to BIDS API

### convert_dicom_to_bids()

Convert DICOM files to BIDS format using HeuDiConv.

```python
from yyprep.dicom2bids.convert import convert_dicom_to_bids

convert_dicom_to_bids(
    df,
    bids_dir,
    heuristic,
    heudiconv_template=None,
    overwrite=False,
    dry_run=False
)
```

#### Parameters

**df** : pandas.DataFrame
: DataFrame with participant information containing columns:
  - `subject_id`: Subject identifier (without 'sub-' prefix)
  - `session_id`: Session identifier (without 'ses-' prefix)
  - `dicom_directory`: Path to DICOM files

**bids_dir** : str or Path
: Root output directory for BIDS dataset

**heuristic** : str or Path
: Path to heuristic Python file for HeuDiConv

**heudiconv_template** : str, optional
: Template for HeuDiConv command. Default uses standard template.

**overwrite** : bool, default=False
: Whether to overwrite existing files

**dry_run** : bool, default=False
: If True, print commands without executing

#### Returns

None

#### Example

```python
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids

# Load participant data
df = pd.DataFrame({
    'subject_id': ['001', '002'],
    'session_id': ['baseline', 'baseline'],
    'dicom_directory': ['/data/sub-001/ses-baseline', '/data/sub-002/ses-baseline']
})

# Convert to BIDS
convert_dicom_to_bids(
    df=df,
    bids_dir='/output/bids',
    heuristic='heuristic.py',
    overwrite=False
)
```

### update_intended_for()

Update fieldmap IntendedFor fields to reference functional scans.

```python
from yyprep.dicom2bids.intended_for import update_intended_for

update_intended_for(bids_dir, participants_df)
```

#### Parameters

**bids_dir** : str or Path
: Path to BIDS dataset directory

**participants_df** : pandas.DataFrame
: DataFrame with participant information

#### Returns

None

#### Example

```python
from yyprep.dicom2bids.intended_for import update_intended_for

# Update IntendedFor fields
update_intended_for('/output/bids', df)
```

## fMRIPrep API

### create_fmriprep_workflow()

Create an fMRIPrep workflow for preprocessing BIDS data.

```python
from yyprep.fmriprep.interface import create_fmriprep_workflow

workflow = create_fmriprep_workflow(
    bids_dir,
    output_dir,
    participant_label=None,
    session_id=None,
    task_id=None,
    output_spaces=None,
    fs_license_file=None,
    work_dir=None,
    mem_mb=None,
    omp_nthreads=None,
    n_cpus=None,
    **kwargs
)
```

#### Parameters

**bids_dir** : str or Path
: Path to BIDS dataset directory

**output_dir** : str or Path  
: Path to output directory for derivatives

**participant_label** : list of str, optional
: List of participant identifiers to process

**session_id** : list of str, optional
: List of session identifiers to process

**task_id** : list of str, optional
: List of task identifiers to process

**output_spaces** : list of str, optional
: List of output spaces (e.g., ['MNI152NLin2009cAsym', 'T1w'])

**fs_license_file** : str or Path, optional
: Path to FreeSurfer license file

**work_dir** : str or Path, optional
: Working directory for intermediate files

**mem_mb** : int, optional
: Maximum memory usage in MB

**omp_nthreads** : int, optional
: Number of OpenMP threads

**n_cpus** : int, optional
: Total number of CPU cores

**Additional Parameters:**

- `skull_strip_template` : str
- `skull_strip_fixed_seed` : bool
- `use_aroma` : bool
- `use_syn_sdc` : bool
- `force_syn` : bool
- `force_bbr` : bool
- `ignore` : list of str
- `bids_filter_file` : str or Path
- `dummy_scans` : int
- `random_seed` : int
- `low_mem` : bool
- `output_layout` : str
- `write_graph` : bool
- `stop_on_first_crash` : bool
- `verbose_count` : int

#### Returns

**workflow** : nipype.pipeline.engine.Workflow
: Configured fMRIPrep workflow ready for execution

#### Example

```python
from yyprep.fmriprep.interface import create_fmriprep_workflow

# Create workflow
workflow = create_fmriprep_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    participant_label=['001', '002'],
    output_spaces=['MNI152NLin2009cAsym:res-2', 'T1w'],
    fs_license_file='/opt/freesurfer/license.txt',
    work_dir='/tmp/work',
    mem_mb=16000,
    omp_nthreads=8,
    n_cpus=12
)

# Run workflow
result = workflow.run()
```

### FMRIPrepInterface

Low-level nipype interface for fMRIPrep.

```python
from yyprep.fmriprep.interface import FMRIPrepInterface
from nipype import Node

# Create interface node
fmriprep_node = Node(FMRIPrepInterface(), name='fmriprep')

# Set inputs
fmriprep_node.inputs.bids_dir = '/data/bids'
fmriprep_node.inputs.output_dir = '/data/derivatives'
fmriprep_node.inputs.participant_label = ['001', '002']
fmriprep_node.inputs.fs_license_file = '/opt/freesurfer/license.txt'

# Run node
result = fmriprep_node.run()
```

#### Input Specification

The `FMRIPrepInterface` accepts all fMRIPrep command-line options as inputs:

```python
# Required inputs
fmriprep_node.inputs.bids_dir = '/data/bids'
fmriprep_node.inputs.output_dir = '/data/derivatives'

# Optional inputs
fmriprep_node.inputs.participant_label = ['001', '002']
fmriprep_node.inputs.session_id = ['baseline', 'followup']
fmriprep_node.inputs.task_id = ['rest', 'nback']
fmriprep_node.inputs.output_spaces = ['MNI152NLin2009cAsym:res-2']
fmriprep_node.inputs.fs_license_file = '/opt/freesurfer/license.txt'
fmriprep_node.inputs.work_dir = '/tmp/work'
fmriprep_node.inputs.mem_mb = 16000
fmriprep_node.inputs.omp_nthreads = 8
fmriprep_node.inputs.n_cpus = 12
fmriprep_node.inputs.low_mem = True
fmriprep_node.inputs.use_aroma = True
fmriprep_node.inputs.skull_strip_template = 'OASIS30ANTs'
fmriprep_node.inputs.bids_filter_file = '/path/to/filter.json'
```

## Complete Workflow Examples

### Basic DICOM to fMRIPrep Pipeline

```python
import pandas as pd
from pathlib import Path
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for
from yyprep.fmriprep.interface import create_fmriprep_workflow

def full_preprocessing_pipeline(participants_csv, bids_dir, heuristic, 
                               output_dir, fs_license_file):
    """Complete preprocessing pipeline from DICOM to fMRIPrep."""
    
    # Step 1: Load participant data
    df = pd.read_csv(participants_csv)
    
    # Step 2: Convert DICOM to BIDS
    print("Converting DICOM to BIDS...")
    convert_dicom_to_bids(
        df=df,
        bids_dir=bids_dir,
        heuristic=heuristic
    )
    
    # Step 3: Update fieldmap IntendedFor
    print("Updating fieldmap IntendedFor...")
    update_intended_for(bids_dir, df)
    
    # Step 4: Create fMRIPrep workflow
    print("Creating fMRIPrep workflow...")
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=output_dir,
        participant_label=df['subject_id'].unique().tolist(),
        output_spaces=['MNI152NLin2009cAsym:res-2', 'T1w'],
        fs_license_file=fs_license_file,
        use_aroma=True
    )
    
    # Step 5: Run fMRIPrep
    print("Running fMRIPrep...")
    result = workflow.run()
    
    print(f"Pipeline completed with return code: {result.returncode}")
    return result

# Usage
result = full_preprocessing_pipeline(
    participants_csv='participants.csv',
    bids_dir='/data/bids',
    heuristic='heuristic.py',
    output_dir='/data/derivatives',
    fs_license_file='/opt/freesurfer/license.txt'
)
```

### Advanced Nipype Integration

```python
from nipype import Workflow, Node, Function
from yyprep.fmriprep.interface import FMRIPrepInterface

def create_custom_preprocessing_workflow(bids_dir, output_dir, work_dir):
    """Create custom workflow with additional processing steps."""
    
    # Create main workflow
    workflow = Workflow(name='custom_preprocessing', base_dir=work_dir)
    
    # Add fMRIPrep node
    fmriprep_node = Node(
        FMRIPrepInterface(),
        name='fmriprep'
    )
    fmriprep_node.inputs.bids_dir = bids_dir
    fmriprep_node.inputs.output_dir = output_dir
    fmriprep_node.inputs.participant_label = ['001', '002']
    fmriprep_node.inputs.fs_license_file = '/opt/freesurfer/license.txt'
    
    # Add custom post-processing function
    def post_process(fmriprep_dir):
        """Custom post-processing function."""
        print(f"Post-processing fMRIPrep output: {fmriprep_dir}")
        # Add custom processing here
        return fmriprep_dir
    
    post_process_node = Node(
        Function(
            input_names=['fmriprep_dir'],
            output_names=['processed_dir'],
            function=post_process
        ),
        name='post_process'
    )
    
    # Connect nodes
    workflow.connect([
        (fmriprep_node, post_process_node, [('output_dir', 'fmriprep_dir')])
    ])
    
    return workflow

# Create and run workflow
workflow = create_custom_preprocessing_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    work_dir='/tmp/work'
)
workflow.run()
```

### Batch Processing

```python
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from yyprep.fmriprep.interface import create_fmriprep_workflow

def process_subject(subject_id, bids_dir, output_dir, fs_license_file):
    """Process a single subject with fMRIPrep."""
    
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=output_dir,
        participant_label=[subject_id],
        fs_license_file=fs_license_file,
        output_spaces=['MNI152NLin2009cAsym:res-2']
    )
    
    result = workflow.run()
    return subject_id, result.returncode

def batch_process_subjects(subject_list, bids_dir, output_dir, 
                          fs_license_file, max_workers=4):
    """Process multiple subjects in parallel."""
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_subject, 
                subject_id, 
                bids_dir, 
                output_dir, 
                fs_license_file
            )
            for subject_id in subject_list
        ]
        
        results = []
        for future in futures:
            subject_id, return_code = future.result()
            results.append({'subject': subject_id, 'return_code': return_code})
            print(f"Subject {subject_id} completed with code {return_code}")
    
    return results

# Usage
subject_list = ['001', '002', '003', '004']
results = batch_process_subjects(
    subject_list=subject_list,
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    fs_license_file='/opt/freesurfer/license.txt',
    max_workers=2
)
```

## Error Handling

### Robust Processing with Error Handling

```python
import logging
from pathlib import Path
from yyprep.fmriprep.interface import create_fmriprep_workflow

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_fmriprep_processing(bids_dir, output_dir, participant_label, 
                              fs_license_file, max_retries=3):
    """Run fMRIPrep with error handling and retries."""
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            
            workflow = create_fmriprep_workflow(
                bids_dir=bids_dir,
                output_dir=output_dir,
                participant_label=participant_label,
                fs_license_file=fs_license_file,
                stop_on_first_crash=True
            )
            
            result = workflow.run()
            
            if result.returncode == 0:
                logger.info("fMRIPrep completed successfully")
                return result
            else:
                logger.warning(f"fMRIPrep failed with return code {result.returncode}")
                
        except Exception as e:
            logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
            
            if attempt == max_retries - 1:
                logger.error("All attempts failed")
                raise
            else:
                logger.info("Retrying...")

# Usage
try:
    result = robust_fmriprep_processing(
        bids_dir='/data/bids',
        output_dir='/data/derivatives',
        participant_label=['001'],
        fs_license_file='/opt/freesurfer/license.txt'
    )
except Exception as e:
    print(f"Processing failed: {e}")
```

## Utilities

### BIDS Dataset Validation

```python
from pathlib import Path
import json

def validate_bids_dataset(bids_dir):
    """Basic BIDS dataset validation."""
    
    bids_path = Path(bids_dir)
    
    # Check required files
    required_files = [
        'dataset_description.json',
        'participants.tsv'
    ]
    
    missing_files = []
    for file in required_files:
        if not (bids_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        raise ValueError(f"Missing required BIDS files: {missing_files}")
    
    # Check dataset description
    with open(bids_path / 'dataset_description.json') as f:
        dataset_desc = json.load(f)
    
    required_fields = ['Name', 'BIDSVersion']
    missing_fields = [field for field in required_fields 
                     if field not in dataset_desc]
    
    if missing_fields:
        raise ValueError(f"Missing dataset_description.json fields: {missing_fields}")
    
    print(f"BIDS dataset validation passed: {bids_dir}")
    return True

# Usage
validate_bids_dataset('/data/bids')
```

### Progress Monitoring

```python
import time
from pathlib import Path

def monitor_fmriprep_progress(output_dir, participant_labels, 
                             check_interval=300):
    """Monitor fMRIPrep progress by checking output files."""
    
    output_path = Path(output_dir)
    
    while True:
        completed = []
        for subject in participant_labels:
            # Check for subject HTML report
            report_file = output_path / f"sub-{subject}.html"
            if report_file.exists():
                completed.append(subject)
        
        print(f"Completed subjects: {completed}")
        print(f"Remaining: {set(participant_labels) - set(completed)}")
        
        if len(completed) == len(participant_labels):
            print("All subjects completed!")
            break
        
        time.sleep(check_interval)

# Usage (run in separate thread/process)
monitor_fmriprep_progress(
    output_dir='/data/derivatives',
    participant_labels=['001', '002', '003'],
    check_interval=300  # Check every 5 minutes
)
```

## Best Practices

### Resource Management

```python
import psutil
from yyprep.fmriprep.interface import create_fmriprep_workflow

def auto_configure_resources():
    """Automatically configure fMRIPrep resources based on system."""
    
    # Get system information
    total_memory = psutil.virtual_memory().total // (1024**3)  # GB
    cpu_count = psutil.cpu_count()
    
    # Configure based on available resources
    mem_mb = int(total_memory * 0.8 * 1024)  # Use 80% of RAM
    n_cpus = max(1, cpu_count - 2)  # Leave 2 cores free
    omp_nthreads = max(1, n_cpus // 2)  # Half of CPUs for OpenMP
    
    return {
        'mem_mb': mem_mb,
        'n_cpus': n_cpus,
        'omp_nthreads': omp_nthreads
    }

# Usage
resources = auto_configure_resources()
print(f"Recommended resources: {resources}")

workflow = create_fmriprep_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    participant_label=['001'],
    fs_license_file='/opt/freesurfer/license.txt',
    **resources
)
```

## API Reference Summary

### Core Functions

| Function | Module | Purpose |
|----------|--------|---------|
| `convert_dicom_to_bids()` | `yyprep.dicom2bids.convert` | Convert DICOM to BIDS |
| `update_intended_for()` | `yyprep.dicom2bids.intended_for` | Update fieldmap IntendedFor |
| `create_fmriprep_workflow()` | `yyprep.fmriprep.interface` | Create fMRIPrep workflow |

### Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `FMRIPrepInterface` | `yyprep.fmriprep.interface` | Nipype interface for fMRIPrep |
| `FMRIPrepInputSpec` | `yyprep.fmriprep.interface` | Input specification for fMRIPrep |

For more examples and advanced usage, see the [examples directory](https://github.com/GalKepler/yyprep/tree/main/examples) in the GitHub repository.
