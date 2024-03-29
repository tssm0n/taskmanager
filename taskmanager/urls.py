from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, Response
import flask.ext.restless
from sqlalchemy import distinct
from flask.ext.openid import OpenID
import json
import logging
from models import *
from config import *
from auth import *
import utils

oid = OpenID(app, oid_file)

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Task, methods=['GET','PUT','PATCH','DELETE'],
        preprocessors=dict(GET_SINGLE=[api_auth],
        GET_MANY=[api_auth], 
	DELETE=[api_auth], 
	PUT_SINGLE=[api_auth],
	PUT_MANY=[api_auth], 
	PATCH_SINGLE=[api_auth],
	PATCH_MANY=[api_auth]))
#manager.create_api(Tag, methods=['GET'],
#        preprocessors=dict(GET_SINGLE=[api_auth],
#        GET_MANY=[api_auth]))
#TODO: Implement REST API for Tags and Lists

unmanaged_urls = ["login", "create_profile", "create_or_login", "logout"]

@app.before_request
def lookup_current_user():
    if not request.endpoint in unmanaged_urls:
        if not 'openid' in session:
   	    return redirect(url_for('login'))
        if not 'user' in session:
            email = session['email']
            session['user'] = User.query.filter_by(name=email).first()

@app.route('/')
def root():
    app.logger.debug("Hello World!")
    return redirect(url_for('view_list'))

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if 'user' in session and not 'openid' in session:
	app.logger.debug("Clearing stale user session")
	session.pop('user')
    if 'user' in session:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
		# TODO: Allow providers other than google
            return oid.try_login(flask.ext.openid.COMMON_PROVIDERS['google'], ask_for=['email','fullname','nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())

@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    app.logger.debug("Create_profile")
    if 'openid' not in session:
        return redirect(url_for('view_list'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
	    default_list = List(name="Inbox")
	    db.session.add(default_list)
	    db.session.commit()
	    user = User(name=email[:50], openid=session['openid'], created=datetime.now(), \
                default_list=default_list.id, lists=[default_list])
            db.session.add(user)
            db.session.commit()
	    session['user'] = user
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())

@oid.after_login
def create_or_login(resp):
    app.logger.debug("create_or_login")
    app.logger.debug(resp.email)
    session['openid'] = resp.identity_url
    session['email']= resp.email
    user = User.query.filter_by(name=resp.email).first()
    if user is not None:
        flash(u'Successfully signed in')
        session['user'] = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

@app.route('/logout')
def logout():
    session.pop('openid', None)
    session.pop('user', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())

@app.route('/list')
@app.route('/listtag/<tagid>')
@app.route('/list/<listid>')
def view_list(tagid=None, listid=None):
    user = db.session.merge(session['user'])
    session['user'] = user

    if not session.has_key('selected_list'):
        session['selected_list'] = session['user'].default_list

    tag = None

    if tagid is not None:
        tag = Tag.query.get(int(tagid))
        session['selected_list'] = tag.list
    if listid is not None:
        session['selected_list'] = listid
	user.default_list = listid
	db.session.commit()

    selected_list = session['selected_list']
    app.logger.debug("Tag: %s, List: %s, Saved List: %s, Passed List: %s"%(tagid, listid, session['selected_list'], selected_list))
    current_list = List.query.get(selected_list)
    lists = user.lists
    lists = [list for list in lists if not list.inactive]

    items = utils.find_tasks(tagid, selected_list, False)

    app.logger.debug("Tag: %s, List: %s, Saved List: %s, Passed List: %s"%(tagid, listid, session['selected_list'], selected_list))

    return render_template('list.html', 
                           listItems = items,
                           itemOrder = json.dumps(utils.item_order(items)),
			               lists = lists,
                           selectedList = int(session['selected_list']),
			   tags = current_list.tags,
			   tag = tag,
                           urlRoot = url_for("root"))

@app.route('/sort', methods=['POST'])
def perform_sort():
    list_data = json.loads(request.form['list'])
    result = utils.reorganize(list_data)
    return json.dumps(result)

@app.route('/newTask', methods=['POST'])
def new_task():
    title = request.form['title']
    list_id = int(request.form['listId'])
    user = db.session.merge(session['user'])
    if not utils.list_id_valid_for_user(user, list_id):
	return Response("Access Denied", 401)	
    all_tasks = Task.query.filter_by(list=list_id).order_by(Task.priority).all()
    max_priority = 5000
    if len(all_tasks) > 0:
        max_priority = all_tasks[-1].priority
    task = Task()
    task.priority = max_priority + 1000
    task.title = title
    task.complete = False
    task.list = list_id
    db.session.add(task)
    db.session.commit()
    return render_template('itemlist.html', item=task)    

@app.route('/completeTask', methods=['POST'])
def complete_task():
# TODO: Check permissions
    task_id = request.form['taskId']
    task = Task.query.get(int(task_id))
    task.complete = not task.complete
    db.session.commit()
    return task_id

@app.route('/changePriority', methods=['POST'])
def change_priority():
# TODO: Check permissions
    task_id = request.form['taskId']
    priority_index = request.form['priorityIndex']
    task = Task.query.get(int(task_id))   
    task.priority = ((10-int(priority_index))*100000 + 50000)
    db.session.commit()
    return "%s" % (task.priority) 
    
@app.route('/addTag', methods=['POST'])
def add_tag():
    task_id = request.form['taskId']
    task = Task.query.get(int(task_id))
    user = session['user']
    user = db.session.merge(user)

    if not utils.list_id_valid_for_user(user, task.list):
	return Response("Access Denied", 401)	

    task_list = task.list
    tag_text = request.form['tag']
    tags = tag_text.split(",")
    user = session['user']
    user = db.session.merge(user)
    for tag in tags:
	app.logger.debug("Adding tag: %s %s"%(tag, task_list))
    	tag_obj = utils.find_tag(user.id, task_list, tag)
        task.tags.append(tag_obj)
    db.session.commit()
    selected_list = List.query.get(task_list)    
    return render_template('taglist.html', tags=selected_list.tags)

@app.route('/addList', methods=['POST'])
def add_list():
    # TODO: Check list already exists
    list_name = request.form['newListName']
    new_list = List()
    new_list.name = list_name
    db.session.add(new_list)
    user = User.query.get(session['user'].id)
    user.lists.append(new_list)
    db.session.commit()
    return redirect(url_for('view_list', listid = new_list.id))

@app.route('/removeList', methods=['POST'])
def remove_list():
    list_id = int(request.form['listId'])
    user = db.session.merge(session['user'])
    if not utils.list_id_valid_for_user(user, list_id):
        return Response("Access Denied", 401)
    list = List.query.get(list_id)
    list.inactive = True
    db.session.commit()
    return "OK"

@app.route('/tags/<listid>', methods=['GET'])
def get_tags(listid):
    user = db.session.merge(session['user'])
    if not utils.list_id_valid_for_user(user, int(listid)):
        return Response("Access Denied", 401)

    tags = Tag.query.filter_by(list=listid).order_by(Tag.name).all()
    tag_names = [t.name for t in tags]
    return json.dumps(tag_names)

@app.route('/removeTag', methods=['POST'])
def remove_tag():
    #TODO: Check permission to the list
    task_id = request.form['taskId']
    tag_id = int(request.form['tag'])
    task = Task.query.get(int(task_id))
    tags = [tag.id for tag in task.tags]
    if not tag_id in tags:
	return Response("Access Denied", 401)

    new_tags = [tag for tag in task.tags if tag.id != tag_id]
    task.tags = new_tags
    db.session.commit()
    return Response("OK", 200)

def load_option_values():
    return OptionValues()
    

class Item:
    def __init__(self, id):
        self.id = id
        
class OptionValues:
    def __init__(self):
        self.values = {}
        options = Options.query.all()
        for option in options:
            if not self.values.has_key(option.group):
                self.values[option.group] = []
            self.values[option.group].append(option)
        
    @staticmethod
    def option_names():
        groups = db.session.query(distinct(Options.group))
        return [group[0] for group in groups]
    
    def __getitem__(self, name):
        return self.values[name]

