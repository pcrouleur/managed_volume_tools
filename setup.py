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
        mvtool=mvtool:cli
        managed_volume_user=managed_volume_user:main
    '''
)
