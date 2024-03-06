from setuptools import find_packages, setup
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='langtrace-python-sdk',  # Choose a unique name for PyPI
    version='1.0.12',
    author='Scale3 Labs',
    license= "AGPL-3.0-or-later",
    author_email='ali@scale3labs.com',
    maintainer=['Karthik Kalyanaraman', 'Ali Waleed', 'Rohit Kadhe'],
    description='Python SDK for LangTrace',
    long_description="LangTrace - Python SDK",
    long_description_content_type='text/markdown',
    url='https://github.com/Scale3-Labs/langtrace-python-sdk',  # Project home page
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=required,
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=False,  # To include non-code files specified in MANIFEST.in
)
