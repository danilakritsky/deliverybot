from flask import Flask, send_from_directory


app = Flask(__name__, static_url_path="/static/photos")


# https://naysan.ca/2021/02/28/flask-101-serve-images/
@app.route("/photos/<photo_name>")
def send_photo(photo_name):
    return send_from_directory("./static/photos", f"{photo_name}")
