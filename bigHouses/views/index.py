"""
bigHouses index (main) view.

URLs include:
/
"""
# import pathlib
# import uuid
# import arrow
import flask
import bigHouses
from bigHouses.views.user import show_user 

LOGGER = flask.logging.create_logger(bigHouses.app)

# FIX WITH EUGENIA CODE
@bigHouses.app.route('/')
def show_index():
    """Display / route."""
    if 'username' not in flask.session:
        # return flask.redirect(flask.url_for('show_login'))
        return flask.render_template("index.html")

    # Connect to database
    # connection = bigHouses.model.get_db()

    logname = flask.session.get('username')
    return show_user(logname) 

    # Connect to database
    # connection = bigHouses.model.get_db()

    # cur_user = connection.execute(
    #     "SELECT name, img_url "
    #     "FROM users "
    #     "WHERE uniqname = ? ",
    #     (logname, )
    # ).fetchone()

    # # fetch posts based on user preference 
    # posts_info = connection.execute(
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
    # ).fetchall()

    # # fetch all images for each post
    # posts = []
    # for post in posts_info:
    #     postid = post["housing_id"]

    #     # Fetch all images for this post
    #     image_info = connection.execute(
    #         "SELECT img_url FROM images WHERE housing_id = ?",
    #         (postid,)
    #     ).fetchone()
        
    #     # Append post info
    #     posts.append({
    #         "housing_id": post["housing_id"],
    #         "contact_student_uniqname": post["contact_student_uniqname"],
    #         "street_address": post["street_address"],
    #         "city": post["city"],
    #         "zip_code": post["zip_code"],
    #         "state": post["state"],
    #         "monthly_rent": post["monthly_rent"],
    #         "images": image_info["img_url"] 
    #     })

    # return render_template("explore.html", username=username, posts=posts)




