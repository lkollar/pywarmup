#!/usr/bin/env python
import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="pywarmup",
    version="0.1.1",
    description="Client library for Warmup thermostats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache",
    author="Laszlo Kiss Kollar",
    author_email="kiss.kollar.laszlo@gmail.com",
    install_requires=["requests"],
    url="https://github.com/lkollar/pywarmup",
    package_dir={"": "src"},
    packages=["pywarmup"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License ",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries",
    ],
)
