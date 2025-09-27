"""Views, one for each bigHouses page."""
from bigHouses.views.index import show_index
from bigHouses.views.follow import show_follower
from bigHouses.views.follow import show_following
from bigHouses.views.user import show_user
from bigHouses.views.explore import show_explore
from bigHouses.views.post import show_post
from bigHouses.views.account import show_login
from bigHouses.views.account import show_create
from bigHouses.views.account import show_delete
from bigHouses.views.account import show_edit
from bigHouses.views.account import show_password
from bigHouses.views.account import auth
