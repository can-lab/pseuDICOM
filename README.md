# pseuDICOM
Pseudonimize (f)MRI data in DICOM format

## Introduction
To share (f)MRI DICOM images with other researchers, the data has to be pseudonimized.
This entails two steps:

1. **Anonymization of all images** (i.e. removing identifiable personal and potentially identifiable information from the DICOM header)
2. **Defacing high-resolution anatomical images** (i.e. removing anterior pxiel data that might allow for reconstructing facial features)

pseuDICOM will perform both of these steps in one go and, unlike most defacing tools, output the final result again in DICOM format.

<img src="https://user-images.githubusercontent.com/2971539/116867429-73a9eb00-ac0d-11eb-9374-5a96ce25bbd4.png" height="500">

## Prerequisites
1. Install [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/)
2. Install [MRIcroGL](https://www.nitrc.org/projects/mricrogl/) (includes a binary for dcm2niix)
3. Install nipype, pydicom, quickshear
   ```
   pip3 install nipype pydicom quickshear
   ```
4. Download [pseuDICOM](https://github.com/can-lab/pseuDICOM/master.zip)
5. Install with
   ```
   pip3 install pseuDICOM-X.X.X.zip
   ```
   (replace X.X.X with latest release version)

### Donders cluster
If you are working on the compute cluster of the Donders Institute, please follow the following steps:
1. Load Anaconda3 module by running command: `module load anaconda3`
2. Create new environment in home directory by running command: `cd && python3 -m venv pseudicom_env`
3. Activate new environment by running command: `source pseudicom_env/bin/activate`
4. Install Nipype, pydicom, quickshear: `pip3 install nipype pydicom quickshear`
5. Download [pseuDICOM](https://github.com/can-lab/pseuDICOM/master.zip)
6. Install with
   ```
   pip3 install pseuDICOM-X.X.X.zip
   ```
   (replace X.X.X with latest release version)

## Usage
An simple example running pseuDICOM on data from a single session with [default arguments](https://github.com/can-lab/pseuDICOM/blob/c803aa583bcf38c0725be68cdf8774d1de591b2f/pseudicom/_pseudicom.py#L18):
```python
from pseudicom import pseudonimize_dicoms

pseudonimize_dicoms("path/to/session_dir")
```

A more advanced example running pseuDICOM on the data of an entire study with some custom arguments:
```python
import os
import glob
from pseudicom import pseudonimize_dicoms

for subject_dir in glob.glob("path/to/study_dir/sub*"):
    for session_dir in glob.glob(os.path.join(subject_dir, "ses-,ri*)):
          pseudonimize_dicoms(session_dir,
                              anatomy_keywords=["t1","AAHead_Scout"],
                              tags_to_clear=[
                                  "(0010, 0010)",  # Patient's Name
                                  "(0010, 0030)",  # Patient's Birth Date
                                             ])
```

Please note that pseuDICOM always assumes that DICOM images are organized in dedicated run/series subdirectories!


### Donders cluster
If you are working on the compute cluster of the Donders Institute, please follow the following steps:
1. Start a new interactive job by running command: `qsub -I -l 'procs=8, mem=64gb, walltime=24:00:00'`
2. Load the dcm2niix module by running command: `module load dcm2niix`
3. Activate environment by running command: `source pseudicom_env/bin/activate`
4. Write script `mystudy_pseudicom.py` (see above for example)
6. Run script by running command: `python3 mystudy_pseudicom.py`
