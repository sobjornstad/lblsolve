"""
setup.py -  setuptools configuration for esc
"""

import setuptools

long_description = "my description"
#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="lbltools",
    version="0.1.0",
    author="Soren I. Bjornstad",
    author_email="contact@sorenbjornstad.com",
    description="solitaire solver for La Belle Lucie",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sobjornstad/lblsolve",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'windows-curses; platform_system == "Windows"',
    ],
    entry_points={
        "console_scripts": [
            "lbl = lblsolve.cards:main"
        ],
    },
    python_requires='>=3.7',
)
