from setuptools import setup

setup(
    name='ManagedVolumeTools',
    version='1.0',
    py_modules=['mv_info', 'mv_user', 'mv_migrate'],
    install_requires=[
        'rubrik_cdm',
        'urllib3',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mv_user=mv_user:cli
        mv_info=mv_info:cli
        mv_migrate=mv_migrate:main
    '''
)
