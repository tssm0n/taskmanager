from models import *


def load_all_tasks():
    return Task.query.order_by(Task.priority).all()
    
def reorganize(new_list):
    TaskReorganizer(new_list).process()
    
    
class TaskReorganizer:
    def __init__(self, new_list, original = None):
        self.current_tasks = original
        if original is None:
            self.current_tasks = load_all_tasks()
        self.new_list = new_list
        
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
            else:
                if task.priority > prev.priority:
                    if index == len(tasks) - 1:
                        task.priority = prev.priority - 250
                        # TODO: Check for negative priority
                    else:
                        if tasks[index+1].priority < prev.priority:
                            task.priority = (prev.priority + tasks[index+1].priority)/2
                        else: 
                            prev.priority = (task.priority + tasks[index-2].priority)/2
            prev = task
        return tasks

class TaskManagerException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)            