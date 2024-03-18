from setuptools import find_packages, setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="langtrace-python-sdk",  # Choose a unique name for PyPI
    version="{{VERSION_PLACEHOLDER}}",
    author="Scale3 Labs",
    license="AGPL-3.0-or-later",
    author_email="engineering@scale3labs.com",
    maintainer=[
        "Ali Waleed",
        "Darshit Suratwala",
        "Dylan Zuber",
        "Karthik Kalyanaraman",
        "Obinna Okafor",
        "Rohit Kadhe",
        "Yemi Adejumobi",
    ],
    description="Python SDK for LangTrace",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Scale3-Labs/langtrace-python-sdk",  # Project home page
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "trace-attributes",
        "opentelemetry-api",
        "opentelemetry-instrumentation",
        "opentelemetry-sdk",
        "tiktoken",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    include_package_data=False,  # To include non-code files specified in MANIFEST.in
)
