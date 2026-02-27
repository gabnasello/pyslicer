from setuptools import setup, find_packages

extended_deps = [
    "shapely",
    "matplotlib",
    "opencv-python"
]

setup(
    name="pyslicer",
    version="0.2.2",
    packages=find_packages(),
    py_modules=["pyslicer"],

    install_requires=[
        "numpy",
        "pandas",
        "slicer",
    ],

    extras_require={
        "extended": extended_deps,
        "all": extended_deps
    }
)