from functools import wraps
from flask import session, redirect
import datetime

def requires_auth(f):
    """Wrapper function to prompt user to authenticate."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'access_token' not in session:
            # Redirect to Login page
            return redirect('/login')
        if session["token_expires_in"] < datetime.datetime.now():
            # If the access token is expired, require the user to login again
            return redirect('/login')

        return f(*args, **kwargs)
    return decorated