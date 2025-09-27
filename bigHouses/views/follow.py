"""bigHouses follower/following view and methods."""
import flask
import bigHouses


@bigHouses.app.route('/users/<username>/followers/')
def show_follower(username):
    """Display users/<username>/followers/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    connection = bigHouses.model.get_db()

    user_url_slug = connection.execute(
        """
        SELECT username FROM users
        WHERE username = ? LIMIT 1
        """,
        (username, )
    )
    user_url_slug = user_url_slug.fetchone()
    if not user_url_slug:
        flask.abort(404)

    logname = flask.session.get('username')
    # Query database
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 = ? ",
        (username,)
    )

    following = cur.fetchall()

    followers = []
    for f in following:
        user = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ? ",
            (f['username1'],)
        )
        user = user.fetchall()

        f['pfp'] = user[0]['filename']

        # RELATIONSHIP with logname -> if result exists: true
        cur_rel = connection.execute(
            "SELECT username1, username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ? ",
            (logname, f['username1'])
        )
        rel = cur_rel.fetchall()

        if rel:
            f['logname_follows_user'] = True
        else:
            f['logname_follows_user'] = False

        followers.append(f)

    # print(f"Final followers object:", followers)

    # Add database info to context
    context = {"logname": logname,
               "username": username, "followers": followers}

    return flask.render_template("followers.html", **context)


@bigHouses.app.route('/users/<username>/following/')
def show_following(username):
    """Display /users/<username>/following/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # username = flask.session.get("username")
    # Connect to database
    connection = bigHouses.model.get_db()

    user_url_slug = connection.execute(
        """
        SELECT username FROM users
        WHERE username = ? LIMIT 1
        """,
        (username, )
    )
    user_url_slug = user_url_slug.fetchone()
    if not user_url_slug:
        flask.abort(404)

    logname = flask.session.get('username')

    # Query database
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ",
        (username,)
    )

    follower = cur.fetchall()

    following = []
    for f in follower:
        user = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ? ",
            (f['username2'],)
        )
        user = user.fetchall()

        f['pfp'] = user[0]['filename']

        # RELATIONSHIP with logname -> if result exists: true
        cur_rel = connection.execute(
            "SELECT username1, username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ? ",
            (logname, f['username2'])
        )
        rel = cur_rel.fetchall()

        if rel:
            f['logname_follows_user'] = True
        else:
            f['logname_follows_user'] = False

        following.append(f)

    # print(f"Final followers object:", followers)

    # Add database info to context
    context = {"logname": logname,
               "username": username, "following": following}

    return flask.render_template("following.html", **context)


@bigHouses.app.route("/following/", methods=["POST"])
def update_following():
    """Routes the post method following and unfollowing a user."""
    logname = flask.session.get('username')
    connection = bigHouses.model.get_db()
    sec_username = flask.request.form.get("username")

    if flask.request.form.get("operation") == "follow":

        follow_stat = connection.execute(
            """
            SELECT username1, username2
            FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, sec_username)
        )

        follow_stat = follow_stat.fetchone()

        if follow_stat:
            # we shouldn't be following so we want it to be NONE
            flask.abort(409)

        connection.execute(
            """
            INSERT INTO following(username1, username2)
            VALUES (?, ?)
            """,
            (logname, sec_username)
        )
        connection.commit()

    elif flask.request.form.get("operation") == "unfollow":

        follow_stat = connection.execute(
            """
            SELECT username1, username2
            FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, sec_username)
        )

        follow_stat = follow_stat.fetchone()

        if not follow_stat:
            # we shouldn't be following so we want it to be NONE
            flask.abort(409)

        connection.execute(
            """
            DELETE FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, sec_username)
        )
        connection.commit()

    target = flask.request.args.get('target')
    if not target:
        return flask.redirect(flask.url_for('show_index', username=logname))

    # return flask.redirect(flask.url_for('show_following'))
    return flask.redirect(target)
