"""
Setup script for the Annotation Toolkit package.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="annotation-toolkit",
    version="0.1.0",
    author="Nicolas Arias Garcia",
    author_email="ariasgarnicolas@meta.com",
    description="A toolkit for data annotation tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/annotation-toolkit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "pyyaml>=5.1",
        "markdown>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "annotation-toolkit=annotation_toolkit.cli:main",
        ],
    },
)
