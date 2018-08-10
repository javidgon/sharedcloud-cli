from setuptools import setup

setup(
    name='sharedcloud',
    version='1.0.0',
    py_modules=['sharedcloud'],
    install_requires=[
        'click'
    ],
    entry_points='''
        [console_scripts]
        sharedcloud=sharedcloud:cli1
    '''
)