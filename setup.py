# setup.py
from setuptools import setup, find_packages

setup(
    name="indy_identity_system",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'python3-indy>=1.16.0',
        'python-dotenv>=0.19.0',
    ],
)