# YY Preprocessing



![PyPI version](https://img.shields.io/pypi/v/yyprep.svg)
[![Documentation Status](https://readthedocs.org/projects/yyprep/badge/?version=latest)](https://yyprep.readthedocs.io/en/latest/?version=latest)

A simple Python pipeline to convert DICOM directories to BIDS format and preprocess them using fMRIPrep. Provides an easy-to-use CLI built with Typer.

Package written specifically for the in-house use in Prof. Yaara Yeshurun's Lab.

* PyPI package: https://pypi.org/project/yyprep/
* Free software: MIT License
* Documentation: https://yyprep.readthedocs.io.


## Overview

This tool helps you:

- Convert DICOM sessions to the BIDS standard using HeuDiConv.
- Update `IntendedFor` fields in BIDS fieldmap JSON files for fMRIPrep.
- Integrate with your own data structure using a user-generated CSV.
- Run the workflow with a single, modern, tab-completing command-line interface.
- Provides an easy wrapper for fMRIPrep to allow reproducible and accessible preprocessing of MRI-derived data.

## Installation

**Recommended**: Install in a virtual environment.

<code>
git clone https://github.com/GalKepler/YY_prep.git
cd yyprep
pip install -e .
</code>

