# Configuration

This guide covers configuring yyprep for different environments and use cases.

## Environment Configuration

### Python Environment Setup

#### Using Conda (Recommended)

```bash
# Create dedicated environment
conda create -n yyprep python=3.11
conda activate yyprep

# Install dependencies via conda
conda install -c conda-forge dcm2niix

# Install yyprep
pip install yyprep
```

#### Using Virtual Environment

```bash
# Create virtual environment
python -m venv yyprep_env
source yyprep_env/bin/activate  # Linux/macOS
# yyprep_env\Scripts\activate  # Windows

# Install yyprep
pip install yyprep
```

### Docker Configuration

#### Docker Desktop Settings

For optimal performance, configure Docker Desktop:

**Memory**: 16GB+ (for fMRIPrep)
**CPUs**: All available cores
**Disk**: 100GB+ free space

#### Linux Docker Configuration

```bash
# Increase Docker memory limits (if needed)
sudo systemctl edit docker

# Add these lines:
[Service]
LimitMEMLOCK=infinity
```

## Environment Variables

### FreeSurfer License

Set your FreeSurfer license path:

```bash
export FREESURFER_LICENSE=/path/to/license.txt
```

Or in Python:

```python
import os
os.environ['FREESURFER_LICENSE'] = '/path/to/license.txt'
```

### HeuDiConv Logging

Control HeuDiConv verbosity:

```bash
export HEUDICONV_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Docker Configuration

```bash
export DOCKER_HOST=unix:///var/run/docker.sock
```

## Configuration Files

### Default Settings

Create `~/.yyprep/config.yaml`:

```yaml
# Default paths
freesurfer_license: /opt/freesurfer/license.txt
work_dir: /tmp/yyprep_work

# Default fMRIPrep settings
fmriprep:
  output_spaces:
    - MNI152NLin2009cAsym:res-2
    - T1w
  use_aroma: true
  skull_strip_template: OASIS30ANTs
  
# Default resource settings
resources:
  mem_mb: 16000
  omp_nthreads: 8
  n_cpus: 12
```

### Project-Specific Configuration

Create `project_config.yaml`:

```yaml
# Project settings
study_name: memory_study
bids_dir: /data/memory_study/bids
output_dir: /data/memory_study/derivatives

# Custom heuristic
heuristic: /data/memory_study/code/memory_heuristic.py

# Participant selection
participants:
  - "001"
  - "002" 
  - "003"

# fMRIPrep settings
fmriprep:
  output_spaces:
    - MNI152NLin2009cAsym:res-2
    - fsnative
  task_id:
    - rest
    - memory
  use_aroma: true
  low_mem: false

# HPC settings (if applicable)
hpc:
  partition: gpu
  time_limit: "24:00:00"
  memory: "32G"
  cpus_per_task: 16
```

### Loading Configuration

```python
import yaml
from pathlib import Path

def load_config(config_file='project_config.yaml'):
    """Load configuration from YAML file."""
    config_path = Path(config_file)
    
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    else:
        return {}

# Usage
config = load_config()

# Use in workflow
from yyprep.fmriprep.interface import create_fmriprep_workflow

workflow = create_fmriprep_workflow(
    bids_dir=config['bids_dir'],
    output_dir=config['output_dir'],
    participant_label=config['participants'],
    **config['fmriprep']
)
```

## HPC Configuration

### SLURM Configuration

Create `slurm_template.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=yyprep-{subject}
#SBATCH --partition=compute
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=logs/yyprep_%j.out
#SBATCH --error=logs/yyprep_%j.err

# Load modules
module load singularity

# Set up environment
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
export SINGULARITYENV_FREESURFER_LICENSE=/freesurfer/license.txt

# Run yyprep
yyprep fmriprep {bids_dir} {output_dir} participant \
    --participant-label {subject} \
    --fs-license-file /freesurfer/license.txt \
    --n-cpus $SLURM_CPUS_PER_TASK \
    --mem-mb 32000 \
    --work-dir $SCRATCH/yyprep_work_{subject}
```

### PBS Configuration

Create `pbs_template.sh`:

```bash
#!/bin/bash
#PBS -N yyprep-{subject}
#PBS -l walltime=24:00:00
#PBS -l nodes=1:ppn=16
#PBS -l mem=32gb
#PBS -o logs/yyprep_$PBS_JOBID.out
#PBS -e logs/yyprep_$PBS_JOBID.err

cd $PBS_O_WORKDIR

# Run yyprep
yyprep fmriprep {bids_dir} {output_dir} participant \
    --participant-label {subject} \
    --fs-license-file /opt/freesurfer/license.txt \
    --n-cpus 16 \
    --mem-mb 32000
```

## Resource Optimization

### Automatic Resource Detection

```python
import psutil
from pathlib import Path

class ResourceManager:
    """Automatically configure resources based on system."""
    
    def __init__(self):
        self.total_memory = psutil.virtual_memory().total
        self.cpu_count = psutil.cpu_count()
        self.disk_space = psutil.disk_usage('/').free
    
    def get_fmriprep_config(self, conservative=True):
        """Get optimal fMRIPrep resource configuration."""
        
        if conservative:
            # Conservative settings (leave resources for system)
            mem_mb = int(self.total_memory * 0.6 / (1024**2))  # 60% of RAM
            n_cpus = max(1, self.cpu_count - 2)  # Leave 2 cores
            omp_nthreads = max(1, n_cpus // 2)
        else:
            # Aggressive settings (use most resources)
            mem_mb = int(self.total_memory * 0.8 / (1024**2))  # 80% of RAM
            n_cpus = max(1, self.cpu_count - 1)  # Leave 1 core
            omp_nthreads = max(1, n_cpus // 2)
        
        return {
            'mem_mb': mem_mb,
            'n_cpus': n_cpus,
            'omp_nthreads': omp_nthreads,
            'low_mem': mem_mb < 16000  # Enable low-mem if < 16GB
        }
    
    def check_requirements(self, min_memory_gb=8, min_cpus=4):
        """Check if system meets minimum requirements."""
        
        memory_gb = self.total_memory / (1024**3)
        disk_gb = self.disk_space / (1024**3)
        
        checks = {
            'memory': memory_gb >= min_memory_gb,
            'cpus': self.cpu_count >= min_cpus,
            'disk_space': disk_gb >= 50  # Minimum 50GB free
        }
        
        return all(checks.values()), checks

# Usage
rm = ResourceManager()
meets_req, details = rm.check_requirements()

if meets_req:
    config = rm.get_fmriprep_config()
    print(f"Recommended fMRIPrep config: {config}")
else:
    print(f"System requirements not met: {details}")
```

### Storage Configuration

```python
from pathlib import Path
import shutil

def setup_work_directories(base_dir='/tmp', subjects=None):
    """Set up temporary work directories for processing."""
    
    base_path = Path(base_dir)
    
    # Check available space
    total, used, free = shutil.disk_usage(base_path)
    free_gb = free / (1024**3)
    
    if free_gb < 100:  # Less than 100GB free
        print(f"Warning: Only {free_gb:.1f}GB free in {base_dir}")
        
        # Try alternative locations
        alternatives = ['/scratch', '/tmp', Path.home() / 'tmp']
        for alt in alternatives:
            alt_path = Path(alt)
            if alt_path.exists():
                total, used, free = shutil.disk_usage(alt_path)
                alt_free_gb = free / (1024**3)
                if alt_free_gb > free_gb:
                    base_path = alt_path
                    free_gb = alt_free_gb
                    print(f"Using {alt_path} with {free_gb:.1f}GB free")
                    break
    
    # Create work directories
    work_dirs = {}
    if subjects:
        for subject in subjects:
            work_dir = base_path / f'yyprep_work_{subject}'
            work_dir.mkdir(parents=True, exist_ok=True)
            work_dirs[subject] = str(work_dir)
    else:
        work_dir = base_path / 'yyprep_work'
        work_dir.mkdir(parents=True, exist_ok=True)
        work_dirs['default'] = str(work_dir)
    
    return work_dirs

# Usage
work_dirs = setup_work_directories(subjects=['001', '002', '003'])
print(work_dirs)
```

## Security Configuration

### Docker Security

```bash
# Run Docker as non-root user
sudo usermod -aG docker $USER

# Use Docker user namespace mapping (optional)
sudo dockerd --userns-remap=default
```

### File Permissions

```python
import os
from pathlib import Path

def secure_directory_setup(base_dir):
    """Set up directories with appropriate permissions."""
    
    base_path = Path(base_dir)
    
    # Create directories with restricted permissions
    directories = ['bids', 'derivatives', 'work', 'logs']
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Set permissions: owner read/write/execute, group read/execute
        os.chmod(dir_path, 0o750)
    
    print(f"Secure directories created in {base_path}")

# Usage
secure_directory_setup('/data/study')
```

## Performance Tuning

### I/O Optimization

```python
import tempfile
from pathlib import Path

def optimize_io_settings():
    """Optimize I/O settings for yyprep."""
    
    # Use RAM disk for temporary files (if available)
    ram_disk_paths = ['/dev/shm', '/tmp']
    
    for path in ram_disk_paths:
        if Path(path).exists():
            # Check available space
            import shutil
            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024**3)
            
            if free_gb > 10:  # At least 10GB available
                return path
    
    # Fallback to system temp
    return tempfile.gettempdir()

# Usage
optimal_work_dir = optimize_io_settings()
print(f"Using work directory: {optimal_work_dir}")
```

### Parallel Processing Configuration

```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing

def get_optimal_parallelization():
    """Determine optimal parallel processing settings."""
    
    cpu_count = multiprocessing.cpu_count()
    
    # Different strategies based on system size
    if cpu_count >= 16:
        # High-end system: process multiple subjects in parallel
        max_subjects_parallel = 4
        cpus_per_subject = cpu_count // max_subjects_parallel
    elif cpu_count >= 8:
        # Medium system: process 2 subjects in parallel
        max_subjects_parallel = 2
        cpus_per_subject = cpu_count // max_subjects_parallel
    else:
        # Low-end system: process one subject at a time
        max_subjects_parallel = 1
        cpus_per_subject = cpu_count
    
    return {
        'max_subjects_parallel': max_subjects_parallel,
        'cpus_per_subject': cpus_per_subject,
        'total_cpus': cpu_count
    }

# Usage
parallel_config = get_optimal_parallelization()
print(f"Parallel processing config: {parallel_config}")
```

## Validation and Testing

### Configuration Validation

```python
def validate_configuration(config):
    """Validate yyprep configuration."""
    
    errors = []
    warnings = []
    
    # Check required paths
    required_paths = ['bids_dir', 'output_dir']
    for path_key in required_paths:
        if path_key not in config:
            errors.append(f"Missing required path: {path_key}")
        elif not Path(config[path_key]).exists():
            errors.append(f"Path does not exist: {config[path_key]}")
    
    # Check FreeSurfer license
    if 'fs_license_file' in config:
        license_path = Path(config['fs_license_file'])
        if not license_path.exists():
            errors.append(f"FreeSurfer license not found: {license_path}")
    else:
        warnings.append("FreeSurfer license not specified")
    
    # Check resource settings
    if 'mem_mb' in config:
        if config['mem_mb'] < 8000:
            warnings.append("Memory setting < 8GB may cause issues")
    
    if 'n_cpus' in config:
        import psutil
        if config['n_cpus'] > psutil.cpu_count():
            warnings.append("CPU setting exceeds available cores")
    
    return errors, warnings

# Usage
config = {
    'bids_dir': '/data/bids',
    'output_dir': '/data/derivatives',
    'fs_license_file': '/opt/freesurfer/license.txt',
    'mem_mb': 16000,
    'n_cpus': 8
}

errors, warnings = validate_configuration(config)
if errors:
    print("Configuration errors:", errors)
if warnings:
    print("Configuration warnings:", warnings)
```

## Next Steps

- Set up your [first workflow](quickstart.md)
- Explore [advanced usage patterns](usage.md)
- Review [troubleshooting tips](troubleshooting.md)
