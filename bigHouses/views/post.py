"""bigHouses post view and methods."""
import uuid
import pathlib
import flask
import bigHouses


@bigHouses.app.route('/posts/<housing_id>/')
def show_post(housing_id):
    """Display a post's route."""
    # Connect to database
    connection = bigHouses.model.get_db()

    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    logname = flask.session.get('username')

    # Get post information
    post_info = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE housing_id = ? ",
        (housing_id, )
    ).fetchone()

    if post_info is None:
        flask.abort(404)

    # Get images for this housing post
    images = connection.execute(
        "SELECT img_url, img_order "
        "FROM images "
        "WHERE housing_id = ? "
        "ORDER BY img_order ASC",
        (housing_id, )
    ).fetchall()

    # Get contact person information
    contact_info = connection.execute(
        "SELECT name, img_url "
        "FROM users "
        "WHERE uniqname = ?",
        (post_info['contact_student_uniqname'], )
    ).fetchone()

    # Add image and contact data to post
    post_dict = dict(post_info)
    post_dict['images'] = images
    post_dict['contact_name'] = contact_info['name'] if contact_info else None
    post_dict['contact_img_url'] = contact_info['img_url'] if contact_info else None

    # Add database info to context
    context = {"logname": logname, "post": post_dict}
    return flask.render_template("post.html", **context)


@bigHouses.app.route("/posts/", methods=["POST"])
def post():
    """Create or delete a housing post."""
    logname = flask.session.get("username")
    if not logname:
        flask.abort(403)

    connection = bigHouses.model.get_db()

    if flask.request.form["operation"] == "create":
        # Ensure required fields exist
        street_address = flask.request.form.get("street_address")
        city = flask.request.form.get("city")
        state = flask.request.form.get("state")
        zip_code = flask.request.form.get("zip_code")
        monthly_rent = flask.request.form.get("monthly_rent")
        house_type = flask.request.form.get("house_type")
        room_type = flask.request.form.get("room_type")

        if not street_address or not city or not state or not zip_code:
            flask.abort(400)

        # Optional features (checkboxes return 'on' if checked)
        wifi = bool(flask.request.form.get("wifi_included"))
        laundry = bool(flask.request.form.get("laundry"))
        parking = bool(flask.request.form.get("parking"))
        pets = bool(flask.request.form.get("pets_allowed"))
        furnished = bool(flask.request.form.get("furnished"))
        air_conditioning = bool(flask.request.form.get("air_conditioning"))
        heating = bool(flask.request.form.get("heating"))
        utilities_included = bool(flask.request.form.get("utilities_included"))
        weed_friendly = bool(flask.request.form.get("weed_friendly"))
        smoking_friendly = bool(flask.request.form.get("smoking_friendly"))
        drinking_friendly = bool(flask.request.form.get("drinking_friendly"))

        # Availability
        availability_start = flask.request.form.get("availability_start")
        availability_end = flask.request.form.get("availability_end")

        # Insert post into posts table
        cur = connection.execute(
            """
            INSERT INTO posts (
                contact_student_uniqname, street_address, city, state, zip_code,
                monthly_rent, house_type, room_type, wifi_included, laundry, parking, pets_allowed,
                furnished, air_conditioning, heating, utilities_included, weed_friendly,
                smoking_friendly, drinking_friendly, availability_start, availability_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                logname, street_address, city, state, zip_code,
                monthly_rent, house_type, room_type, wifi, laundry, parking, pets,
                furnished, air_conditioning, heating, utilities_included, weed_friendly,
                smoking_friendly, drinking_friendly, availability_start, availability_end
            )
        )
        housing_id = cur.lastrowid  # Get the newly inserted post's ID

        # Handle multiple image uploads
        files = flask.request.files.getlist("images")
        for idx, fileobj in enumerate(files):
            if fileobj and fileobj.filename != "":
                suffix = pathlib.Path(fileobj.filename).suffix.lower()
                filename = f"{uuid.uuid4().hex}{suffix}"

                # Save to uploads directory
                path = pathlib.Path(bigHouses.app.config["UPLOAD_FOLDER"]) / filename
                fileobj.save(path)

                # Insert into images table
                connection.execute(
                    "INSERT INTO images (housing_id, img_url, img_order) VALUES (?, ?, ?)",
                    (housing_id, filename, idx)
                )

        connection.commit()

    elif flask.request.form["operation"] == "delete":
        housing_id = flask.request.form["housing_id"]

        post = connection.execute(
            """
            SELECT contact_student_uniqname
            FROM posts
            WHERE housing_id = ?
            """,
            (housing_id,)
        ).fetchone()

        if not post:
            flask.abort(404)

        # Check ownership
        if post["contact_student_uniqname"] != logname:
            flask.abort(403)

        # Delete images from filesystem + db
        images = connection.execute(
            "SELECT img_url FROM images WHERE housing_id = ?", (housing_id,)
        ).fetchall()
        for img in images:
            path = bigHouses.app.config["UPLOAD_FOLDER"] / img["img_url"]
            if path.exists():
                path.unlink()

        connection.execute("DELETE FROM images WHERE housing_id = ?", (housing_id,))
        connection.execute("DELETE FROM posts WHERE housing_id = ?", (housing_id,))
        connection.commit()

    # Redirect back
    target = flask.request.args.get("target")
    if not target:
        return flask.redirect(flask.url_for("show_user", username=logname))
    return flask.redirect(target)