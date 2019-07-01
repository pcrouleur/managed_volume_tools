from setuptools import setup

setup(
    name='ManagedVolumeTools',
    version='1.0',
    py_modules=['managed_volumes'],
    install_requires=[
        'rubrik_cdm',
        'urllib3',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mv_user=mv_user:cli
        mv_info=mv_info:cli
    '''
)
