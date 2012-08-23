from models import *
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
    organizer = TaskReorganizer(new_list)
    organizer.process()
    result = {}
    for task in organizer.dirty:
        db.session.merge(task)
        key = "item%s" % (task.id)
        result[key] = task.priority_index()
    db.session.commit()    
    return result 
    
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
                        # TODO: Check for negative priority
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
