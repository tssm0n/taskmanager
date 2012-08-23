from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from models import *
import utils
from sqlalchemy import distinct
import json

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def root():
    return "Hello World!"

@app.route('/list')
def view_list():
    items = utils.load_all_tasks()
    return render_template('list.html', 
                           listItems = items,
                           itemOrder = json.dumps(utils.item_order(items)),
                           optionValues = load_option_values(), 
                           optionNames = OptionValues.option_names())

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
    db.session.add(task)
    db.session.commit()
    return "%s" % (task.id)    

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
    task.priority = ((11-int(priority_index))*100000 + 50000)
    db.session.commit()
    return "%s" % (task.priority) 

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
