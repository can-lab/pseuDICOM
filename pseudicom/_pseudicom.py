"""pseuDICOM

Pseudonimize DICOM images.

"""


import os

from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
from nipype.interfaces.io import DataFinder
from nipype.interfaces.dcm2nii import Dcm2nii, Dcm2niix
from nipype.interfaces.fsl import BET, maths, utils
from nipype.interfaces.quickshear import Quickshear


def pseudonimize_dicoms(directory,
                        run_dir_pattern="[0-9][0-9][0-9]-.+",
                        anatomy_keywords=[
                            "t1", "T1",
                            "mprage", "MPRAGE",
                            "AAHead"],
                        tags_to_clear=[
                            "(0008, 0080)",  # Institution Name
                            "(0008, 0081)",  # Institution Address
                            "(0008, 0090)",  # Referring Physician's Name
                            "(0008, 1010)",  # Station Name
                            "(0008, 1030)",  # Study Description
                            "(0008, 103e)",  # Series Description 
                            "(0008, 1040)",  # Institutional Department Name 
                            "(0008, 1048)",  # Physician(s) of Record 
                            "(0008, 1050)",  # Performing Physician's Name 
                            "(0010, 0010)",  # Patient's Name
                            "(0010, 0020)",  # Patient ID
                            "(0010, 0030)",  # Patient's Birth Date
                            "(0010, 0040)",  # Patient's Sex
                            "(0010, 1010)",  # Patient's Age
                            "(0010, 1020)",  # Patient's Size
                            "(0010, 1030)",  # Patient's Weight
                            "(0018, 1030)",  # Protocol Name
                            "(0032, 1032)",  # Requesting Physician 
                            "(0032, 1060)",  # Requested Procedure Description 
                                       ],
                        change_dates=True,
                        make_backup=True,
                        base_dir=None):

    """Psuedonimize DICOM images within a directory.

    This will (1) anonymize all DICOM files (i.e. remove identifiable personal
    and potentially identifiable information) and (2) deface high-resolution
    anatomical DICOMS.

    Parameters
    ----------
    run_dir_pattern : str, optional
        a regular expression that specifies the pattern to find run
        directories
        Default:
            "[0-9][0-9][0-9]-.+"
    anatomy_keywords : list, optional
        a list of keywords (as strings, e.g. "T1") that are part of the run
        directory name, if that run corresponnds to an anatomical recording
        Default:
            [
                "t1", "T1",
                "mprage", "MPRAGE",
                "AAHead"
            ]
    tags_to_clear : list, optional
        a list of DICOM tags (as strings, e.g. "(0010, 0010)") to clear
        Default:
            [
                "(0008, 0080)",  # Institution Name
                "(0008, 0081)",  # Institution Address
                "(0008, 0090)",  # Referring Physician's Name
                "(0008, 1010)",  # Station Name
                "(0008, 1030)",  # Study Description
                "(0008, 103e)",  # Series Description
                "(0008, 1040)",  # Institutional Department Name
                "(0008, 1048)",  # Physician(s) of Record
                "(0008, 1050)",  # Performing Physician's Name
                "(0010, 0010)",  # Patient's Name
                "(0010, 0020)",  # Patient ID
                "(0010, 0030)",  # Patient's Birth Date
                "(0010, 0040)",  # Patient's Sex
                "(0010, 1010)",  # Patient's Age
                "(0010, 1020)",  # Patient's Size
                "(0010, 1030)",  # Patient's Weight
                "(0018, 1030)",  # Protocol Name
                "(0032, 1032)",  # Requesting Physician
                "(0032, 1060)",  # Requested Procedure Description
            ]
    change_dates : bool, optional
        if True, all dates in the DICOM header will be changed to the current
        date
        Default:
            True
    make_backup : bool, optional
        if True, make backups before both anonymizing ("*.bak_anynym") and
        defacing ("*.bak_deface") in the same directory
        Default:
            True
    base_dir : str, optional
        a base directory for the Nipype worklfow
        Default:
            None

    """

    pseudonimize_wf = pe.Workflow('pseudonimize_dicoms')
    if base_dir is not None:
        pseudonimize_wf.base_dir = base_dir

    # Select all runs
    def _find_runs(directory, run_dir_pattern):
        import os
        import re
        out_paths = []
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                if re.search(run_dir_pattern, d):
                    out_paths.append(os.path.join(root, d))
        return out_paths

    find_runs = pe.Node(niu.Function(input_names=["directory",
                                                  "run_dir_pattern"],
                                     output_names=["out_paths"],
                                     function=_find_runs),
                        name="find_runs")
    find_runs.inputs.directory  = os.path.abspath(directory)
    find_runs.inputs.run_dir_pattern = run_dir_pattern

    # Anonymize DICOMs (MapNode)
    def _anonymize(in_path, make_backup, tags_to_clear, change_dates):
        import os
        import glob
        import datetime
        import pydicom
        dicoms = []
        files = glob.glob(os.path.join(in_path, "*"))
        for f in files:
            if f.endswith("dcm") or f.endswith("IMA"):
                dicoms.append(f)
        timestamp = datetime.datetime.now()
        today = timestamp.strftime("%Y%m%d")
        for f in files:
            d = pydicom.read_file(f)
            d.remove_private_tags()
            dates = []
            for element in d:
                if element.VR == "DA":
                    dates.append(element.value)
            for element in d:
                if str(element.tag) in tags_to_clear:
                    element.value = ""
                elif change_dates:
                    if element.VR == "SQ":
                        for s in element:
                            for e in s:
                                for date in dates:
                                    if date in str(e.value):
                                        e.value = str(e.value).replace(date,
                                                                       today)
                                        break
                    elif element.VR in ("DA", "UI"):
                        for date in dates:
                            if date in str(element.value):
                                element.value = str(element.value).replace(
                                    date, today)
                                break
            d.fix_meta_info()
            if make_backup:
                os.rename(f, f + ".bak_anonym")
            path, name = os.path.split(f)
            for date in dates:
                if date in name:
                    name = name.replace(date, today)
                    break
            d.save_as(os.path.join(path, name))
        return in_path

    anonymize = pe.MapNode(niu.Function(input_names=["in_path", "make_backup",
                                                    "tags_to_clear",
                                                    "change_dates"],
                                        output_names=["out_path"],
                                        function=_anonymize),
                         iterfield=["in_path"],
                         name="anonymize")
    anonymize.inputs.make_backup = make_backup
    anonymize.inputs.tags_to_clear = tags_to_clear
    anonymize.inputs.change_dates = change_dates

    # Select anatomy runs (Node)
    def _find_anats(in_paths, keywords):
        import os
        import glob
        out_files = []
        for path in in_paths:
            for keyword in keywords:
                if keyword in path:
                    dicoms = []
                    for files in ("*.dcm", "*.IMA"):
                        dicoms.extend(glob.glob(os.path.join(path, files)))
                    out_files.append(sorted(dicoms))
                    break
        return out_files

    find_anats = pe.Node(niu.Function(input_names=["in_paths", "keywords"],
                                      output_names=["out_files"],
                                      function=_find_anats),
                         name="find_anats")
    find_anats.inputs.keywords = anatomy_keywords

    # Convert DICOM to NIfTI (MapNode)
    converter = pe.MapNode(
        #Dcm2nii(args= '-x n -r n -p n -e n -f n -d n -g n -i y'),
        Dcm2niix(args= '-x i -i y'),
        name="dcm2nii", iterfield=["source_names"])

    # Remove derived, localizer and 2D images
    def _remove_derived(in_files, nii_files):
        print(len(in_files), len(nii_files))
        in_files_out = []
        nii_files_out = []
        for c,x in enumerate(nii_files):
            if type(x) == str:
                in_files_out.append(in_files[c])
                nii_files_out.append(x)
        print(len(in_files_out), len(nii_files_out))
        return in_files_out, nii_files_out

    remove_derived = pe.Node(niu.Function(input_names=["in_files",
                                                       "nii_files"],
                                          output_names=["out_files",
                                                        "nii_files"],
                                          function=_remove_derived),
                             name="remove_derived")

    # Deface NIfTI (MapNode)
    bet = pe.MapNode(BET(mask=True), name='bet', iterfield=["in_file"])
    deface = pe.MapNode(Quickshear(), name='deface',
                            iterfield=["in_file", "mask_file"])

    # Convert NiFTI to DICOM (MapNode)
    def _nii2dcm(in_file, dcm_files, make_backup):
        import numpy as np
        import nibabel as nb
        import pydicom
        img = nb.load(in_file)
        pixel_data = np.flip(img.get_fdata().astype(np.uint16), 2)
        for f in dcm_files:
            d = pydicom.read_file(f)
            slice_nr = int(d.InstanceNumber)
            if make_backup:
                d.save_as(f + ".bak_deface")
            d.PixelData = np.rot90(pixel_data[:,:,slice_nr-1]).tobytes()
            d.save_as(f)
        return dcm_files

    nii2dcm = pe.MapNode(niu.Function(input_names=['in_file', 'dcm_files',
                                                   'make_backup'],
                                      output_names=['out_files'],
                                      function=_nii2dcm),
                         name='nii2dcm', iterfield=["in_file", "dcm_files"])
    nii2dcm.inputs.make_backup = make_backup

    # Connect everything and run
    pseudonimize_wf.connect([
        (find_runs, anonymize, [('out_paths', 'in_path')]),
        (anonymize, find_anats, [('out_path', 'in_paths')]),
        (find_anats, converter, [('out_files', 'source_names')]),
        (find_anats, remove_derived, [('out_files', 'in_files')]),
        (converter, remove_derived, [('converted_files', 'nii_files')]),
        (remove_derived, bet, [('nii_files', 'in_file')]),
        (remove_derived, deface, [('nii_files', 'in_file')]),
        (bet, deface, [('mask_file', 'mask_file')]),
        (deface, nii2dcm, [('out_file', 'in_file')]),
        (remove_derived, nii2dcm, [('out_files', 'dcm_files')]),
        ])

    pseudonimize_wf.run()

