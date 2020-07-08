from setuptools import setup, find_packages

setup(
    name="scihub-client",
    version="0.1",  # TODO: versioning
    description="Client for downloading papers from scihub",
    url="https://www.github.com/lkirk/scihub-client",
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4"],
)
