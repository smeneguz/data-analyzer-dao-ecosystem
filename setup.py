# setup.py
from setuptools import setup, find_packages

setup(
    name="capire_dati_kaggle",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'pandas>=2.0.0',
        'kagglehub>=0.1.0',
        'python-dotenv>=0.19.0',
    ],
    entry_points={
        'console_scripts': [
            'capire_dati_kaggle=src.presentation.cli.main:cli',
        ],
    },
    author="Silvio Meneguzzo",
    author_email="meneguzzosilvio@gmail.com",
    description="A tool for analyzing DAO ecosystems across multiple platforms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/smeneguz/data-analyzer-dao-ecosystem.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)