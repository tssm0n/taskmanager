from taskmanager import models

models.db.create_all()

for priority in range(1,11):
    o1 = models.Options()
    o1.group = 'priority'
    o1.label = "%s" % (priority)
    o1.value = "%s" % (priority)
    models.db.session.add(o1)
    
t1 = models.Task()
t1.title = 'Test Task 1'
t1.priority = 100000
t1.details = 'Test Task 1 details'
t1.complete = False

t2 = models.Task()
t2.title = 'Another test task'
t2.priority = 100001
t2.details = 'Test Task 2 details'
t2.complete = False
   
models.db.session.add(t1)
models.db.session.add(t2)    
    
models.db.session.commit()


