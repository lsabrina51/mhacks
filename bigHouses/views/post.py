"""bigHouses post view and methods."""
import uuid
import pathlib
import arrow
import flask
import bigHouses


@bigHouses.app.route('/posts/<post_id>/')
def show_post(post_id):
    """Display a post's route."""
    # Connect to database
    connection = bigHouses.model.get_db()

    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    logname = flask.session.get('username')

    # sqlite3 var/bigHouses.sqlite3
    post_info = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ? ",
        (post_id, )
    )

    post_info = post_info.fetchone()

    if post_info is None:
        flask.abort(404)

    post_info['created'] = arrow.get(post_info['created'],
                                     'YYYY-MM-DD HH:mm:ss')
    post_info['created'] = post_info['created'].humanize()

    # get all comments
    comments = connection.execute(
        "SELECT owner, text "
        "FROM comments "
        "WHERE postid = ?"
        "ORDER BY commentid ASC",
        (post_id, )
    )
    comments = comments.fetchall()

    post_info['comments'] = comments

    # get total likes
    likes = connection.execute(
        "SELECT COUNT(*) AS total_likes "
        "FROM likes "
        "WHERE postid = ? ",
        (post_id, )
    )

    likes = likes.fetchall()
    post_info['likes'] = likes[0]['total_likes']

    # get poster pfp
    user = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ? ",
        (post_info['owner'], )
    )

    user = user.fetchall()
    post_info['owner_pic'] = user[0]['filename']

    # get whether post is liked by user
    like = connection.execute(
        """
        SELECT owner
        FROM likes
        WHERE postid = ?
        """,
        (post_id, )
    )
    like = like.fetchone()

    if not like:
        post_info['like_owner'] = 0
    else:
        post_info['like_owner'] = like['owner']

    # Add database info to context
    context = {"logname": logname, "post": post_info}
    return flask.render_template("post.html", **context)


@bigHouses.app.route("/posts/", methods=["POST"])
def post():
    """Creates/Deletes Post."""
    logname = flask.session.get('username')
    connection = bigHouses.model.get_db()

    if flask.request.form["operation"] == "create":
        # Unpack flask object
        fileobj = flask.request.files.get("file")
        # If a user tries to create a post with an empty file, then abort(400).
        if not fileobj or fileobj.filename == "":
            flask.abort(400)

        filename = fileobj.filename

        # Compute base name (filename without directory).
        # We use a UUID to avoid clashes with existing files,
        # and ensure that the name is compatible with the
        # filesystem. For best practive, we ensure uniform
        # file extensions (e.g. lowercase).
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = bigHouses.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        created = flask.request.form["create_post"]

        connection.execute(
            """
            INSERT INTO posts(filename, owner, created)
            VALUES(?, ?, ?)
            """,
            (uuid_basename, logname, created, )
        )

        connection.commit()

    elif flask.request.form["operation"] == "delete":
        post_id = flask.request.form["postid"]
        posts = connection.execute(
            """
            SELECT filename, owner
            FROM posts
            WHERE postid = ?
            """,
            (post_id, )
        ).fetchone()

        # If a user tries to delete a post that they do not own
        if posts["owner"] != logname:
            flask.abort(403)

        # Delete from filesystem
        path = bigHouses.app.config["UPLOAD_FOLDER"]/posts["filename"]
        path.unlink()

        connection.execute(
            """
            DELETE FROM posts
            WHERE postid = ?
            """,
            (post_id, )
        )

        connection.commit()

    target = flask.request.args.get('target')
    if not target:
        return flask.redirect(flask.url_for('show_user', username=logname))

    return flask.redirect(target)
