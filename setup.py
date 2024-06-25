from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="PylibMS",
    version="0.6.2",
    author="AbdyyEee",
    packages=find_packages(),
    description="Library for Nintendo's LMS file formats (MSBT, MSBP) for Nintendo 3DS and Wii U and Switch.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbdyyEee/PylibMS",
    keywords=["nintendo", "msbf", "msbt", "msbp",
              "modding", "lms", "libmessagestudio"],
    python_requires=">=3.10",
    include_package_data=True,
    package_data={
        'LMS.Message': ['System.lua'],
    },
)
