from setuptools import find_packages, setup

setup(
    name='python-sdk',  # Choose a unique name for PyPI
    version='0.0.0',
    author='Ali Waleed',
    author_email='ali@scale3labs.com',
    description='LangTrace - Python SDK',
    long_description="LangTrace - Python SDK",
    long_description_content_type='text/markdown',
    url='https://github.com/Scale3-Labs/langtrace-trace-attributes',  # Project home page
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'pydantic>=1.8',  # Example dependency, adjust according to your project's needs
        'typing'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=False,  # To include non-code files specified in MANIFEST.in
)
