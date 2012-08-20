from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import json

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def root():
    return "Hello World!"

@app.route('/list')
def view_list():
    items = [Item(1),
             Item(2)]
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
        self.values = {'test': ['one', 'two']}
        
    @staticmethod
    def option_names():
        return ['test']
    
    def __getitem__(self, name):
        return self.values[name]