import flask 
import os

import bigHouses


@bigHouses.app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Fetch uploaded image."""
    # checks if user is logged in
    if "username" not in flask.session:
        flask.abort(403)

    upload_dir = bigHouses.app.config.get("UPLOAD_FOLDER", "uploads")
    path = os.path.join(upload_dir, filename)
    # Error for when file does not exist and user is logged in
    if not os.path.isfile(path):
        flask.abort(404)
    return flask.send_from_directory(upload_dir, filename)