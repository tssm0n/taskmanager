from models import *
from config import app
from sqlalchemy.sql.expression import desc

def load_all_tasks():
    return Task.query.order_by(desc(Task.priority)).all()
    
def item_order(items):
    orders = {}
    for item in items:
        key = "item%s" % (item.id)
        orders[key] = item.priority
    return orders    
    
def reorganize(new_list):
    # TODO: This should take in the current list ID so that only the tasks in the current list are sorted
    organizer = TaskReorganizer(new_list)
    organizer.process()
    result = {}
    for task in organizer.dirty:
        db.session.merge(task)
        key = "item%s" % (task.id)
        result[key] = task.priority_index()
    db.session.commit()    
    return result 

def find_tag(user_id, task_list, tag):
    # TODO: Filter based on the user's ID or list...
    tag_obj = Tag.query.filter_by(name=tag).first()
    app.logger.debug("tag: %s - list: %s"%(tag_obj, task_list))
    if tag_obj is not None:
	return tag_obj
    tag_obj = Tag()
    tag_obj.name = tag
    list_obj = List.query.get(task_list)
    list_obj.tags.append(tag_obj)
    db.session.add(tag_obj)
    return tag_obj

def find_tasks(tag_id, list_id, include_completed=True):
    query = Task.query
    if tag_id is not None:
        tag = Tag.query.get(int(tag_id))
        if tag is None:
            return []
        query = query.filter(Task.tags.contains(tag))
    if list_id is not None:
        query = query.filter(Task.list==int(list_id))
    if not include_completed:
        query = query.filter(Task.complete==False)
    return query.order_by(desc(Task.priority)).all()
    
class TaskReorganizer:
    def __init__(self, new_list, original = None):
        self.current_tasks = original
        if original is None:
            self.current_tasks = load_all_tasks()
        self.new_list = new_list
        self.dirty = []
        
    def process(self):
        result = []
        for next_id in self.new_list:
            task = self.find_task(next_id)
            result.append(task)
        return self.update_priorities(result)
    
    def find_task(self, task_id):
        clean_id = int(task_id[4:])
        for task in self.current_tasks:
            if task.id == clean_id:
                return task
        raise TaskManagerException("Unable to find existing task for id: %s" % (clean_id))
    
    def update_priorities(self, tasks):
        if len(tasks) <= 1:
            return tasks
        prev = None
        for index in range(len(tasks)):
            task = tasks[index]
            if prev is None:
                if task.priority < tasks[index+1].priority:
                    task.priority = tasks[index+1].priority + 250
                    self.dirty.append(task)
            else:
                if task.priority > prev.priority:
                    if index == len(tasks) - 1:
                        task.priority = prev.priority - 250
                        self.dirty.append(task)
                        if task.priority < 0:
				task.priority = 1
                    else:
                        if tasks[index+1].priority < prev.priority:
                            task.priority = (prev.priority + tasks[index+1].priority)/2
                            self.dirty.append(task)
                        else: 
                            prev.priority = (task.priority + tasks[index-2].priority)/2
                            self.dirty.append(prev)
            prev = task
        return tasks

class TaskManagerException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)            
