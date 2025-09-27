"""REST API for posts."""
import flask
import bigHouses


@bigHouses.app.route('/api/v1/')
def get_list():
    """Return list of services."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
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
    latest_pid = flask.request.args.get("postid_lte", default=None, type=int)

    num_offset = size * pages
    # print(num_offset)

    if latest_pid is None:
        cur = connection.execute(
          "SELECT postid FROM posts "
          "INNER JOIN following "
          "ON (posts.owner = ? OR (following.username1 = ? AND"
          " posts.owner = following.username2)) "
          "ORDER BY posts.postid DESC "
          "LIMIT 1",
          (username, username)
        ).fetchone()
        latest_pid = cur['postid']

    if (size < 1) or (pages < 0):
        return flask.jsonify({
          "message": "Bad Request",
          "status_code": 400
        }), 400

    cur = connection.execute(
        "SELECT postid "
        "FROM posts "
        "INNER JOIN following "
        "ON (posts.owner = ? OR (following.username1 = ? AND"
        " posts.owner = following.username2)) "
        "WHERE posts.postid <= ? "
        "GROUP BY posts.postid "
        "ORDER BY posts.postid DESC "
        "LIMIT ? OFFSET ? ",
        (username, username, latest_pid, size, num_offset)
    )

    ten_posts = cur.fetchall()
    for post in ten_posts:
        post['url'] = "/api/v1/posts/" + str(post['postid']) + "/"

    base_url = "/api/v1/posts/"
    query = []

    if "size" in flask.request.args:
        query.append("size=" + str(size))
    if "page" in flask.request.args:
        query.append("page=" + str(pages))
    if "postid_lte" in flask.request.args:
        query.append("postid_lte=" + str(latest_pid))

    full_url = base_url + ("?" + "&".join(query) if query else "")

    if len(ten_posts) < size:
        next_url = ""
    else:
        next_url = (base_url + "?size=" + str(size) + "&page=" +
                    str(pages + 1) + "&postid_lte=" + str(latest_pid))

    context = {"next": next_url,
               "results": ten_posts,
               "url": full_url
               }

    return flask.jsonify(**context)


@bigHouses.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return the details for one post."""
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
        logname = flask.session.get("username")
    else:
        logname = flask.request.authorization["username"]

    # start of sql
    connection = bigHouses.model.get_db()

    # Post IDs that are out of range should return a 404 error.
    post_info = connection.execute(
      """
      SELECT *
      FROM posts
      WHERE posts.postid = ?
      """,
      (postid_url_slug, )
    ).fetchone()

    if post_info is None:
        error_context = {
            "message": "Not Found",
            "status_code": 404
            }
        return flask.jsonify(**error_context), 404

    owner_info = connection.execute(
          "SELECT filename "
          "FROM users "
          "WHERE username = ? ",
          (post_info["owner"], )
    ).fetchone()

    comments_info = connection.execute(
          "SELECT commentid, owner, text "
          "FROM comments "
          "WHERE postid = ?"
          "ORDER BY commentid ASC ",
          (postid_url_slug, )
      ).fetchall()

    for comment in comments_info:
        comment["lognameOwnsThis"] = logname == comment['owner']
        comment["ownerShowUrl"] = f'/users/{comment["owner"]}/'
        comment["url"] = f"/api/v1/comments/{comment['commentid']}/"

    base_likes_info = connection.execute(
          "SELECT owner, likeid, COUNT(*) as numLikes "
          "FROM likes "
          "WHERE likes.postid = ?",
          (postid_url_slug, )
      ).fetchall()

    likes_info = {}
    likes_info["numLikes"] = base_likes_info[0]["numLikes"]
    likes_info["lognameLikesThis"] = False
    likes_info["url"] = None

    for like in base_likes_info:
        if logname == like["owner"]:
            likes_info["url"] = f"/api/v1/likes/{str(like['likeid'])}/"
            likes_info["lognameLikesThis"] = True

    context = {
        "comments": comments_info,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": post_info["created"],
        "imgUrl": f"/uploads/{post_info['filename']}",
        "likes": likes_info,
        "owner": post_info["owner"],
        "ownerImgUrl": f"/uploads/{owner_info['filename']}",
        "ownerShowUrl": f"/users/{post_info['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/"
    }

    return flask.jsonify(**context)


# @bigHouses.app.route("/api/v1/likes/?postid=<postid>", methods=["POST"])
@bigHouses.app.route("/api/v1/likes/", methods=["POST"])
def add_likes():
    """Change the number of likes on a post with <postid>."""
    if (
          not flask.request.authorization
          or "password" not in flask.request.authorization
      ) and ("username" not in flask.session):
        error_context = {
          "message": "Forbidden",
          "status_code": 403
          }
        return flask.jsonify(**error_context), 403

    postid = flask.request.args.get("postid", default=None, type=int)

    if not flask.request.authorization:
        logname = flask.session.get("username")
    else:
        logname = flask.request.authorization["username"]

    connection = bigHouses.model.get_db()

    # Error checking to ensure post exists
    # QUESTION: how do we check if the postid is "out of range"?
    # is this enough or is there a literal upperbound?

    post_info = connection.execute(
      """
      SELECT *
      FROM posts
      WHERE postid = ?
      """,
      (postid, )
    ).fetchone()

    # Postid out of range
    if post_info is None:
        error_context = {
          "message": "Not Found",
          "status_code": 404
          }
        return flask.jsonify(**error_context), 404

    like_info = connection.execute(
      """
      SELECT likeid
      FROM likes
      WHERE postid = ? AND owner = ?
      """,
      (postid, logname)
    ).fetchone()

    # Like already exists:
    if like_info is not None:
        context = {
            "likeid": like_info["likeid"],
            "url": f"/api/v1/likes/{like_info['likeid']}/"
          }
        return flask.jsonify(**context), 200

    # Create like (does not already exist)
    connection.execute(
        """
        INSERT INTO likes(owner, postid)
        VALUES (?, ?)
        """,
        (logname, postid)
      )
    connection.commit()
    like_info = connection.execute(
      """
      SELECT likeid
      FROM likes
      WHERE postid = ? AND owner = ?
      """,
      (postid, logname)
    ).fetchone()

    context = {
        "likeid": like_info["likeid"],
        "url": f"/api/v1/likes/{like_info['likeid']}/"
    }
    return flask.jsonify(**context), 201


@bigHouses.app.route("/api/v1/likes/<likeid>/", methods=["DELETE"])
def delete_likes(likeid):
    """Delete one like."""
    if (
          not flask.request.authorization
          or "password" not in flask.request.authorization
      ) and ("username" not in flask.session):
        error_context = {
            "message": "Forbidden",
            "status_code": 404
            }
        return flask.jsonify(**error_context), 404

    if not flask.request.authorization:
        logname = flask.session.get("username")
    else:
        logname = flask.request.authorization["username"]

    # SQL starts here
    connection = bigHouses.model.get_db()

    # If the likeid does not exist, return 404.
    cur = connection.execute(
      """
      SELECT *
      FROM likes
      WHERE likeid = ?
      """,
      (likeid, )
    ).fetchone()

    # likeid DNE
    if not cur:
        error_context = {
              "message": "Not Found",
              "status_code": 404
              }
        return flask.jsonify(**error_context), 404

    # user does not own the like, return 403.
    if cur["owner"] != logname:
        error_context = {
              "message": "Forbidden",
              "status_code": 403
              }
        return flask.jsonify(**error_context), 403

    connection.execute(
              """
              DELETE FROM likes
              WHERE likeid = ?
              """,
              (likeid, )
          )
    connection.commit()

    # returns NO CONTENT, 204 on successful deletion
    return '', 204


@bigHouses.app.route("/api/v1/comments/", methods=["POST"])
def add_comment():
    """Add a comment to a post."""
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
        logname = flask.session.get("username")
    else:
        logname = flask.request.authorization["username"]

    # SQL starts here
    connection = bigHouses.model.get_db()
    postid = flask.request.args.get("postid", default=None, type=int)
    print(postid)

    # 1. Confirm post exists
    post = connection.execute(
      """
      SELECT *
      FROM posts
      WHERE postid = ?
      """,
      (postid, )
    ).fetchone()

    if post is None:
        error_context = {
              "message": "Not Found",
              "status_code": 404
              }
        return flask.jsonify(**error_context), 404

    # 2. Create new comment
    text = flask.request.get_json().get("text")

    if text is not None:
        connection.execute(
              """
              INSERT INTO comments(owner, postid, text)
              VALUES (?, ?, ?)
              """,
              (logname, postid, text)
            )
        connection.commit()

    # 3. Get commentid of most recent -> SELECT last_insert_rowid()
    comment_info = connection.execute(
      """
      SELECT last_insert_rowid()
      """
    ).fetchone()

    # add other data, return 201
    context = {
        "commentid": comment_info["last_insert_rowid()"],
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": f"/users/{logname}/",
        "text": text,
        "url": f"/api/v1/comments/{comment_info['last_insert_rowid()']}/",
    }
    return flask.jsonify(**context), 201


@bigHouses.app.route("/api/v1/comments/<commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete a comment to a post."""
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
        logname = flask.session.get("username")
    else:
        logname = flask.request.authorization["username"]

    # SQL starts here
    connection = bigHouses.model.get_db()

    # Commentid DNE
    cur = connection.execute(
      """
      SELECT *
      FROM comments
      WHERE commentid = ?
      """,
      (commentid, )
    ).fetchone()

    if cur is None:
        error_context = {
              "message": "Not Found",
              "status_code": 404
              }
        return flask.jsonify(**error_context), 404

    # user does not own the comment, return 403.
    if cur["owner"] != logname:
        error_context = {
              "message": "Forbidden",
              "status_code": 403
              }
        return flask.jsonify(**error_context), 403

    # Delete the comment
    connection.execute(
              """
              DELETE FROM comments
              WHERE commentid = ?
              """,
              (commentid, )
          )
    connection.commit()
    return "", 204
