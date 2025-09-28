"""
bigHouses index (main) view.

URLs include:
/
"""
# import pathlib
# import uuid
import arrow
import flask
import bigHouses
from bigHouses.views.user import show_user 

LOGGER = flask.logging.create_logger(bigHouses.app)


@bigHouses.app.route('/')
def show_index():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    # connection = bigHouses.model.get_db()

    logname = flask.session.get('username')
    return show_user(logname) 

    # Connect to database
    connection = bigHouses.model.get_db()

    # 
    # cur_user = connection.execute(
    #     "SELECT name, img_url "
    #     "FROM users "
    #     "WHERE uniqname = ? ",
    #     (logname, )
    # )
    # user = cur.fetchone()

    # # fetch posts based on user preference 
    # posts = connection.execute(
    #     "SELECT housing_id, contact_student_uniqname, street_address, city, zip_code, state, monthly_rent "
    #     "FROM posts "
    #     "INNER JOIN users "
    #     "ON users.uniqname = ? "
    #     "AND users.move_in_date >= posts.availability_start "
    #     "AND users.move_out_date <= posts.availability_end "
    #     "AND (users.house_type_pref IS NULL OR users.house_type_pref = posts.house_type) "
    #     "AND (users.room_type_pref IS NULL OR users.room_type_pref = posts.room_type) "
    #     "AND (users.budget IS NULL OR posts.monthly_rent <= users.budget) "
    #     "AND ((users.car = 1 AND posts.parking = 1) OR users.car = 0) "
    #     "AND (users.preferred_location IS NULL OR posts.city = users.preferred_location) "
    #     "ORDER BY posts.distance_from_campus DESC ",
    #     (logname,)
    # )
    # posts = cur.fetchall()

    # fetch all images for each post 



    # cur = connection.execute(
    #     "SELECT * "
    #     "FROM posts "
    #     "INNER JOIN following "
    #     "ON (posts.owner = ? OR (following.username1 = ? AND"
    #     " posts.owner = following.username2)) "
    #     "GROUP BY posts.postid "
    #     "ORDER BY posts.postid DESC ",
    #     (logname, logname)
    # )

    # posts = cur.fetchall()

    # postcontext = []
    # for p in posts:
    #     p['created'] = arrow.get(p['created'], 'YYYY-MM-DD HH:mm:ss')
    #     p['created'] = p['created'].humanize()

    #     # Get comments
    #     comments = connection.execute(
    #         "SELECT owner, text "
    #         "FROM comments "
    #         "WHERE postid = ? "
    #         "ORDER BY commentid ASC",
    #         (p['postid'], )
    #     )
    #     comments = comments.fetchall()

    #     p['comments'] = comments

    #     # get total # of likes for the post:
    #     likes = connection.execute(
    #         "SELECT COUNT(*) AS total_likes "
    #         "FROM likes "
    #         "WHERE postid = ? ",
    #         (p['postid'], )
    #     )

    #     likes = likes.fetchall()

    #     if likes is not None:
    #         p['likes'] = likes[0]['total_likes']

    #         # checking whether the user has already liked this post
    #         liked = connection.execute(
    #             """
    #             SELECT owner
    #             FROM likes
    #             WHERE postid = ?
    #             """,
    #             (p['postid'],)
    #         )

    #         liked = liked.fetchone()
    #         if liked is not None:
    #             p['like_owner'] = liked['owner']

    #     user = connection.execute(
    #         "SELECT filename "
    #         "FROM users "
    #         "WHERE username = ? ",
    #         (p['owner'], )
    #     )
    #     user = user.fetchall()

    #     p['owner_pic'] = user[0]['filename']

    #     postcontext.append(p)

    # # Add database info to context
    # context = {"logname": logname, "posts": postcontext}

    # return flask.render_template("index.html", **context)



# @bigHouses.app.route('/uploads/<filename>')
# def uploads(filename):
#     """Return file image."""
#     if 'username' not in flask.session:
#         return flask.abort(403)

#     # logname = flask.session.get('username')
#     connection = bigHouses.model.get_db()

#     # If an authenticated user attempts to access a file that does not exist
#     # user = connection.execute(
#     #     """
#     #     SELECT filename
#     #     FROM users
#     #     WHERE filename = ?
#     #     """,
#     #     (filename, )
#     # ).fetchone()

#     # post = connection.execute(
#     #     """
#     #     SELECT filename
#     #     FROM posts
#     #     WHERE filename = ?
#     #     """,
#     #     (filename, )
#     # ).fetchone()

#     # if (user is None) and (post is None):
#     #     return flask.abort(404)

#     # Serve the image from the "uploads" directory
#     return flask.send_from_directory(bigHouses.app.config['UPLOAD_FOLDER'],
#                                      filename, as_attachment=True)


# @bigHouses.app.route("/likes/", methods=["POST"])
# def update_likes():
#     """Update likes."""
#     LOGGER.debug("operation = %s", flask.request.form["operation"])
#     LOGGER.debug("postid = %s", flask.request.form["postid"])

#     # 2nd option request.form.get("postid")
#     post_id = flask.request.form["postid"]

#     logname = flask.session.get('username')
#     connection = bigHouses.model.get_db()

#     if flask.request.form["operation"] == "like":
#         # check if trying to like an already liked post
#         liked = connection.execute(
#             """
#             SELECT postid
#             FROM likes
#             WHERE (postid = ? AND owner = ?)
#             """,
#             (post_id, logname)
#         )
#         liked = liked.fetchone()

#         if liked:
#             flask.abort(409)

#         connection.execute(
#             """
#             INSERT INTO likes(owner, postid)
#             VALUES (?, ?)
#             """,
#             (logname, post_id)
#         )
#         connection.commit()

#     elif flask.request.form["operation"] == "unlike":
#         # check if trying to unlike a post they have not liked
#         never_liked = connection.execute(
#             """
#             SELECT postid
#             FROM likes
#             WHERE (postid = ? AND owner = ?)
#             """,
#             (post_id, logname)
#         )
#         never_liked = never_liked.fetchone()

#         if not never_liked:
#             flask.abort(409)

#         connection.execute(
#             """DELETE FROM likes
#             WHERE (owner = ? AND postid = ?) """,
#             (logname, post_id)
#         )

#         connection.commit()

#     target = flask.request.args.get('target')
#     if not target:
#         return flask.redirect('/')

#     return flask.redirect(target)


# @bigHouses.app.route("/comments/", methods=["POST"])
# def update_comments():
#     """Update comments."""
#     LOGGER.debug("operation = %s", flask.request.form["operation"])
#     # LOGGER.debug("postid = %s", flask.request.form["postid"])

#     logname = flask.session.get('username')
#     connection = bigHouses.model.get_db()

#     if flask.request.form["operation"] == "create":
#         # check if trying to  an already liked post
#         comment_text = flask.request.form.get("text")
#         post_id = flask.request.form["postid"]

#         if not comment_text:
#             flask.abort(400)

#         connection.execute(
#             """
#             INSERT INTO comments(owner, postid, text)
#             VALUES (?, ?, ?)
#             """,
#             (logname, post_id, comment_text)
#         )

#         connection.commit()

#     elif flask.request.form["operation"] == "delete":
#         # If a user tries to delete a comment that they do not own
#         comment_id = flask.request.form.get("commentid")

#         never_commented = connection.execute(
#             """
#             SELECT owner
#             FROM comments
#             WHERE commentid = ?
#             """,
#             (comment_id, )
#         )

#         never_commented = never_commented.fetchone()

#         if never_commented['owner'] != logname:
#             flask.abort(403)

#         connection.execute(
#             """
#             DELETE FROM comments
#             WHERE commentid = ?
#             """,
#             (comment_id, )
#         )

#         connection.commit()

#     target = flask.request.args.get('target')
#     if not target:
#         return flask.redirect('/')

#     return flask.redirect(target)
