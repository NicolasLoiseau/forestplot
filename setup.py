from setuptools import setup, find_packages

setup(
    name='forestplot',
    version='1.0',
    description='Python script to create forest plots',
    author='Nicolas Loiseau',
    packages=find_packages(),
    long_description=open('README.md').read()
)
