from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import flask.ext.restless
from models import *
from auth import *
import utils
from sqlalchemy import distinct
import json

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'asd123jf23\/\/\/1231aa'

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Task, methods=['GET','PUT','PATCH'], 
	preprocessors=dict(GET_SINGLE=[api_auth],
	GET_MANY=[api_auth]))
manager.create_api(Tag, methods=['GET'],
        preprocessors=dict(GET_SINGLE=[api_auth],
        GET_MANY=[api_auth]))
#TODO: Implement pre and post processors on the rest API to filter available tasks 

@app.route('/')
def root():
    return "Hello World!"

@app.route('/list')
@app.route('/listtag/<tagid>')
@app.route('/list/<listid>')
def view_list(tagid=None, listid=None):
    #TODO: This is a login workaround
    check_auth()
    if not session.has_key('selected_list'):
        session['selected_list'] = session['user'].default_list

    user = User.query.get(session['user'].id)
    selected_list = session['selected_list']
    current_list = List.query.get(selected_list)
        # TODO: When loading tasks, filter out the completed ones
    lists = user.lists
    if tagid is None and listid is None:
	items = current_list.tasks
    else:
        items = utils.find_tasks(tagid, listid)

    return render_template('list.html', 
                           listItems = items,
                           itemOrder = json.dumps(utils.item_order(items)),
			               lists = lists,
                           selectedList = session['selected_list'],
			   tags = current_list.tags)

@app.route('/sort', methods=['POST'])
def perform_sort():
    list_data = json.loads(request.form['list'])
    result = utils.reorganize(list_data)
    return json.dumps(result)

@app.route('/newTask', methods=['POST'])
def new_task():
    title = request.form['title']
    max_priority = Task.query.order_by(Task.priority).all()[-1].priority
    task = Task()
    task.priority = max_priority + 1000
    task.title = title
    task.complete = False
    task.list = int(request.form['listId'])
    # TODO: Before saving, check that the user has permission to save to that list
    db.session.add(task)
    db.session.commit()
    return render_template('itemlist.html', item=task)    

@app.route('/completeTask', methods=['POST'])
def complete_task():
    task_id = request.form['taskId']
    task = Task.query.get(int(task_id))
    task.complete = not task.complete
    db.session.commit()
    return task_id

@app.route('/changePriority', methods=['POST'])
def change_priority():
    task_id = request.form['taskId']
    priority_index = request.form['priorityIndex']
    task = Task.query.get(int(task_id))   
    task.priority = ((10-int(priority_index))*100000 + 50000)
    db.session.commit()
    return "%s" % (task.priority) 
    
@app.route('/addTag', methods=['POST'])
def add_tag():
    check_auth()
    task_id = request.form['taskId']
    task = Task.query.get(int(task_id))
    task_list = task.list
    tag_text = request.form['tag']
    tags = tag_text.split(",")
    user = session['user']
    for tag in tags:
	print "%s %s"%(tag, task_list)
    	tag_obj = utils.find_tag(user.id, task_list, tag)
        task.tags.append(tag_obj)
    db.session.commit()
    return tag_text	        

@app.route('/addList', methods=['POST'])
def add_list():
    # TODO: Check list already exists
    check_auth()
    list_name = request.form['newListName']
    new_list = List()
    new_list.name = list_name
    db.session.add(new_list)
    user = User.query.get(session['user'].id)
    user.lists.append(new_list)
    db.session.commit()
    return redirect(url_for('view_list', listid = new_list.id))

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

