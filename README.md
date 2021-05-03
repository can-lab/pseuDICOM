# pseuDICOM
Pseudonimize DICOM images

## Introduction
To share raw (f)MRI DICOM images with other researchers, the data first has to be pseudonimized.
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
1. Create new environment in home directory by running command: `cd && python3 -m venv pseudicom_env`
2. Activate new environment by running command: `source pseudicom_env/bin/activate`
3. Install Nipype, pydicom, quickshear: `pip3 install nipype pydicom quickshear`
4. Download [pseuDICOM](https://github.com/can-lab/pseuDICOM/master.zip)
5. Install with
   ```
   pip3 install pseuDICOM-X.X.X.zip
   ```
   (replace X.X.X with latest release version)

## Usage
Example:
```python
import os
import glob

from pseudicom import pseudonimize_dicoms


for subject_dir in glob.glob("path/to/study_dir/sub-*"):
    pseudonimize_dicoms(subject_dir,
                        run_dir_pattern="[0-9][0-9][0-9]-.+",
                        anatomy_keywords=["t1","AAHead_Scout"],
                        tags_to_clear=[
                            "(0010, 0010)",  # Patient's Name
                            "(0010, 0030)",  # Patient's Birth Date
                                       ],
                        change_dates=True,
                        make_backup=True)
```

### Donders cluster
If you are working on the compute cluster of the Donders Institute, please follow the following steps:
1. Start a new interactive job by running command: `qsub -I -l 'procs=8, mem=64gb, walltime=24:00:00'`
2. Load the dcm2niix module by running command: `module load dcm2niix`
3. Activate environment by running command: `source pseudicom_env/bin/activate`
4. Write script `mystudy_pseudicom.py` with custom workflow; example:
    ```python
    import os
    import glob

    from pseudicom import pseudonimize_dicoms


    for subject_dir in glob.glob("path/to/study_dir/sub-*"):
        pseudonimize_dicoms(subject_dir,
                            run_dir_pattern="[0-9][0-9][0-9]-.+",
                            anatomy_keywords=["t1","AAHead_Scout"],
                            tags_to_clear=[
                                "(0010, 0010)",  # Patient's Name
                                "(0010, 0030)",  # Patient's Birth Date
                                           ],
                            change_dates=True,
                            make_backup=True)
    ```
6. Run script by running command: `python3 mystudy_pseudicom.py`
