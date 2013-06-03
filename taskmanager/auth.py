from models import *
from flask import session
from flask.ext.restless import ProcessingException
from config import app, db
import utils
from models import *

def check_auth():
    app.logger.debug("check_auth")
    return session.has_key('user')

def api_auth(search_params=None, **kw):
    if not check_auth():
        raise ProcessingException(message='Not Authorized', status_code=401)
    user = db.session.merge(session['user'])
    if search_params is not None:
        return _process_search(search_params, user)
    if not 'instance_id' in kw:
	return
    task = Task.query.get(int(kw['instance_id']))
    if not utils.list_id_valid_for_user(user, task.list):
	raise ProcessingException(message='Not Authorized', status_code=401)

def _process_search(search_params, user):
    filt = dict(name='list', op='in', val=[list.id for list in user.lists])
    #filt = dict(name='id', op='in', val=[1,2,3,4,5,6,7])
    if 'filters' not in search_params:
	search_params['filters'] = []
    search_params['filters'].append(filt)


class authed:
    def __init__(self, f):
	self.__name__ = f.__name__
        self.f = f
    
    def __call__(self):
        return self.f()
