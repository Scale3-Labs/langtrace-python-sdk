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
   python src/entrypoint.py
   ```