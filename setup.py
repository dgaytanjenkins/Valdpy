"""Setup configuration for valdpy package"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="valdpy",
    version="0.1.1",
    author="Danny Gaytan-Jenkins",
    author_email="dgaytanj@uoregon.edu",
    description="Python SDK for VALD Performance APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dgaytanjenkins/Valdpy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    keywords="vald performance testing forcedecks dynamo",
    project_urls={
        "Bug Reports": "https://github.com/dgaytanjenkins/Valdpy/issues",
        "Documentation": "https://github.com/dgaytanjenkins/Valdpy#readme",
        "Source Code": "https://github.com/dgaytanjenkins/Valdpy",
    },
)
