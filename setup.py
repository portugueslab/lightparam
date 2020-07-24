from setuptools import setup, find_namespace_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="lightparam",
    version="0.4.3",
    author="Vilim Stich, Luigi Petrucco",
    author_email="vilim@neuro.mpg.de",
    packages=find_namespace_packages(exclude=("docs", "tests*")),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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