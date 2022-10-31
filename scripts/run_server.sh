# poetry run flask --app deliverybot/server/app.py run --host=0.0.0.0
# set host to 0.0.0.0 to make it available to other containers
# https://stackoverflow.com/questions/26423984/unable-to-connect-to-flask-app-on-docker-from-host


# GUNICORN
# https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn/#binding-externally
poetry run gunicorn --bind 0.0.0.0:5000 deliverybot.server.app:app