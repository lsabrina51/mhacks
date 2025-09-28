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

    # Get all users except the current user
    all_users = connection.execute(
        """
        SELECT DISTINCT uniqname, name, img_url
        FROM users
        WHERE uniqname != ?
        """,
        (logname, )
    ).fetchall()

    # Add database info to context
    context = {"logname": logname, "all_users": all_users}

    return flask.render_template("explore.html", **context)
