"""bigHouses accounts view and methods."""
import hashlib
import uuid
import pathlib
import flask
import bigHouses


# QUESTION: idk what this is checking if we check for logged in in show_index?
# QUESTION: do all our routes need a "get" method?
@bigHouses.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Display /login/ route."""
    # 1. check if user is logged in
    # 2. if yes: route to '/'
    # 3. if no: display form

    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    return flask.render_template("account_login.html")


@bigHouses.app.route('/accounts/create/', methods=['GET'])
def show_create():
    """Display /accounts/create/ route."""
    # if user is signed in:
    if 'username' in flask.session:
        # route to '/accounts/edit/'
        return flask.redirect("/accounts/edit/")

    return flask.render_template("account_create.html")


@bigHouses.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Display /accounts/delete/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # connection = bigHouses.model.get_db()
    logname = flask.session.get('username')

    context = {"logname": logname}
    return flask.render_template("account_delete.html", **context)


@bigHouses.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display /accounts/edit/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    logname = flask.session.get('username')
    connection = bigHouses.model.get_db()

    cur = connection.execute(
        """
        SELECT username, filename, fullname, email
        FROM users
        WHERE username = ?
        """,
        (logname, )
    )

    user = cur.fetchone()
    context = {"logname": logname, "user": user}

    return flask.render_template("account_edit.html", **context)


@bigHouses.app.route('/accounts/password/', methods=['GET'])
def show_password():
    """Display /accounts/password/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session.get('username')
    context = {"logname": logname}
    return flask.render_template("account_password.html", **context)


@bigHouses.app.route('/accounts/auth/', methods=['GET'])
def auth():
    """Check authentication."""
    if 'username' in flask.session:
        return flask.Response(status=200)

    return flask.abort(403)


@bigHouses.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout the user."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    flask.session.clear()
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('show_login'))


@bigHouses.app.route('/accounts/', methods=["POST"])
def accounts():
    """Accounts Post Routes."""
    if flask.request.form.get('operation') == 'login':
        return handle_login()

    if flask.request.form.get('operation') == 'create':
        return handle_create()

    if flask.request.form.get('operation') == 'delete':
        return handle_delete()

    if flask.request.form.get('operation') == 'edit_account':
        return handle_edit_account()

    return handle_update_password()


def handle_login():
    """Handle logging in."""
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    # If the username or password fields are empty, abort(400)
    if not username or not password:
        flask.abort(400)

    # If username and password authentication fails, abort(403)
    # hash this password, compare to user_pass
    connection = bigHouses.model.get_db()
    user_pass = connection.execute(
        """
        SELECT password
        FROM users
        WHERE username = ?
        """,
        (username, )
    ).fetchone()

    # ie. the username dne:
    if user_pass is None:
        flask.abort(403)

    user_pass = user_pass['password']

    # split user_pass based off $ to get salt
    pass_parts = user_pass.split('$')

    algorithm = 'sha512'
    salt = pass_parts[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if password_db_string != user_pass:
        flask.abort(403)

    # Set a session cookie.
    # Reminder: only store minimal information in a session cookie!
    flask.session['username'] = flask.request.form.get('username')

    target = flask.request.args.get('target')
    if not target:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(target)


def handle_create():
    """Handle creating account."""
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files.get('file')

    if (
        not username
        or not password
        or not fullname
        or not email
        or not fileobj
    ):
        flask.abort(400)

    if fileobj.filename == '':
        flask.abort(400)

    connection = bigHouses.model.get_db()
    exis_user = connection.execute(
        """
        SELECT 1
        FROM users
        WHERE username = ?
        """,
        (username, )
    ).fetchone()

    if exis_user:
        flask.abort(409)

    # CREATE THE USER:
    # Compute base name (filename without directory).
    # Use UUID to avoid clashes with existing files,
    # and ensure that the name is compatible with the filesystem.
    # For best practice, we ensure uniform file extensions (e.g.
    # lowercase).
    suffix = pathlib.Path(fileobj.filename).suffix.lower()
    uuid_basename = f"{uuid.uuid4().hex}{suffix}"

    # Save to disk
    fileobj.save(bigHouses.app.config["UPLOAD_FOLDER"]/uuid_basename)

    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join(['sha512', salt, password_hash])

    connection.execute(
        """
        INSERT INTO users(filename, username, password, fullname, email)
        VALUES(?, ?, ?, ?, ?)
        """,
        (uuid_basename, username, password_db_string, fullname, email)
    )
    connection.commit()

    # log the user in and redirect:
    flask.session['username'] = username

    target = flask.request.args.get('target')
    if not target:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(target)


def handle_delete():
    """Display /accounts/delete/ route."""
    if 'username' not in flask.session:
        # this means the user isn't logged in so we should abort
        flask.abort(403)

    else:
        username = flask.session.get('username')
        # password = flask.session.get("password")

        # TO DO need to check at some point if deleting their own account
        connection = bigHouses.model.get_db()
        # first get old filename so can delete from sql db
        old_file = connection.execute(
            """
            SELECT filename
            FROM users
            WHERE username = ?
            """,
            (username, )
        )

        old_file = old_file.fetchone()
        path = pathlib.Path(
            bigHouses.app.config["UPLOAD_FOLDER"])/old_file['filename']
        path.unlink()

        connection.execute(
            """
            DELETE FROM users
            WHERE username = ?
            """,
            (username, )
        )
        connection.commit()

        flask.session.clear()
        # flask.session.pop('username', None)

        target = flask.request.args.get('target')
        if not target:
            return flask.redirect(flask.url_for('show_index'))

        return flask.redirect(target)


def handle_edit_account():
    """Display /accounts/edit/ route."""
    if 'username' not in flask.session:
        flask.abort(403)

    else:
        username = flask.session.get('username')

        fullname = flask.request.form.get('fullname')
        email = flask.request.form.get('email')
        fileobj = flask.request.files.get('file')

        if not (fullname or email):
            flask.abort(400)

        if fileobj:
            # pfp given
            connection = bigHouses.model.get_db()
            # first get old filename so can delete from sql db
            old_file = connection.execute(
                """
                SELECT filename
                FROM users
                WHERE username = ?
                """,
                (username, )
            )

            old_file = old_file.fetchone()
            # file_name = old_file[0]
            path = pathlib.Path(
                bigHouses.app.config["UPLOAD_FOLDER"])/old_file['filename']
            path.unlink()

            # now we need to update the account including the new photo
            filename = fileobj.filename

            # Compute base name (filename without directory).
            # We use a UUID to avoid clashes with existing files,
            # and ensure that the name is compatible with the filesystem.
            # For best practive, we ensure uniform file extensions (e.g.
            # lowercase).
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"

            # Save to disk
            path = pathlib.Path(
                bigHouses.app.config["UPLOAD_FOLDER"])/uuid_basename
            fileobj.save(path)

            connection.execute(
                """
                UPDATE users
                SET fullname = ?, email = ?, filename = ?
                WHERE username = ?
                """,
                (fullname, email, uuid_basename, username)
            )

            connection.commit()

        else:
            # no new photo given

            connection = bigHouses.model.get_db()
            connection.execute(
                """
                UPDATE users
                SET fullname = ?, email = ?
                WHERE username = ?
                """,
                (fullname, email, username)
            )
            connection.commit()

        target = flask.request.args.get('target')
        if not target:
            return flask.redirect(flask.url_for('show_index'))

        return flask.redirect(target)


def handle_update_password():
    """Update user password."""
    if 'username' not in flask.session:
        flask.abort(403)

    else:
        username = flask.session.get('username')
        new_password1 = flask.request.form.get('new_password1')
        new_password2 = flask.request.form.get('new_password2')
        old_password = flask.request.form.get('password')

        if not new_password1 or not new_password2 or not old_password:
            flask.abort(400)

        if new_password1 != new_password2:
            flask.abort(401)

        # compare old password to currently stored password
        connection = bigHouses.model.get_db()
        user_pass = connection.execute(
            """
            SELECT password
            FROM users
            WHERE username = ?
            """,
            (username, )
        )
        user_pass = user_pass.fetchone()['password']

        # ie. the username dne:
        if not user_pass:
            flask.abort(403)

        # split user_pass based off $ to get salt
        salt = user_pass.split('$')[1]
        hash_obj = hashlib.new('sha512')
        password_salted = salt + old_password
        hash_obj.update(password_salted.encode('utf-8'))
        password_db_string = "$".join(['sha512', salt, hash_obj.hexdigest()])

        if password_db_string != user_pass:
            flask.abort(403)
        # we have confirmed old password is true password

        # create new password using hash and salt
        new_salt = uuid.uuid4().hex
        sec_hash_obj = hashlib.new('sha512')
        new_salted_pass = new_salt + new_password1
        sec_hash_obj.update(new_salted_pass.encode('utf-8'))
        storing_password = "$".join(['sha512', new_salt,
                                     sec_hash_obj.hexdigest()])

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE username = ?
            """,
            (storing_password, username)
        )

        connection.commit()

    target = flask.request.args.get("target")
    if not target:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(target)
