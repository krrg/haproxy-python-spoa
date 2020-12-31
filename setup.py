import pathlib
from setuptools import setup, find_packages

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name="haproxyspoa",
    version="0.0.1",
    description="A pure-python asyncio implementation of an HAProxy Stream Processing Offload Agent (SPOA)",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/krrg/haproxy-python-spoa",
    author="Ken Reese",
    author_email="krrgithub@gmail.com",
    license="Apache 2",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
    ],
    packages=find_packages(exclude=("example", "tests")),
    # include_package_data=True,
    install_requires=[],
)
