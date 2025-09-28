"""bigHouses development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = (
        b"\x80\xbc:'x\xa0\xb00\xb8\xf7>Y\xd6%\xb7\x0e\t%\x80$\xf8\xcf\x08\xeb"
            )
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
bigHouses_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = bigHouses_ROOT/'var'/'uploads'
# FOR DEPLOYING TO AWS USE BELOW:
# UPLOAD_FOLDER = pathlib.Path('/var/www/uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/bigHouses.sqlite3
DATABASE_FILENAME = bigHouses_ROOT/'var'/'bighouses.sqlite3'
