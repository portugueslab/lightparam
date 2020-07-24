from distutils.core import setup
from setuptools import find_packages

setup(
    name="lightparam",
    version="0.4.2",
    author="Vilim Stich, Luigi Petrucco",
    author_email="vilim@neuro.mpg.de",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="parameters",
    description="A light, qt-compatible python parametrization package.",
    project_urls={
        "Source": "https://github.com/portugueslab/lightparam",
        "Tracker": "https://github.com/portugueslab/lightparam/issues",
    },
)