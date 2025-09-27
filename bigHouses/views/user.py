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
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ? ",
        (username, )
    )
    # since only 1 result:
    user = cur_user.fetchone()
    # Error: User DNE
    if user is None:
        flask.abort(404)

    # RELATIONSHIP w logname -> if result exists: true
    cur_rel = connection.execute(
        "SELECT username1, username2 "
        "FROM following "
        "WHERE username1 = ? AND username2 = ? ",
        (logname, username)
    )
    rel = cur_rel.fetchall()
    if rel:
        user['logname_follows_user'] = True
    else:
        user['logname_follows_user'] = False

    # NUM_POSTS: count # of rows from posts
    # where post.owner = username
    cur_posts = connection.execute(
        "SELECT COUNT(*) AS num_posts "
        "FROM posts "
        "WHERE owner = ? ",
        (username, )
    )
    num_posts = cur_posts.fetchall()
    user['num_posts'] = num_posts[0]['num_posts']

    # FOLLOWER/FOLLOWING: iterate grab # of rows from follow table
    cur_followers = connection.execute(
        "SELECT COUNT(*) AS followers "
        "FROM following "
        "WHERE username2 = ? ",
        (username, )
    )
    followers = cur_followers.fetchall()
    user['followers'] = followers[0]['followers']

    cur_following = connection.execute(
        "SELECT COUNT(*) AS following "
        "FROM following "
        "WHERE username1 = ? ",
        (username, )
    )
    following = cur_following.fetchall()
    user['following'] = following[0]['following']

    # POSTS: get image links
    cur_posts = connection.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner = ? ",
        (username, )
    )
    user['posts'] = cur_posts.fetchall()

    # Ship n send as context
    context = {"logname": logname, "user": user}
    return flask.render_template("user.html", **context)
