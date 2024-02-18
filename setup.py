"""Install driverlib."""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="driverlib",
    version="0.0.1",
    author="LKB",
    author_email="cryo.paris.su@gmail.com",
    description="Control your instruments via USB or LAN.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kyrylo-gr/driverlib",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pyvisa",
    ],
)
