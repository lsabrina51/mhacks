"""bigHouses explore view."""
import flask
import bigHouses


@bigHouses.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    connection = bigHouses.model.get_db()
    logname = flask.session.get('username')

    followed = connection.execute(
        """
        SELECT DISTINCT users.username AS username
        FROM users
        JOIN following
        ON (users.username == following.username2 AND following.username1 = ?)
        """,
        (logname, )
    )

    followed = followed.fetchall()

    names_followed = [logname]
    for diction in followed:
        names_followed.append(diction['username'])

    # sqlite3 var/bigHouses.sqlite3
    query = f"""
    SELECT DISTINCT username, filename
    FROM users
    WHERE username NOT IN ({', '.join(['?'] * len(names_followed))})
    """
    not_follow = connection.execute(query, tuple(names_followed))

    not_follow = not_follow.fetchall()

    # Add database info to context
    context = {"logname": logname, "not_following": not_follow}

    return flask.render_template("explore.html", **context)
