from setuptools import setup, find_packages

setup(
    name="pyslicer",
    version="0.2.2",
    packages=find_packages(),
    py_modules=["pyslicer"],

    # Required dependencies
    install_requires=[
        "numpy",
        "pandas",
        "slicer"
    ],

    # Optional extras
    extras_require={
        "extended": [
            "shapely",
            "matplotlib",
            "opencv-python"
        ]
    }
)