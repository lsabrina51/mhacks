"""bigHouses explore view."""
import flask
import bigHouses
from bigHouses.views.recommendations import (
    get_user_with_preferences, 
    get_filtered_housing, 
    RecommendationService,
    get_simple_recommendations
)
import os

# importing module
import logging
import json

import pprint  # for pretty-printing posts in logs

# ---------------------------
# Logging configuration
# ---------------------------
logging.basicConfig(
    filename="explore.log",
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="w"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Test messages
logger.debug("Harmless debug Message")
logger.info("Just an information")
logger.warning("Its a Warning")
logger.error("Did you try to divide by zero")
logger.critical("Internet is down")

@bigHouses.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    
    if 'username' not in flask.session:
        # return flask.redirect(flask.url_for('show_login'))
        return flask.render_template("index.html")

    logname = flask.session.get('username')

    # Connect to database
    connection = bigHouses.model.get_db()

    # fetch posts based on user preference 
    posts_info = connection.execute(
        "SELECT housing_id, contact_student_uniqname, street_address, city, zip_code, state, monthly_rent, contact_student_uniqname "
        "FROM posts "
        "INNER JOIN users "
        "ON users.uniqname = ? "
        "AND users.move_in_date >= posts.availability_start "
        "AND users.move_out_date <= posts.availability_end "
        "AND (users.house_type_pref IS NULL OR users.house_type_pref = posts.house_type) "
        "AND (users.room_type_pref IS NULL OR users.room_type_pref = posts.room_type) "
        "AND (users.budget IS NULL OR posts.monthly_rent <= users.budget) "
        "AND ((users.car = 1 AND posts.parking = 1) OR users.car = 0) "
        "ORDER BY posts.distance_from_campus DESC ",
        (logname,)
    ).fetchall()

    # fetch all images and owner for each post
    posts = []
    for post in posts_info:
        postid = post["housing_id"]

        # Fetch all images for this post
        image_info = connection.execute(
            "SELECT img_url FROM images WHERE housing_id = ?",
            (postid,)
        ).fetchone()

        userid = post["contact_student_uniqname"]
        user_info = connection.execute(
            "SELECT name, img_url, uniqname "
            "FROM users "
            "WHERE uniqname = ? ",
            (userid, )
        ).fetchone()
        
        # Append post info
        posts.append({
            "housing_id": post["housing_id"],
            "contact_student_uniqname": post["contact_student_uniqname"],
            "street_address": post["street_address"],
            "city": post["city"],
            "zip_code": post["zip_code"],
            "state": post["state"],
            "monthly_rent": post["monthly_rent"],
            "house_image": image_info["img_url"],
            "user_image": user_info["img_url"], 
            "name": user_info["name"], 
            "uniqname" : user_info["uniqname"]
        })
    # Log the posts and logname
    logger.info("Logged in user: %s", logname)
    logger.info("Posts fetched: %s", json.dumps(posts, indent=2))

    # Don't show recommendations by default - only after form submission
    return flask.render_template("explore.html", posts=posts, logname=logname, recommendations=[])


@bigHouses.app.route('/explore/dream-search', methods=['POST'])
def dream_place_search():
    """Handle dream place search form submission."""
    
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session.get('username')
    dream_query = flask.request.form.get('query', '').strip()
    
    if not dream_query:
        flask.flash('Please describe your dream place!', 'error')
        return flask.redirect('/explore/')

    try:
        # Get user data and housing options
        user_data = get_user_with_preferences(logname)
        available_housing = get_filtered_housing(user_data)
        
        # Generate AI recommendations with dream description
        if os.getenv('GOOGLE_API_KEY'):
            rec_service = RecommendationService()
            recommendations = rec_service.get_housing_recommendations(
                user_data, available_housing, dream_query
            )
        else:
            # Fallback recommendations
            recommendations = get_simple_recommendations(user_data, available_housing)
            # Add dream query context to the reason
            for rec in recommendations:
                rec['reason'] = f"Based on '{dream_query}': {rec['reason']}"
        
        # Get regular posts as well
        connection = bigHouses.model.get_db()
        posts_info = connection.execute(
            "SELECT housing_id, contact_student_uniqname, street_address, city, zip_code, state, monthly_rent, contact_student_uniqname "
            "FROM posts "
            "INNER JOIN users "
            "ON users.uniqname = ? "
            "AND users.move_in_date >= posts.availability_start "
            "AND users.move_out_date <= posts.availability_end "
            "AND (users.house_type_pref IS NULL OR users.house_type_pref = posts.house_type) "
            "AND (users.room_type_pref IS NULL OR users.room_type_pref = posts.room_type) "
            "AND (users.budget IS NULL OR posts.monthly_rent <= users.budget) "
            "AND ((users.car = 1 AND posts.parking = 1) OR users.car = 0) "
            "ORDER BY posts.distance_from_campus DESC ",
            (logname,)
        ).fetchall()

        posts = []
        for post in posts_info:
            postid = post["housing_id"]
            image_info = connection.execute(
                "SELECT img_url FROM images WHERE housing_id = ?",
                (postid,)
            ).fetchone()

            userid = post["contact_student_uniqname"]
            user_info = connection.execute(
                "SELECT name, img_url, uniqname "
                "FROM users "
                "WHERE uniqname = ? ",
                (userid, )
            ).fetchone()
            
            posts.append({
                "housing_id": post["housing_id"],
                "contact_student_uniqname": post["contact_student_uniqname"],
                "street_address": post["street_address"],
                "city": post["city"],
                "zip_code": post["zip_code"],
                "state": post["state"],
                "monthly_rent": post["monthly_rent"],
                "house_image": image_info["img_url"],
                "user_image": user_info["img_url"], 
                "name": user_info["name"], 
                "uniqname" : user_info["uniqname"]
            })

        # Log the search
        logger.info("Dream place search by %s: '%s'", logname, dream_query)
        logger.info("AI Recommendations: %s", json.dumps(recommendations, indent=2))

        # Add success message
        flask.flash(f'Found recommendations based on: "{dream_query}"', 'success')
        
        return flask.render_template("explore.html", 
                                   posts=posts, 
                                   logname=logname, 
                                   recommendations=recommendations,
                                   dream_query=dream_query)
        
    except Exception as e:
        logger.error(f"Error in dream place search: {e}")
        flask.flash('Sorry, there was an error processing your request. Please try again.', 'error')
        return flask.redirect('/explore/')
