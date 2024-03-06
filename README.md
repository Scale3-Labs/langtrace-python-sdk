# langtrace-python-sdk

export PYTHONPATH="/Users/karthikkalyanaraman/work/langtrace/python-sdk:$PYTHONPATH"

## Steps to run

1. From your root directory, create a virtualenv for installing your dependencies
    ```
    python -m venv pysdk
    ```
2. Activate the virtualenv
    ```
    source pysdk/bin/activate
    ```
3. Install the dependencies
   ```
    pip install -r requirements.txt
    ```
4. Run the example and see the traces on the terminal
   ```
   python src/run_example.py
   ```

## How to build and publish a new package

1. Remove the build/ and dist/ folders from the root
   ```
   rm -rf dist/
   rm -rf build/
   ```
2. Bump the version in setup.py

3. Build the package
   ```
   python3 setup.py sdist bdist_wheel
   ```

4. Upload the package
   ```
   twine upload dist/*
   ```

Note: For API Key, reach out to Karthik/Ali