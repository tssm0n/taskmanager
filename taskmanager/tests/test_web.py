import sys
import os
sys.path.append("..")
import config
import unittest
import tempfile
import json

class TaskManagerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
	cls.db_fd, cls.db_file = tempfile.mkstemp()
	config.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + cls.db_file
	config.app.config['TESTING'] = True
	#config.app.config['SQLALCHEMY_ECHO'] = True
	cls.app = config.app.test_client()
	global models
	import models
	import urls
	models.db.create_all()

    @classmethod
    def tearDownClass(cls):
	os.close(cls.db_fd)
	os.unlink(cls.db_file)

    def tearDown(self):
	models.Task.query.delete()
	models.List.query.delete()
	models.Tag.query.delete()

    def test_datamodel(self):
	self.assertEquals(0,len(models.Task.query.all()))
	self.setup_tasks(1)
	models.db.session.commit()
	self.assertEquals(1,len(models.Task.query.all())) 

    def setup_list(self):
        list = models.List()
        list.name = "List"
	models.db.session.add(list)
	return list

    def setup_tag(self):
	list = self.setup_list()
	tag = models.Tag()
	tag.name = "Tag1"
	tag.list = list.id
	models.db.session.add(tag)
	

    def setup_tasks(self, count):
	for index in range(1, count+1):
            t = models.Task()
            t.title = "Test%s"%(index)
            t.priority = index
            t.complete = False
            models.db.session.add(t)
	return t

    def setup_user(self):
	user = models.User()
	user.name = "User"
	models.db.session.add(user)
	return user

    def test_root(self):
	result = self.app.get("/")
	self.assertEquals("Hello World!", result.data)

    def test_sort(self):
	self.setup_tasks(10)
	models.db.session.commit()
	input = '["item3","item8","item7","item9"]'
	expected = {"item3": 10, "item9": 10}
	result = self.app.post("/sort", data=dict(
		list=input))
	self.assertEquals(json.dumps(expected), result.data)

    def test_new_task(self):
	self.setup_tasks(1)
	self.setup_list()
	models.db.session.commit()
	before = len(models.Task.query.all())
	result = self.app.post("newTask", data=dict(
		title="New", listId="1"))
	assert "200" in result.status
	after = len(models.Task.query.all())
	self.assertEquals(1, after-before)
	t = models.Task.query.order_by(models.Task.priority.desc()).first()
	self.assertEquals("New", t.title)

    def test_complete_task(self):
	self.setup_tasks(1)
	models.db.session.commit()
	task = models.Task.query.first()
	id = str(task.id)
	result = self.app.post("completeTask", data=dict(
		taskId = id))
	assert "200" in result.status
	self.assertEquals(id, result.data)
	task = models.Task.query.first()
	assert task.complete

    def test_add_tag(self):
	self.setup_tag()
	task = self.setup_tasks(1)
	list = self.setup_list()
	models.db.session.commit()
	list = models.List.query.first()
	task.list = list.id
	models.db.session.commit()
	task = models.Task.query.first()
	before = len(models.Tag.query.all())
	result = self.app.post("addTag", data=dict(
		taskId=str(task.id),tag="New"))
	after = len(models.Tag.query.all())
	assert "200" in result.status   
	self.assertEquals(1, after-before)

    def test_add_list(self):
	self.setup_list()
	user = self.setup_user()
	models.db.session.commit()
	user = models.User.query.first()
	before = len(models.List.query.all())

	with self.app as c:
	    with c.session_transaction() as sess:
		sess['user'] = user
	    result = c.post("addList", data=dict(
		newListName="New List"))

	after = len(models.List.query.all())
	assert "302" in result.status
	self.assertEquals(1, after-before)

if __name__ == '__main__':
    unittest.main()



