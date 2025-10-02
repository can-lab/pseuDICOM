from setuptools import setup

def get_version():
    """Get version and version_info from finish_the_job/__meta__.py file."""

    import os
    module_path = os.path.join(os.path.dirname('__file__'), 'pseudicom',
                               '__meta__.py')

    import importlib.util
    spec = importlib.util.spec_from_file_location('__meta__', module_path)
    meta = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(meta)
    return meta.__version__

__version__ = get_version()

setup(
    name = 'pseuDICOM',
    version = __version__,
    packages = ['pseudicom'],
    install_requires = ['nipype',
                        'pydicom',
                        'quickshear'])
