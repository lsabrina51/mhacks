"""REST API for posts."""
import flask
import bigHouses


@bigHouses.app.route('/api/v1/')
def get_list():
    """Return list of services."""
    context = {
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
        }
    return flask.jsonify(**context)


@bigHouses.app.route('/api/v1/posts/')
def latest_posts():
    """Return the ten latest created posts."""
    if (
          not flask.request.authorization
          or "password" not in flask.request.authorization
      ) and ("username" not in flask.session):
        error_context = {
            "message": "Forbidden",
            "status_code": 403
            }
        return flask.jsonify(**error_context), 403

    if not flask.request.authorization:
        username = flask.session.get("username")
    else:
        username = flask.request.authorization["username"]
    # start of sql
    connection = bigHouses.model.get_db()
    size = flask.request.args.get("size", default=10, type=int)
    pages = flask.request.args.get("page", default=0, type=int)
    latest_pid = flask.request.args.get("housing_id_lte", default=None, type=int)

    num_offset = size * pages

    if latest_pid is None:
        cur = connection.execute(
          "SELECT housing_id FROM posts "
          "ORDER BY housing_id DESC "
          "LIMIT 1",
        ).fetchone()
        latest_pid = cur['housing_id'] if cur else 0

    if (size < 1) or (pages < 0):
        return flask.jsonify({
          "message": "Bad Request",
          "status_code": 400
        }), 400

    cur = connection.execute(
        "SELECT housing_id "
        "FROM posts "
        "WHERE housing_id <= ? "
        "ORDER BY housing_id DESC "
        "LIMIT ? OFFSET ? ",
        (latest_pid, size, num_offset)
    )

    ten_posts = cur.fetchall()
    for post in ten_posts:
        post['url'] = "/api/v1/posts/" + str(post['housing_id']) + "/"

    base_url = "/api/v1/posts/"
    query = []

    if "size" in flask.request.args:
        query.append("size=" + str(size))
    if "page" in flask.request.args:
        query.append("page=" + str(pages))
    if "housing_id_lte" in flask.request.args:
        query.append("housing_id_lte=" + str(latest_pid))

    full_url = base_url + ("?" + "&".join(query) if query else "")

    if ten_posts:
        last_id = ten_posts[-1]["housing_id"]
    else:
        last_id = latest_pid
    next_url = (
        f"{base_url}?size={size}&housing_id_lte={last_id}"
        if len(ten_posts) == size
        else ""
    )

    context = {"next": next_url,
               "results": ten_posts,
               "url": full_url
               }

    return flask.jsonify(**context)


@bigHouses.app.route('/api/v1/posts/<int:housing_id_url_slug>/')
def get_post(housing_id_url_slug):
    """Return the details for one post."""
    if not (
            (flask.request.authorization and "username" in flask.request.authorization and "password" in flask.request.authorization)
            or ("username" in flask.session)
           ):
        error_context = {
          "message": "Forbidden",
          "status_code": 403
          }
        return flask.jsonify(**error_context), 403

    if not flask.request.authorization:
        logname = flask.session.get("username")
    else:
        logname = flask.request.authorization["username"]

    # start of sql
    connection = bigHouses.model.get_db()

    # Housing IDs that are out of range should return a 404 error.
    post_info = connection.execute(
      """
      SELECT *
      FROM posts
      WHERE posts.housing_id = ?
      """,
      (housing_id_url_slug, )
    ).fetchone()

    if post_info is None:
        error_context = {
            "message": "Not Found",
            "status_code": 404
            }
        return flask.jsonify(**error_context), 404

    context = {
        "ownerShowUrl": f"/users/{post_info['contact_student_uniqname']}/",
        "postShowUrl": f"/posts/{housing_id_url_slug}/",
        "housing_id": housing_id_url_slug,
        "url": f"/api/v1/posts/{housing_id_url_slug}/"
    }

    return flask.jsonify(**context)