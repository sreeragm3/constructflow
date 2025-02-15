venv:

    python -m venv debugclub
    debugclub\Scripts\activate

installing dependencies:

    pip install -r requirements.txt

for automatically reloading when you make changes to your code :
    $env:FLASK_APP = "main"
    $env:FLASK_ENV = "development"
    $env:FLASK_APP = "main"
    flask run --debug

    

