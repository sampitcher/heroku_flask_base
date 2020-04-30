This is a framework for a flask web app that can connect to a postgres database and be hosted on Heroku

1. Change the name of heroku_flask_base.py to NAME_OF_YOUR_APP.py
2. Change the procfile to ```web: flask db upgrade; gunicorn NAME_OF_YOUR_APP:app```
3. Update the models file to include your database schemas