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
    return render_template('list.html', listItems = items, optionValues = load_option_values(), optionNames = OptionValues.option_names())

@app.route('/sort', methods=['POST'])
def perform_sort():
    list_data = json.loads(request.form['list'])
    return "Size: %s" % (len(list_data))

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