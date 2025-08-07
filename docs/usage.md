# Usage Guide

This guide covers the main use cases and workflows for yyprep.

## Overview

yyprep supports two main workflows:

1. **DICOM to BIDS conversion** - Convert raw DICOM files to BIDS format
2. **fMRIPrep preprocessing** - Preprocess BIDS data with fMRIPrep
3. **Complete pipeline** - End-to-end processing from DICOM to preprocessed data

## Workflow 1: DICOM to BIDS Conversion

### Step 1: Prepare Your Data

Organize your DICOM files and create a participant CSV file:

```csv
subject_id,session_id,dicom_directory
001,baseline,/data/raw/sub-001/ses-baseline
001,followup,/data/raw/sub-001/ses-followup
002,baseline,/data/raw/sub-002/ses-baseline
```

### Step 2: Create a Heuristic

Define how DICOM series map to BIDS filenames:

```python
# heuristic.py
def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template.format(**locals())

def infotodict(seqinfo):
    t1w = create_key('sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w')
    func_rest = create_key('sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-rest_bold')
    
    info = {t1w: [], func_rest: []}
    
    for s in seqinfo:
        if 't1' in s.protocol_name.lower():
            info[t1w].append(s.series_id)
        elif 'rest' in s.protocol_name.lower():
            info[func_rest].append(s.series_id)
    
    return info
```

### Step 3: Run Conversion

```bash
yyprep dicom2bids participants.csv \
    --bids-dir /data/bids \
    --heuristic heuristic.py
```

Or using Python:

```python
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for

df = pd.read_csv('participants.csv')

convert_dicom_to_bids(
    df=df,
    bids_dir='/data/bids',
    heuristic='heuristic.py'
)

update_intended_for('/data/bids', df)
```

## Workflow 2: fMRIPrep Preprocessing

### Prerequisites

- Valid BIDS dataset
- FreeSurfer license file
- Docker installed and running

### Basic fMRIPrep Run

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 \
    --fs-license-file /path/to/license.txt
```

### Advanced Configuration

```bash
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 \
    --output-spaces MNI152NLin2009cAsym:res-2 T1w \
    --fs-license-file /path/to/license.txt \
    --work-dir /tmp/fmriprep_work \
    --mem-mb 16000 \
    --omp-nthreads 8 \
    --n-cpus 12 \
    --use-aroma
```

### Python API

```python
from yyprep.fmriprep.interface import create_fmriprep_workflow

workflow = create_fmriprep_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    participant_label=['001', '002'],
    output_spaces=['MNI152NLin2009cAsym:res-2'],
    fs_license_file='/path/to/license.txt',
    use_aroma=True
)

result = workflow.run()
```

## Workflow 3: Complete Pipeline

### Command Line

```bash
# Step 1: Convert DICOM to BIDS
yyprep dicom2bids participants.csv \
    --bids-dir /data/bids \
    --heuristic heuristic.py

# Step 2: Run fMRIPrep
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label 001 002 \
    --fs-license-file /path/to/license.txt
```

### Python Script

```python
import pandas as pd
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for
from yyprep.fmriprep.interface import create_fmriprep_workflow

def complete_pipeline(participants_csv, bids_dir, heuristic, 
                     output_dir, fs_license_file):
    # Load data
    df = pd.read_csv(participants_csv)
    
    # Convert DICOM to BIDS
    convert_dicom_to_bids(df, bids_dir, heuristic)
    update_intended_for(bids_dir, df)
    
    # Run fMRIPrep
    subjects = df['subject_id'].unique().tolist()
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=output_dir,
        participant_label=subjects,
        fs_license_file=fs_license_file
    )
    
    return workflow.run()

# Run complete pipeline
result = complete_pipeline(
    participants_csv='participants.csv',
    bids_dir='/data/bids',
    heuristic='heuristic.py',
    output_dir='/data/derivatives',
    fs_license_file='/path/to/license.txt'
)
```

## Common Use Cases

### Research Lab Setup

For a typical research lab processing multiple studies:

```python
# lab_preprocessing.py
import pandas as pd
from pathlib import Path
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.fmriprep.interface import create_fmriprep_workflow

def process_study(study_name, participants_csv, heuristic):
    """Process a complete study from DICOM to fMRIPrep."""
    
    # Setup paths
    study_dir = Path(f'/lab/studies/{study_name}')
    bids_dir = study_dir / 'bids'
    derivatives_dir = study_dir / 'derivatives'
    
    # Load participants
    df = pd.read_csv(participants_csv)
    
    # Convert to BIDS
    convert_dicom_to_bids(df, bids_dir, heuristic)
    
    # Run fMRIPrep
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=derivatives_dir,
        participant_label=df['subject_id'].unique().tolist(),
        output_spaces=['MNI152NLin2009cAsym:res-2'],
        fs_license_file='/lab/software/freesurfer/license.txt',
        use_aroma=True
    )
    
    return workflow.run()

# Process multiple studies
studies = [
    ('memory_study', 'memory_participants.csv', 'memory_heuristic.py'),
    ('attention_study', 'attention_participants.csv', 'attention_heuristic.py')
]

for study_name, csv_file, heuristic in studies:
    print(f"Processing {study_name}...")
    result = process_study(study_name, csv_file, heuristic)
    print(f"Study {study_name} completed with code {result.returncode}")
```

### High-Performance Computing

For processing on HPC clusters:

```bash
#!/bin/bash
#SBATCH --job-name=yyprep
#SBATCH --array=1-10
#SBATCH --cpus-per-task=12
#SBATCH --mem=32G
#SBATCH --time=24:00:00

# Get subject ID from array
SUBJECTS=(001 002 003 004 005 006 007 008 009 010)
SUBJECT=${SUBJECTS[$SLURM_ARRAY_TASK_ID-1]}

# Run fMRIPrep for single subject
yyprep fmriprep /data/bids /data/derivatives participant \
    --participant-label $SUBJECT \
    --fs-license-file $HOME/license.txt \
    --work-dir $SCRATCH/fmriprep_work_$SUBJECT \
    --n-cpus $SLURM_CPUS_PER_TASK \
    --mem-mb 32000
```

### Quality Control Workflow

```python
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

def quality_control_pipeline(derivatives_dir):
    """Generate QC reports for fMRIPrep outputs."""
    
    derivatives_path = Path(derivatives_dir)
    subjects = [d.name for d in derivatives_path.iterdir() 
               if d.is_dir() and d.name.startswith('sub-')]
    
    qc_data = []
    
    for subject in subjects:
        subject_dir = derivatives_path / subject
        
        # Check for required outputs
        html_report = derivatives_path / f"{subject}.html"
        confounds_files = list(subject_dir.glob('func/*confounds*.tsv'))
        
        # Load motion parameters
        for confounds_file in confounds_files:
            confounds = pd.read_csv(confounds_file, sep='\t')
            
            # Calculate motion metrics
            trans_mean = confounds[['trans_x', 'trans_y', 'trans_z']].abs().mean().mean()
            rot_mean = confounds[['rot_x', 'rot_y', 'rot_z']].abs().mean().mean()
            
            qc_data.append({
                'subject': subject,
                'task': confounds_file.name.split('_task-')[1].split('_')[0],
                'html_report_exists': html_report.exists(),
                'mean_translation': trans_mean,
                'mean_rotation': rot_mean
            })
    
    # Create QC dataframe
    qc_df = pd.DataFrame(qc_data)
    
    # Generate QC plots
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    qc_df.boxplot(column='mean_translation', ax=axes[0])
    axes[0].set_title('Translation Parameters')
    axes[0].set_ylabel('mm')
    
    qc_df.boxplot(column='mean_rotation', ax=axes[1])
    axes[1].set_title('Rotation Parameters')
    axes[1].set_ylabel('radians')
    
    plt.tight_layout()
    plt.savefig(derivatives_path / 'qc_motion_summary.png')
    
    # Save QC data
    qc_df.to_csv(derivatives_path / 'qc_summary.csv', index=False)
    
    return qc_df

# Run QC
qc_results = quality_control_pipeline('/data/derivatives')
print(qc_results.head())
```

## Best Practices

### 1. Data Organization

```
/lab/studies/study_name/
├── raw/                    # Raw DICOM files
│   ├── sub-001/
│   └── sub-002/
├── bids/                   # BIDS dataset
├── derivatives/            # fMRIPrep outputs
├── code/                   # Analysis scripts
│   ├── heuristic.py
│   └── participants.csv
└── work/                   # Temporary processing files
```

### 2. Resource Management

```python
# Check system resources before processing
import psutil

def check_resources():
    memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()
    
    print(f"Available memory: {memory_gb:.1f} GB")
    print(f"CPU cores: {cpu_count}")
    
    # Recommend settings
    recommended_mem = int(memory_gb * 0.8 * 1024)  # 80% of RAM in MB
    recommended_cpus = max(1, cpu_count - 2)  # Leave 2 cores free
    
    print(f"Recommended --mem-mb: {recommended_mem}")
    print(f"Recommended --n-cpus: {recommended_cpus}")

check_resources()
```

### 3. Error Handling

```python
import logging

def robust_processing(func, *args, max_retries=3, **kwargs):
    """Run function with retry logic."""
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            else:
                logging.info("Retrying...")

# Usage
result = robust_processing(
    create_fmriprep_workflow,
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    participant_label=['001'],
    fs_license_file='/path/to/license.txt'
).run()
```

### 4. Progress Monitoring

```python
import time
from pathlib import Path

def monitor_progress(output_dir, expected_subjects):
    """Monitor fMRIPrep progress."""
    
    output_path = Path(output_dir)
    
    while True:
        # Check completed subjects
        completed = []
        for subject in expected_subjects:
            report_file = output_path / f"sub-{subject}.html"
            if report_file.exists():
                completed.append(subject)
        
        progress = len(completed) / len(expected_subjects) * 100
        print(f"Progress: {progress:.1f}% ({len(completed)}/{len(expected_subjects)})")
        
        if len(completed) == len(expected_subjects):
            print("All subjects completed!")
            break
        
        time.sleep(300)  # Check every 5 minutes

# Start monitoring in background
import threading
monitor_thread = threading.Thread(
    target=monitor_progress,
    args=('/data/derivatives', ['001', '002', '003'])
)
monitor_thread.start()
```

## Troubleshooting

### Common Issues

1. **Docker permission errors**
   ```bash
   sudo usermod -aG docker $USER
   # Then log out and back in
   ```

2. **Memory errors**
   ```bash
   yyprep fmriprep /data/bids /data/derivatives participant \
       --low-mem \
       --mem-mb 8000
   ```

3. **BIDS validation errors**
   ```bash
   bids-validator /data/bids
   ```

4. **HeuDiConv issues**
   - Check heuristic syntax
   - Verify DICOM paths exist
   - Test with single subject first

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).

## Next Steps

- Explore [advanced workflows](workflows.md)
- Read the complete [CLI reference](cli.md)
- Check out [example notebooks](https://github.com/GalKepler/yyprep/tree/main/examples)
