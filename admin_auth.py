from functools import wraps
from flask import request, Response
import os


ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password")


def check_auth(username, password):
return username == ADMIN_USER and password == ADMIN_PASS


def require_admin(f):
@wraps(f)
def decorated(*args, **kwargs):
auth = request.authorization
if not auth or not check_auth(auth.username, auth.password):
return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login required"'})
return f(*args, **kwargs)
return decorated
