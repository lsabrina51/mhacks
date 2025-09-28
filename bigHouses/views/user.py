"""
bigHouses user (sub) view.

URLs include:
/users/<user_url_slug>/
"""
import flask
import bigHouses


@bigHouses.app.route('/users/<username>/')
def show_user(username):
    """Display /users/<username>/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    connection = bigHouses.model.get_db()

    logname = flask.session.get('username')
    cur_user = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE uniqname = ? ",
        (username, )
    )
    # since only 1 result:
    user = cur_user.fetchone()
    # Error: User DNE
    if user is None:
        flask.abort(404)  

    student = dict(user)
    #student["img_url"] = "/uploads/" + student["img_url"]

    cur_post = connection.execute(
        "SELECT street_address, monthly_rent, house_type, housing_id "
        "FROM posts "
        "WHERE contact_student_uniqname = ? ",
        (username, )
    ).fetchall()

    post_list = []
    for post in cur_post:
        images = connection.execute(
            "SELECT img_url FROM images WHERE housing_id = ? ORDER BY img_order ASC",
            (post["housing_id"],)
        ).fetchall()

        post_dict = dict(post)  
        post_dict["images"] = ["/uploads/" + img["img_url"] for img in images]
        post_list.append(post_dict)

    # Ship n send as context
    context = {
        "logname": logname,
        "student": user,
        "posts": post_list
    }
    return flask.render_template("user.html", **context)
