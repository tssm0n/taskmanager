from taskmanager import models

models.db.create_all()

for priority in range(1,11):
    o1 = models.Options()
    o1.group = 'priority'
    o1.label = "%s" % (priority)
    o1.value = "%s" % (priority)
    models.db.session.add(o1)

list = models.List()
list.name = "My List"

user = models.User()
user.name = "User 1"
user.lists = [list]

models.db.session.add(list)
models.db.session.add(user)

models.db.session.commit()

user.default_list = list.id
    
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

t3 = models.Task()
t3.title = 'Yet Another test task'
t3.priority = 100001
t3.details = 'Test Task 3 details'
t3.complete = True

t1.list = list.id
t2.list = list.id
t3.list = list.id
   
models.db.session.add(t1)
models.db.session.add(t2)
models.db.session.add(t3)

tag1 = models.Tag()
tag1.name="Tag1"
tag1.list = list.id

tag2 = models.Tag()
tag2.name="Other Tag"
tag2.list = list.id

list.tags = [tag1,tag2]

models.db.session.add(tag1)
models.db.session.add(tag2)

models.db.session.commit()


