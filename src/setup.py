from setuptools import setup

setup(
    name='silkmoth',
    version='0.1.0',
    packages=['silkmoth', 'silkmoth.test'],
    install_requires=['numpy==2.2.5', 'rapidfuzz==3.13.0', 'ordered-set==4.1.0', 'scipy==1.15.3',]
)