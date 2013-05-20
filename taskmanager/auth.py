from models import *
from flask import session
from flask.ext.restless import ProcessingException

def check_auth():
    #TODO: This is a login workaround
    print "Single user mode..."
    if not session.has_key('user'):
        session['user'] = User.query.get(1)
    return True

def api_auth(instance_id=None, **kw):
    if not check_auth():
        raise ProcessingException(message='Not Authorized', status_code=401)
