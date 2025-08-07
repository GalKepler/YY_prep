# Workflows and Examples

This guide provides comprehensive examples and workflows for using yyprep in different scenarios.

## Basic Workflows

### Workflow 1: Single Subject Processing

Process a single subject from DICOM to preprocessed data:

```python
import pandas as pd
from pathlib import Path
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.dicom2bids.intended_for import update_intended_for
from yyprep.fmriprep.interface import create_fmriprep_workflow

def process_single_subject(subject_id, session_id, dicom_dir, 
                          output_dir, heuristic, fs_license):
    \"\"\"Process a single subject from DICOM to fMRIPrep.\"\"\"
    
    # Setup paths
    bids_dir = Path(output_dir) / 'bids'
    derivatives_dir = Path(output_dir) / 'derivatives'
    
    # Create participant dataframe
    df = pd.DataFrame({
        'subject_id': [subject_id],
        'session_id': [session_id], 
        'dicom_directory': [dicom_dir]
    })
    
    # Step 1: Convert DICOM to BIDS
    print(f\"Converting subject {subject_id} DICOM to BIDS...\")
    convert_dicom_to_bids(df, bids_dir, heuristic)
    
    # Step 2: Update fieldmaps
    print(\"Updating fieldmap IntendedFor...\")
    update_intended_for(bids_dir, df)
    
    # Step 3: Run fMRIPrep
    print(f\"Running fMRIPrep for subject {subject_id}...\")
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=derivatives_dir,
        participant_label=[subject_id],
        fs_license_file=fs_license,
        output_spaces=['MNI152NLin2009cAsym:res-2'],
        use_aroma=True
    )
    
    result = workflow.run()
    print(f\"Subject {subject_id} completed with return code: {result.returncode}\")
    
    return result

# Usage
result = process_single_subject(
    subject_id='001',
    session_id='baseline',
    dicom_dir='/data/raw/sub-001/ses-baseline',
    output_dir='/data/processed',
    heuristic='heuristic.py',
    fs_license='/opt/freesurfer/license.txt'
)
```

### Workflow 2: Batch Processing

Process multiple subjects efficiently:

```python
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.fmriprep.interface import create_fmriprep_workflow

def batch_process_study(participants_csv, bids_dir, derivatives_dir, 
                       heuristic, fs_license, max_parallel=2):
    \"\"\"Process an entire study with parallel execution.\"\"\"
    
    # Load participants
    df = pd.read_csv(participants_csv)
    
    # Step 1: Convert all subjects to BIDS
    print(\"Converting all subjects to BIDS...\")
    convert_dicom_to_bids(df, bids_dir, heuristic)
    
    # Step 2: Process subjects in parallel with fMRIPrep
    subjects = df['subject_id'].unique()
    
    def process_subject(subject_id):
        \"\"\"Process single subject with fMRIPrep.\"\"\"
        try:
            workflow = create_fmriprep_workflow(
                bids_dir=bids_dir,
                output_dir=derivatives_dir,
                participant_label=[subject_id],
                fs_license_file=fs_license,
                output_spaces=['MNI152NLin2009cAsym:res-2'],
                work_dir=f'/tmp/fmriprep_work_{subject_id}',
                use_aroma=True,
                low_mem=True
            )
            result = workflow.run()
            return subject_id, result.returncode
        except Exception as e:
            return subject_id, f\"Error: {str(e)}\"
    
    # Process in parallel
    with ProcessPoolExecutor(max_workers=max_parallel) as executor:
        futures = [executor.submit(process_subject, subject) for subject in subjects]
        results = []
        
        for future in futures:
            subject_id, status = future.result()
            results.append({'subject': subject_id, 'status': status})
            print(f\"Subject {subject_id}: {status}\")
    
    return results

# Usage
results = batch_process_study(
    participants_csv='participants.csv',
    bids_dir='/data/study/bids',
    derivatives_dir='/data/study/derivatives',
    heuristic='study_heuristic.py',
    fs_license='/opt/freesurfer/license.txt',
    max_parallel=2
)
```

## Advanced Workflows

### Workflow 3: Multi-Session Longitudinal Study

Handle longitudinal data with multiple sessions:

```python
import pandas as pd
from pathlib import Path
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.fmriprep.interface import create_fmriprep_workflow

def longitudinal_study_workflow(participants_csv, study_dir, heuristic, fs_license):
    \"\"\"Process longitudinal study with multiple sessions.\"\"\"
    
    # Setup directories
    bids_dir = Path(study_dir) / 'bids'
    derivatives_dir = Path(study_dir) / 'derivatives'
    
    # Load participants
    df = pd.read_csv(participants_csv)
    
    # Convert all sessions to BIDS
    print(\"Converting all sessions to BIDS...\")
    convert_dicom_to_bids(df, bids_dir, heuristic)
    
    # Get unique subjects
    subjects = df['subject_id'].unique()
    
    # Process each subject across all sessions
    for subject in subjects:
        subject_sessions = df[df['subject_id'] == subject]['session_id'].unique()
        
        print(f\"Processing subject {subject} with sessions: {list(subject_sessions)}\")
        
        # Process all sessions for this subject together
        workflow = create_fmriprep_workflow(
            bids_dir=bids_dir,
            output_dir=derivatives_dir,
            participant_label=[subject],
            session_id=list(subject_sessions),  # Process all sessions
            fs_license_file=fs_license,
            output_spaces=['MNI152NLin2009cAsym:res-2', 'T1w'],
            use_aroma=True,
            longitudinal=True  # Enable longitudinal processing
        )
        
        result = workflow.run()
        print(f\"Subject {subject} completed: {result.returncode}\")

# Example participants.csv for longitudinal study:
# subject_id,session_id,dicom_directory
# 001,baseline,/data/raw/sub-001/ses-baseline
# 001,month06,/data/raw/sub-001/ses-month06  
# 001,month12,/data/raw/sub-001/ses-month12
# 002,baseline,/data/raw/sub-002/ses-baseline
# 002,month06,/data/raw/sub-002/ses-month06

longitudinal_study_workflow(
    participants_csv='longitudinal_participants.csv',
    study_dir='/data/longitudinal_study',
    heuristic='longitudinal_heuristic.py',
    fs_license='/opt/freesurfer/license.txt'
)
```

### Workflow 4: Task-Specific Processing

Process only specific tasks or runs:

```python
from yyprep.fmriprep.interface import create_fmriprep_workflow

def task_specific_workflow(bids_dir, output_dir, tasks, subjects, fs_license):
    \"\"\"Process only specific tasks for given subjects.\"\"\"
    
    # Create BIDS filter for specific tasks
    bids_filter = {
        \"bold\": {
            \"task\": tasks,
            \"datatype\": \"func\"
        },
        \"t1w\": {},  # Always include anatomical
        \"fmap\": {}  # Always include fieldmaps
    }
    
    # Save filter to file
    import json
    filter_file = 'task_filter.json'
    with open(filter_file, 'w') as f:
        json.dump(bids_filter, f, indent=2)
    
    # Run fMRIPrep with filter
    workflow = create_fmriprep_workflow(
        bids_dir=bids_dir,
        output_dir=output_dir,
        participant_label=subjects,
        task_id=tasks,  # Specify tasks directly
        bids_filter_file=filter_file,  # Or use filter file
        fs_license_file=fs_license,
        output_spaces=['MNI152NLin2009cAsym:res-2'],
        use_aroma=True
    )
    
    return workflow.run()

# Process only rest and nback tasks
result = task_specific_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    tasks=['rest', 'nback'],
    subjects=['001', '002', '003'],
    fs_license='/opt/freesurfer/license.txt'
)
```

## Research Lab Workflows

### Workflow 5: Multi-Study Lab Setup

Organize multiple studies in a research lab:

```python
import pandas as pd
from pathlib import Path
from yyprep.dicom2bids.convert import convert_dicom_to_bids
from yyprep.fmriprep.interface import create_fmriprep_workflow

class LabManager:
    \"\"\"Manage multiple studies in a research lab.\"\"\"
    
    def __init__(self, lab_dir, fs_license):
        self.lab_dir = Path(lab_dir)
        self.fs_license = fs_license
        
    def setup_study(self, study_name):
        \"\"\"Create directory structure for a new study.\"\"\"
        study_dir = self.lab_dir / study_name
        
        # Create directory structure
        directories = [
            'raw',           # Raw DICOM data
            'bids',          # BIDS dataset
            'derivatives',   # Processed data
            'code',          # Analysis code
            'work',          # Temporary processing files
            'logs'           # Processing logs
        ]
        
        for directory in directories:
            (study_dir / directory).mkdir(parents=True, exist_ok=True)
        
        return study_dir
    
    def process_study(self, study_name, participants_csv, heuristic):
        \"\"\"Process complete study from DICOM to fMRIPrep.\"\"\"
        
        # Setup study
        study_dir = self.setup_study(study_name)
        print(f\"Processing study: {study_name}\")
        
        # Load participants
        df = pd.read_csv(participants_csv)
        
        # Convert to BIDS
        print(\"Converting to BIDS...\")
        convert_dicom_to_bids(
            df=df,
            bids_dir=study_dir / 'bids',
            heuristic=heuristic
        )
        
        # Get study-specific parameters
        config = self.get_study_config(study_name)
        
        # Run fMRIPrep
        print(\"Running fMRIPrep...\")
        workflow = create_fmriprep_workflow(
            bids_dir=study_dir / 'bids',
            output_dir=study_dir / 'derivatives',
            participant_label=df['subject_id'].unique().tolist(),
            work_dir=study_dir / 'work',
            fs_license_file=self.fs_license,
            **config
        )
        
        result = workflow.run()
        
        # Generate summary report
        self.generate_study_report(study_name, result)
        
        return result
    
    def get_study_config(self, study_name):
        \"\"\"Get study-specific configuration.\"\"\"
        
        # Default configuration
        config = {
            'output_spaces': ['MNI152NLin2009cAsym:res-2'],
            'use_aroma': True,
            'skull_strip_template': 'OASIS30ANTs'
        }
        
        # Study-specific overrides
        study_configs = {
            'memory_study': {
                'output_spaces': ['MNI152NLin2009cAsym:res-2', 'fsnative'],
                'task_id': ['rest', 'memory'],
                'use_aroma': True
            },
            'attention_study': {
                'output_spaces': ['MNI152NLin2009cAsym:res-2'],
                'task_id': ['attention', 'rest'],
                'use_aroma': False
            }
        }
        
        if study_name in study_configs:
            config.update(study_configs[study_name])
        
        return config
    
    def generate_study_report(self, study_name, result):
        \"\"\"Generate processing summary report.\"\"\"
        
        study_dir = self.lab_dir / study_name
        report_file = study_dir / 'logs' / 'processing_report.txt'
        
        with open(report_file, 'w') as f:
            f.write(f\"Study: {study_name}\\n\")
            f.write(f\"Processed: {pd.Timestamp.now()}\\n\")
            f.write(f\"Return code: {result.returncode}\\n\")
            f.write(f\"Success: {'Yes' if result.returncode == 0 else 'No'}\\n\")
        
        print(f\"Report saved: {report_file}\")

# Usage
lab = LabManager('/lab/studies', '/opt/freesurfer/license.txt')

# Process multiple studies
studies = [
    ('memory_study', 'memory_participants.csv', 'memory_heuristic.py'),
    ('attention_study', 'attention_participants.csv', 'attention_heuristic.py')
]

for study_name, participants_csv, heuristic in studies:
    lab.process_study(study_name, participants_csv, heuristic)
```

## HPC Workflows

### Workflow 6: SLURM Cluster Processing

Process data on HPC clusters with SLURM:

```python
import subprocess
from pathlib import Path
from string import Template

def create_slurm_jobs(subjects, bids_dir, output_dir, fs_license, 
                     template_file='slurm_template.sh'):
    \"\"\"Create SLURM job scripts for each subject.\"\"\"
    
    # SLURM template
    slurm_template = Template('''#!/bin/bash
#SBATCH --job-name=yyprep-$subject
#SBATCH --partition=compute
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=logs/yyprep_$subject_%j.out
#SBATCH --error=logs/yyprep_$subject_%j.err

# Setup environment
module load singularity
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow

# Run yyprep
yyprep fmriprep $bids_dir $output_dir participant \\
    --participant-label $subject \\
    --fs-license-file $fs_license \\
    --n-cpus $$SLURM_CPUS_PER_TASK \\
    --mem-mb 32000 \\
    --work-dir $$SCRATCH/yyprep_work_$subject \\
    --output-spaces MNI152NLin2009cAsym:res-2 \\
    --use-aroma \\
    --verbose-count 1
''')
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    job_files = []
    for subject in subjects:
        # Create job script
        job_content = slurm_template.substitute(
            subject=subject,
            bids_dir=bids_dir,
            output_dir=output_dir,
            fs_license=fs_license
        )
        
        job_file = f'slurm_job_{subject}.sh'
        with open(job_file, 'w') as f:
            f.write(job_content)
        
        # Make executable
        Path(job_file).chmod(0o755)
        job_files.append(job_file)
    
    return job_files

def submit_slurm_jobs(job_files, max_concurrent=4):
    \"\"\"Submit SLURM jobs with dependency management.\"\"\"
    
    job_ids = []
    
    for i, job_file in enumerate(job_files):
        # Submit job
        if i < max_concurrent:
            # Submit first batch immediately
            result = subprocess.run(['sbatch', job_file], 
                                  capture_output=True, text=True)
        else:
            # Submit with dependency on earlier job
            dependency_job = job_ids[i - max_concurrent]
            result = subprocess.run(['sbatch', '--dependency=afterany:' + dependency_job, job_file],
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            job_id = result.stdout.strip().split()[-1]
            job_ids.append(job_id)
            print(f\"Submitted job {job_id} for {job_file}\")
        else:
            print(f\"Failed to submit {job_file}: {result.stderr}\")
    
    return job_ids

# Usage
subjects = ['001', '002', '003', '004', '005']
job_files = create_slurm_jobs(
    subjects=subjects,
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    fs_license='/home/user/license.txt'
)

job_ids = submit_slurm_jobs(job_files, max_concurrent=2)
print(f\"Submitted {len(job_ids)} jobs\")
```

## Quality Control Workflows

### Workflow 7: Automated QC Pipeline

Implement quality control checks:

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json

def quality_control_workflow(derivatives_dir, output_dir='qc_reports'):
    \"\"\"Generate comprehensive quality control reports.\"\"\"
    
    derivatives_path = Path(derivatives_dir)
    qc_dir = Path(output_dir)
    qc_dir.mkdir(exist_ok=True)
    
    # Find all subjects
    subjects = [d.name for d in derivatives_path.iterdir() 
               if d.is_dir() and d.name.startswith('sub-')]
    
    qc_data = []
    
    for subject in subjects:
        subject_dir = derivatives_path / subject
        
        # Check basic outputs
        html_report = derivatives_path / f\"{subject}.html\"
        
        # Analyze confounds files
        confounds_files = list(subject_dir.glob('func/*confounds*.tsv'))
        
        for confounds_file in confounds_files:
            try:
                confounds = pd.read_csv(confounds_file, sep='\\t')
                
                # Extract task and run info
                filename_parts = confounds_file.name.split('_')
                task = next((part.split('-')[1] for part in filename_parts if part.startswith('task-')), 'unknown')
                run = next((part.split('-')[1] for part in filename_parts if part.startswith('run-')), '1')
                
                # Calculate motion metrics
                motion_cols = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z']
                if all(col in confounds.columns for col in motion_cols):
                    trans_mean = confounds[['trans_x', 'trans_y', 'trans_z']].abs().mean().mean()
                    rot_mean = confounds[['rot_x', 'rot_y', 'rot_z']].abs().mean().mean()
                    
                    # Count high motion volumes (FD > 0.5mm)
                    if 'framewise_displacement' in confounds.columns:
                        high_motion_vols = (confounds['framewise_displacement'] > 0.5).sum()
                        total_vols = len(confounds)
                        high_motion_pct = (high_motion_vols / total_vols) * 100
                    else:
                        high_motion_vols = None
                        high_motion_pct = None
                    
                    qc_data.append({
                        'subject': subject,
                        'task': task,
                        'run': run,
                        'html_report_exists': html_report.exists(),
                        'mean_translation_mm': trans_mean,
                        'mean_rotation_rad': rot_mean,
                        'high_motion_volumes': high_motion_vols,
                        'high_motion_percent': high_motion_pct,
                        'total_volumes': len(confounds)
                    })
                
            except Exception as e:
                print(f\"Error processing {confounds_file}: {e}\")
    
    # Create QC DataFrame
    qc_df = pd.DataFrame(qc_data)
    
    if qc_df.empty:
        print(\"No QC data found\")
        return
    
    # Generate plots
    generate_qc_plots(qc_df, qc_dir)
    
    # Generate summary report
    generate_qc_summary(qc_df, qc_dir)
    
    # Save QC data
    qc_df.to_csv(qc_dir / 'qc_data.csv', index=False)
    
    print(f\"QC reports generated in {qc_dir}\")
    return qc_df

def generate_qc_plots(qc_df, qc_dir):
    \"\"\"Generate QC visualization plots.\"\"\"
    
    # Motion summary plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Translation parameters
    qc_df.boxplot(column='mean_translation_mm', by='task', ax=axes[0,0])
    axes[0,0].set_title('Mean Translation by Task')
    axes[0,0].set_ylabel('Translation (mm)')
    
    # Rotation parameters
    qc_df.boxplot(column='mean_rotation_rad', by='task', ax=axes[0,1]) 
    axes[0,1].set_title('Mean Rotation by Task')
    axes[0,1].set_ylabel('Rotation (radians)')
    
    # High motion percentage
    if 'high_motion_percent' in qc_df.columns:
        qc_df.boxplot(column='high_motion_percent', by='task', ax=axes[1,0])
        axes[1,0].set_title('High Motion Volumes (%) by Task')
        axes[1,0].set_ylabel('High Motion (%)')
    
    # Subject-wise motion
    subject_motion = qc_df.groupby('subject')['mean_translation_mm'].mean()
    subject_motion.plot(kind='bar', ax=axes[1,1])
    axes[1,1].set_title('Mean Translation by Subject')
    axes[1,1].set_ylabel('Translation (mm)')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(qc_dir / 'motion_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_qc_summary(qc_df, qc_dir):
    \"\"\"Generate text summary report.\"\"\"
    
    with open(qc_dir / 'qc_summary.txt', 'w') as f:
        f.write(\"=== fMRIPrep Quality Control Summary ===\\n\\n\")
        
        # Basic statistics
        f.write(f\"Total subjects processed: {qc_df['subject'].nunique()}\\n\")
        f.write(f\"Total runs processed: {len(qc_df)}\\n\")
        f.write(f\"Tasks found: {', '.join(qc_df['task'].unique())}\\n\\n\")
        
        # Motion statistics
        f.write(\"=== Motion Statistics ===\\n\")
        f.write(f\"Mean translation across all runs: {qc_df['mean_translation_mm'].mean():.3f} mm\\n\")
        f.write(f\"Mean rotation across all runs: {qc_df['mean_rotation_rad'].mean():.3f} rad\\n\")
        
        if 'high_motion_percent' in qc_df.columns:
            f.write(f\"Mean high motion percentage: {qc_df['high_motion_percent'].mean():.1f}%\\n\")
        
        # Outlier detection
        translation_threshold = qc_df['mean_translation_mm'].quantile(0.95)
        high_motion_subjects = qc_df[qc_df['mean_translation_mm'] > translation_threshold]['subject'].unique()
        
        if len(high_motion_subjects) > 0:
            f.write(f\"\\nSubjects with high motion (top 5%): {', '.join(high_motion_subjects)}\\n\")
        
        # Missing reports
        missing_reports = qc_df[~qc_df['html_report_exists']]['subject'].unique()
        if len(missing_reports) > 0:
            f.write(f\"\\nSubjects missing HTML reports: {', '.join(missing_reports)}\\n\")

# Usage
qc_results = quality_control_workflow('/data/derivatives', 'qc_reports')
```

## Custom Integration Workflows

### Workflow 8: Integration with Existing Pipelines

Integrate yyprep with existing analysis pipelines:

```python
from nipype import Workflow, Node, Function
from yyprep.fmriprep.interface import FMRIPrepInterface

def create_analysis_workflow(bids_dir, output_dir, subjects):
    \"\"\"Create complete analysis workflow including preprocessing and analysis.\"\"\"
    
    # Main workflow
    workflow = Workflow(name='complete_analysis', base_dir='/tmp/work')
    
    # Preprocessing with yyprep
    fmriprep_node = Node(
        FMRIPrepInterface(),
        name='fmriprep'
    )
    fmriprep_node.inputs.bids_dir = bids_dir
    fmriprep_node.inputs.output_dir = output_dir
    fmriprep_node.inputs.participant_label = subjects
    fmriprep_node.inputs.fs_license_file = '/opt/freesurfer/license.txt'
    fmriprep_node.inputs.output_spaces = ['MNI152NLin2009cAsym:res-2']
    
    # Custom analysis functions
    def first_level_analysis(fmriprep_dir, subject):
        \"\"\"Run first-level GLM analysis.\"\"\"
        print(f\"Running first-level analysis for {subject}\")
        # Your first-level analysis code here
        return f\"{fmriprep_dir}/first_level/{subject}\"
    
    def group_analysis(first_level_results):
        \"\"\"Run group-level analysis.\"\"\"
        print(\"Running group-level analysis\")
        # Your group analysis code here
        return \"group_results\"
    
    # Create analysis nodes
    first_level_node = Node(
        Function(
            input_names=['fmriprep_dir', 'subject'],
            output_names=['first_level_result'],
            function=first_level_analysis
        ),
        name='first_level'
    )
    
    group_node = Node(
        Function(
            input_names=['first_level_results'],
            output_names=['group_result'],
            function=group_analysis
        ),
        name='group_analysis'
    )
    
    # Connect workflow
    # Note: This is a simplified example - real workflows would need iterables
    workflow.connect([
        (fmriprep_node, first_level_node, [('output_dir', 'fmriprep_dir')]),
        (first_level_node, group_node, [('first_level_result', 'first_level_results')])
    ])
    
    return workflow

# Usage
workflow = create_analysis_workflow(
    bids_dir='/data/bids',
    output_dir='/data/derivatives',
    subjects=['001', '002', '003']
)

workflow.run()
```

These workflows demonstrate the flexibility and power of yyprep for various neuroimaging processing scenarios. Adapt them to your specific research needs and computational environment.

## Next Steps

- Explore the [API documentation](api.md) for detailed function references
- Check the [troubleshooting guide](troubleshooting.md) for common issues
- Review [configuration options](configuration.md) for optimization
- See the [examples directory](https://github.com/GalKepler/yyprep/tree/main/examples) for more complete examples
