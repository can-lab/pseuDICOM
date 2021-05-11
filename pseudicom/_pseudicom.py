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
                            "AAHead"
                        ],
                        tags_to_clear=[
                            "(0007, 002a)",  # Acquisition DateTime
                            "(0008, 0012)",  # Instance Creation Date
                            "(0008, 0013)",  # Instance Creation Time
                            "(0008, 0020)",  # Study Date 
                            "(0008, 0021)",  # Series Date
                            "(0008, 0022)",  # Acquisition Date
                            "(0008, 0023)",  # Content Date
                            "(0008, 0030)",  # Study Time
                            "(0008, 0031)",  # Series Time
                            "(0008, 0033)",  # Content Time
                            "(0008, 0050)",  # Accession Number
                            "(0008, 0070)",  # Manufacturer
                            "(0008, 0080)",  # Institution Name
                            "(0008, 0081)",  # Institution Address
                            "(0008, 0090)",  # Referring Physician's Name
                            "(0008, 0092)",  # Referring Physician's Address
                            "(0008, 0094)",  # Referring Physician's Telephone Number
                            "(0008, 1010)",  # Station Name
                            "(0008, 1030)",  # Study Descripion
                            "(0008, 103e)",  # Series Description
                            "(0008, 1040)",  # Institutional Department Name
                            "(0008, 1048)",  # Physician(s) of Record
                            "(0008, 1050)",  # Performing Physician's Name
                            "(0008, 1060)",  # Name of Physician(s) Reading Study
                            "(0008, 1070)",  # Operators' Name
                            "(0008, 1080)",  # Admitting Diagnoses Description
                            "(0008, 1090)",  # Manufacturer's Model Name
                            "(0008, 2111)",  # Derivation Description
                            "(0010, 0010)",  # Patient's Name
                            "(0010, 0020)",  # Patient ID
                            "(0010, 0021)",  # Issuer of Patient ID
                            "(0010, 0030)",  # Patient's Birth Date
                            "(0010, 0032)",  # Patient's Birth Time
                            "(0010, 0040)",  # Patient's Sex
                            "(0010, 1001)",  # Other Patient Names
                            "(0010, 1002)",  # Other Patient IDs (SEQ)
                            "(0010, 1005)",  # Patient's Birth Name
                            "(0010, 1010)",  # Patient's Age
                            "(0010, 1020)",  # Patient's Size
                            "(0010, 1030)",  # Patient's Weight
                            "(0010, 1040)",  # Patient's Address
                            "(0010, 1060)",  # Patient's Mother's Birth Name
                            "(0010, 1080)",  # Military Rank
                            "(0010, 1081)",  # Branch Of Service
                            "(0010, 1090)",  # Medical Record Locator
                            "(0010, 2150)",  # Country of Residence
                            "(0010, 2152)",  # Region of Residence
                            "(0010, 2154)",  # Patient's Telephone Numbers
                            "(0010, 2160)",  # Ethnic Group
                            "(0010, 2180)",  # Occupation
                            "(0010, 21b0)",  # Additional Patient History
                            "(0010, 21f0)",  # Patient's Religious Preference
                            "(0010, 4000)",  # Patient Comments
                            "(0018, 1000)",  # Device Serial Number
                            "(0018, 1020)",  # Software Version(s)
                            "(0018, 1200)",  # Date of Last Calibration
                            "(0018, 1201)",  # Time of Last Calibration
                            "(0020, 0010)",  # Study ID
                            "(0020, 4000)",  # Image Comments
                            "(0032, 0012)",  # Study ID Issuer
                            "(0032, 0032)",  # Study Verfied Date
                            "(0032, 0033)",  # Study Verfied Time
                            "(0032, 0034)",  # Study Read Date
                            "(0032, 0035)",  # Study Read Time
                            "(0032, 1000)",  # Scheduled Study Start Date
                            "(0032, 1001)",  # Scheduled Study Start Time
                            "(0032, 1010)",  # Scheduled Study Stop Date
                            "(0032, 1011)",  # Scheduled Study Stop Time
                            "(0032, 1020)",  # Scheduled Study Location
                            "(0032, 1021)",  # Schelued Study Location AE Title
                            "(0032, 1030)",  # Reason for Study
                            "(0032, 1032)",  # Requesting Physician
                            "(0032, 1033)",  # Requesting Service
                            "(0032, 1040)",  # Study Arrival Date
                            "(0032, 1041)",  # Study Arrival Time
                            "(0032, 1050)",  # Study Completion Date
                            "(0032, 1051)",  # Study Completion Time
                            "(0032, 1060)",  # Requested Procedure Description
                            "(0032, 4000)",  # Study Comments
                            "(0038, 0010)",  # Admission ID
                            "(0038, 0014)",  # Issuer of Admission ID
                            "(0038, 001a)",  # Scheduled Admission Date
                            "(0038, 001b)",  # Scheduled Admission Time
                            "(0038, 001c)",  # Scheduled Discharge Date
                            "(0038, 001d)",  # Scheduled Discharge Time
                            "(0038, 001e)",  # Scheduled Patient Institution Residence
                            "(0038, 0020)",  # Admitting Date
                            "(0038, 0021)",  # Admitting Time
                            "(0038, 0030)",  # Discharge Date
                            "(0038, 0032)",  # Discharge Time
                            "(0038, 0300)",  # Current Patient Location
                            "(0038, 0400)",  # Patient's Institution Residence
                            "(0038, 4000)",  # Visit Comments
                            "(0040, 0001)",  # Scheduled Station AE Title
                            "(0040, 0002)",  # Scheduled Procedure Step Start Date
                            "(0040, 0003)",  # Scheduled Procedure Step Start Time
                            "(0040, 0004)",  # Scheduled Procedure Step End Date
                            "(0040, 0005)",  # Scheduled Procedure Step End Time
                            "(0040, 0006)",  # Scheduled Performing Physician's Name
                            "(0040, 0007)",  # Scheduled Procedure Step Description
                            "(0040, 0010)",  # Scheduled Station Name
                            "(0040, 0011)",  # Scheduled Procedure Step Location
                            "(0040, 0241)",  # Performed Station AE Title
                            "(0040, 0242)",  # Performed Station Name
                            "(0040, 0243)",  # Performed Location
                            "(0040, 0244)",  # Performed Procedure Step Start Date
                            "(0040, 0245)",  # Performed Procedure Step Start Time
                            "(0040, 0250)",  # Performed Procedure Step End Date
                            "(0040, 0251)",  # Performed Procedure Step End Time
                            "(0040, 0254)",  # Performed Procedure Step Description
                            "(0040, 0255)",  # Performed Procedure Type Description
                            "(0040, 0280)",  # Comments on the Performed Procedure Step
                            "(0040, 0400)",  # Comments on the Scheduled Procedure Step
                            "(0040, 1002)",  # Reason for the Requested Procedure
                            "(0040, 1004)",  # Patient Transport Arrangement
                            "(0040, 1005)",  # Requested Procedure Location
                            "(0040, 1010)",  # Names of Intended Recipients of Results
                            "(0040, 2001)",  # Reason for the Imaging Service Request
                            "(0040, 2004)",  # Issue Date of Imaging Service Request
                            "(0040, 2005)",  # Issue Time of Imaging Service Request
                            "(0040, 2008)",  # Order Entered By
                            "(0040, 2009)",  # Order Enterer's Location
                            "(0040, 2010)",  # Order Callback Phone Number
                            "(0040, 2400)",  # Imaging Service Request Comments
                            "(0040, 1400)",  # Requested Procedure Comments
                            "(4008, 0042)",  # Results ID Issuer
                            "(4008, 0100)",  # Interpretation Recorded Date
                            "(4008, 0101)",  # Interpretation Recorded Time
                            "(4008, 0102)",  # Interpretation Recorder
                            "(4008, 0103)",  # Reference to Recorded Sound
                            "(4008, 0108)",  # Interpretation Transcription Date
                            "(4008, 0109)",  # Interpretation Transcription Time
                            "(4008, 010a)",  # Interpretation Transcriber
                            "(4008, 010b)",  # Interpretation Text
                            "(4008, 010c)",  # Interpretation Author
                            "(4008, 0112)",  # Interpretation Approval Date
                            "(4008, 0113)",  # Interpretation Approval Time
                            "(4008, 0114)",  # Physician Approving Interpretation
                            "(4008, 0115)",  # Interpretation Diagnosis Description
                            "(4008, 0119)",  # Distibution Name
                            "(4008, 011a)",  # Distribution Address
                            "(4008, 0202)",  # Interpretation ID Issuer
                            "(4008, 0300)",  # Impressions
                            "(4008, 4000)",  # Results Comments
                        ],
                        change_dates=True,
                        make_backup=True,
                        work_dir=None):

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
                "(0007, 002a)",  # Acquisition DateTime
                "(0008, 0012)",  # Instance Creation Date
                "(0008, 0013)",  # Instance Creation Time
                "(0008, 0020)",  # Study Date 
                "(0008, 0021)",  # Series Date
                "(0008, 0022)",  # Acquisition Date
                "(0008, 0023)",  # Content Date
                "(0008, 0030)",  # Study Time
                "(0008, 0031)",  # Series Time
                "(0008, 0033)",  # Content Time
                "(0008, 0050)",  # Accession Number
                "(0008, 0070)",  # Manufacturer
                "(0008, 0080)",  # Institution Name
                "(0008, 0081)",  # Institution Address
                "(0008, 0090)",  # Referring Physician's Name
                "(0008, 0092)",  # Referring Physician's Address
                "(0008, 0094)",  # Referring Physician's Telephone Number
                "(0008, 1010)",  # Station Name
                "(0008, 1030)",  # Study Descripion
                "(0008, 103e)",  # Series Description
                "(0008, 1040)",  # Institutional Department Name
                "(0008, 1048)",  # Physician(s) of Record
                "(0008, 1050)",  # Performing Physician's Name
                "(0008, 1060)",  # Name of Physician(s) Reading Study
                "(0008, 1070)",  # Operators' Name
                "(0008, 1080)",  # Admitting Diagnoses Description
                "(0008, 1090)",  # Manufacturer's Model Name
                "(0008, 2111)",  # Derivation Description
                "(0010, 0010)",  # Patient's Name
                "(0010, 0020)",  # Patient ID
                "(0010, 0021)",  # Issuer of Patient ID
                "(0010, 0030)",  # Patient's Birth Date
                "(0010, 0032)",  # Patient's Birth Time
                "(0010, 0040)",  # Patient's Sex
                "(0010, 1001)",  # Other Patient Names
                "(0010, 1002)",  # Other Patient IDs (SEQ)
                "(0010, 1005)",  # Patient's Birth Name
                "(0010, 1010)",  # Patient's Age
                "(0010, 1020)",  # Patient's Size
                "(0010, 1030)",  # Patient's Weight
                "(0010, 1040)",  # Patient's Address
                "(0010, 1060)",  # Patient's Mother's Birth Name
                "(0010, 1080)",  # Military Rank
                "(0010, 1081)",  # Branch Of Service
                "(0010, 1090)",  # Medical Record Locator
                "(0010, 2150)",  # Country of Residence
                "(0010, 2152)",  # Region of Residence
                "(0010, 2154)",  # Patient's Telephone Numbers
                "(0010, 2160)",  # Ethnic Group
                "(0010, 2180)",  # Occupation
                "(0010, 21b0)",  # Additional Patient History
                "(0010, 21f0)",  # Patient's Religious Preference
                "(0010, 4000)",  # Patient Comments
                "(0018, 1000)",  # Device Serial Number
                "(0018, 1020)",  # Software Version(s)
                "(0018, 1200)",  # Date of Last Calibration
                "(0018, 1201)",  # Time of Last Calibration
                "(0020, 0010)",  # Study ID
                "(0020, 4000)",  # Image Comments
                "(0032, 0012)",  # Study ID Issuer
                "(0032, 0032)",  # Study Verfied Date
                "(0032, 0033)",  # Study Verfied Time
                "(0032, 0034)",  # Study Read Date
                "(0032, 0035)",  # Study Read Time
                "(0032, 1000)",  # Scheduled Study Start Date
                "(0032, 1001)",  # Scheduled Study Start Time
                "(0032, 1010)",  # Scheduled Study Stop Date
                "(0032, 1011)",  # Scheduled Study Stop Time
                "(0032, 1020)",  # Scheduled Study Location
                "(0032, 1021)",  # Schelued Study Location AE Title
                "(0032, 1030)",  # Reason for Study
                "(0032, 1032)",  # Requesting Physician
                "(0032, 1033)",  # Requesting Service
                "(0032, 1040)",  # Study Arrival Date
                "(0032, 1041)",  # Study Arrival Time
                "(0032, 1050)",  # Study Completion Date
                "(0032, 1051)",  # Study Completion Time
                "(0032, 1060)",  # Requested Procedure Description
                "(0032, 4000)",  # Study Comments
                "(0038, 0010)",  # Admission ID
                "(0038, 0014)",  # Issuer of Admission ID
                "(0038, 001a)",  # Scheduled Admission Date
                "(0038, 001b)",  # Scheduled Admission Time
                "(0038, 001c)",  # Scheduled Discharge Date
                "(0038, 001d)",  # Scheduled Discharge Time
                "(0038, 001e)",  # Scheduled Patient Institution Residence
                "(0038, 0020)",  # Admitting Date
                "(0038, 0021)",  # Admitting Time
                "(0038, 0030)",  # Discharge Date
                "(0038, 0032)",  # Discharge Time
                "(0038, 0300)",  # Current Patient Location
                "(0038, 0400)",  # Patient's Institution Residence
                "(0038, 4000)",  # Visit Comments
                "(0040, 0001)",  # Scheduled Station AE Title
                "(0040, 0002)",  # Scheduled Procedure Step Start Date
                "(0040, 0003)",  # Scheduled Procedure Step Start Time
                "(0040, 0004)",  # Scheduled Procedure Step End Date
                "(0040, 0005)",  # Scheduled Procedure Step End Time
                "(0040, 0006)",  # Scheduled Performing Physician's Name
                "(0040, 0007)",  # Scheduled Procedure Step Description
                "(0040, 0010)",  # Scheduled Station Name
                "(0040, 0011)",  # Scheduled Procedure Step Location
                "(0040, 0241)",  # Performed Station AE Title
                "(0040, 0242)",  # Performed Station Name
                "(0040, 0243)",  # Performed Location
                "(0040, 0244)",  # Performed Procedure Step Start Date
                "(0040, 0245)",  # Performed Procedure Step Start Time
                "(0040, 0250)",  # Performed Procedure Step End Date
                "(0040, 0251)",  # Performed Procedure Step End Time
                "(0040, 0254)",  # Performed Procedure Step Description
                "(0040, 0255)",  # Performed Procedure Type Description
                "(0040, 0280)",  # Comments on the Performed Procedure Step
                "(0040, 0400)",  # Comments on the Scheduled Procedure Step
                "(0040, 1002)",  # Reason for the Requested Procedure
                "(0040, 1004)",  # Patient Transport Arrangement
                "(0040, 1005)",  # Requested Procedure Location
                "(0040, 1010)",  # Names of Intended Recipients of Results
                "(0040, 2001)",  # Reason for the Imaging Service Request
                "(0040, 2004)",  # Issue Date of Imaging Service Request
                "(0040, 2005)",  # Issue Time of Imaging Service Request
                "(0040, 2008)",  # Order Entered By
                "(0040, 2009)",  # Order Enterer's Location
                "(0040, 2010)",  # Order Callback Phone Number
                "(0040, 2400)",  # Imaging Service Request Comments
                "(0040, 1400)",  # Requested Procedure Comments
                "(4008, 0042)",  # Results ID Issuer
                "(4008, 0100)",  # Interpretation Recorded Date
                "(4008, 0101)",  # Interpretation Recorded Time
                "(4008, 0102)",  # Interpretation Recorder
                "(4008, 0103)",  # Reference to Recorded Sound
                "(4008, 0108)",  # Interpretation Transcription Date
                "(4008, 0109)",  # Interpretation Transcription Time
                "(4008, 010a)",  # Interpretation Transcriber
                "(4008, 010b)",  # Interpretation Text
                "(4008, 010c)",  # Interpretation Author
                "(4008, 0112)",  # Interpretation Approval Date
                "(4008, 0113)",  # Interpretation Approval Time
                "(4008, 0114)",  # Physician Approving Interpretation
                "(4008, 0115)",  # Interpretation Diagnosis Description
                "(4008, 0119)",  # Distibution Name
                "(4008, 011a)",  # Distribution Address
                "(4008, 0202)",  # Interpretation ID Issuer
                "(4008, 0300)",  # Impressions
                "(4008, 4000)",  # Results Comments
            ]
    change_dates : bool or str, optional
        if True, all dates in the DICOM header will be changed to the current;
        date; if a string is given, all dates will be changed to that string
        Default:
            True
    make_backup : bool, optional
        if True, make backups before both anonymizing ("*.bak_anynym") and
        defacing ("*.bak_deface") in the same directory
        Default:
            True
    work_dir : str, optional
        a working directory for the Nipype worklfow
        Default:
            None

    """

    pseudonimize_wf = pe.Workflow('pseudonimize_dicoms')
    if work_dir is not None:
        pseudonimize_wf.base_dir = work_dir

    # Select all runs
    def _find_runs(directory, run_dir_pattern):
        import os
        import re
        out_paths = []
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                if re.search(run_dir_pattern, d):
                    out_paths.append(os.path.join(root, d))
        return sorted(out_paths)

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
        if change_dates is True:
          timestamp = datetime.datetime.now()
          new_date = timestamp.strftime("%Y%m%d")
        else:
          new_date = change_dates
        for f in files:
            d = pydicom.dcmread(f)
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
                                                                       new_date)
                                        break
                    elif element.VR in ("DA", "UI"):
                        for date in dates:
                            if date in str(element.value):
                                element.value = str(element.value).replace(
                                    date, new_date)
                                break
            d.fix_meta_info()
            if make_backup:
                os.rename(f, f + ".bak_anonym")
            else:
                os.remove(f)
            path, name = os.path.split(f)
            for date in dates:
                if date in name:
                    name = name.replace(date, new_date)
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
        import traits
        in_files_out = []
        nii_files_out = []
        len_diff = len(in_files) - len(nii_files)
        if len_diff > 0:  # dcm2niix removes <undefined> at the beginning of the outputs list!
            in_files = in_files[len_diff:]
        for c,x in enumerate(nii_files):
            if type(x) != traits.trait_base._Undefined:
                in_files_out.append(in_files[c])
                nii_files_out.append(x)
                
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
                        iterfield=["in_file", "mask_file", "out_file"])

    # Convert NiFTI to DICOM (MapNode)
    def _nii2dcm(in_file, dcm_files, make_backup):
        import numpy as np
        import nibabel as nb
        import pydicom
        img = nb.load(in_file)
        pixel_data = np.flip(img.get_fdata().astype(np.uint16), 2)
        for f in dcm_files:
            d = pydicom.dcmread(f)
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

    # Helper functions
    def fix_defaced_outfile(niis):
        import os
        return [os.path.split(nii)[-1].replace(".nii", "_defaced.nii") \
                for nii in niis]

    # Connect everything and run
    pseudonimize_wf.connect([
        (find_runs, anonymize, [('out_paths', 'in_path')]),
        (anonymize, find_anats, [('out_path', 'in_paths')]),
        (find_anats, converter, [('out_files', 'source_names')]),
        (find_anats, remove_derived, [('out_files', 'in_files')]),
        (converter, remove_derived, [('converted_files', 'nii_files')]),
        (remove_derived, bet, [('nii_files', 'in_file')]),
        (remove_derived, deface, [('nii_files', 'in_file')]),
        (remove_derived, deface,
         [(('nii_files', fix_defaced_outfile), 'out_file')]),
        (bet, deface, [('mask_file', 'mask_file')]),
        (deface, nii2dcm, [('out_file', 'in_file')]),
        (remove_derived, nii2dcm, [('out_files', 'dcm_files')]),
        ])

    pseudonimize_wf.run()
