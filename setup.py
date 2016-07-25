import os

from pyreleaseplugin import CleanCommand, ReleaseCommand, PyTest
from setuptools import find_packages, setup


def read(fname):
    """Utility function to read the README file into the long_description."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires_list = ["boto3>=1.3.1"]
tests_require = ["dill>=0.2.5", "moto>=0.4.23", "pytest>=2.9"]


version_file = "model_storage/_version.py"
with open(version_file) as fp:
    exec(fp.read())

setup(
    name="model_storage",
    version=__version__,
    author="The Discovery Team",
    author_email="discovery-l@socrata.com",
    description=("A module for loading and saving models"),
    license="TBD",
    url="https://github.com/socrata/model-storage-common",
    install_requires=install_requires_list,
    tests_require=tests_require,
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Socrata",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={"test": PyTest, "clean": CleanCommand, "release": ReleaseCommand})
