from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()
setup(
    name="PylibMS",
    version="0.1.2",
    author="AbdyyEee",
    packages=find_packages(),
    license="mit",
    description="Library for Nintendo's LMS file formats (MSBT, MSBP) for Nintendo 3DS and Wii U",
    long_description=description,
    keywords=["nintendo", "msbf", "msbt", "msbp", "modding", "lms", "libmessagestudio"],
    python_requires=">=3.10"
)