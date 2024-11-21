from StereoX2 import *
from setuptools import setup, find_packages

setup(
    name="StereoX2",
    version="0.1.0",
    author="KANG CHANYOUNG",
    author_email="cykang@keeworks.com",
    description="Stereo Camera Library",
    url="https://github.com/BackGwa/StereoX2",
    install_requires=[
        "numpy>=2.1.2",
        "opencv-python>=4.10.0.84"
    ],
    packages = find_packages(),
    python_requires=">=3.11.10",
)