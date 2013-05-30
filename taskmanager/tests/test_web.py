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

    def setUp(self):
        self.list = self.setup_list()
        self.user = self.setup_user()
        self.tag = self.setup_tag()
	models.db.session.commit()
	self.user = models.db.session.merge(self.user)

        with self.app as c:
            with c.session_transaction() as sess:
                sess['user'] = self.user
                sess['openid'] = "1"
	
    def tearDown(self):
	models.db.session.commit()
	models.Task.query.delete()
	models.List.query.delete()
	models.Tag.query.delete()
	models.User.query.delete()
	self.user = None
	self.list = None
	models.db.session.commit()
	models.db.session.flush()

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
	list = self.list
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

    def setup_multi_user(self):
	self.user = models.db.session.merge(self.user)
	self.list = models.db.session.merge(self.list)
	self.user.lists = [self.list]

        list2 = models.List()
        list2.name = "List2"
        models.db.session.add(list2)

	user2 = models.User()
        user2.name = "User2"
	user2.lists = [list2]
        models.db.session.add(user2)
	models.db.session.commit()
	models.db.session.flush()

	return user2

    def test_root(self):
	user = models.User.query.first()
	result = self.app.get("/", follow_redirects=False)
	assert "302" in result.status

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
	task = self.setup_tasks(1)
	list = self.list
	models.db.session.commit()
	list = models.List.query.first()
	task.tags = []
	task.list = list.id
	models.db.session.commit()
	task = models.Task.query.first()
	before = len(models.Tag.query.all())
	result = self.app.post("addTag", data=dict(
		taskId=str(task.id),tag="New"))
	after = len(models.Tag.query.all())
	self.assertIn("200", result.status)   
	self.assertEquals(1, after-before)
	task = models.Task.query.first()
	self.assertEquals(1, len(task.tags))

    def execute_existing_tag(self, change_case):
	self.user = models.db.session.merge(self.user)
	self.list = models.db.session.merge(self.list)
	self.user.lists = [self.list]
        task = self.setup_tasks(1)
        list = self.list
        models.db.session.commit()
	task = models.Task.query.first()
        list = models.List.query.first()
        task.list = list.id
        models.db.session.commit()
	existing = models.Tag.query.first()
        task = models.Task.query.first()
        before = len(models.Tag.query.all())
	user = models.User.query.first()
	name = existing.name
	if change_case:
	    name = name.upper()

        with self.app as c:
            with c.session_transaction() as sess:
                sess['user'] = user
            result = self.app.post("addTag", data=dict(
                taskId=str(task.id),tag=name))
        after = len(models.Tag.query.all())
        self.assertIn("200", result.status)
        self.assertEquals(0, after-before)
        task = models.Task.query.first()
        self.assertEquals(1, len(task.tags))

    def test_add_existing_tag(self):
	self.execute_existing_tag(False)

    def test_add_existing_tag_with_case(self):
        self.execute_existing_tag(True)

    def test_tag_list(self):
	models.db.session.commit()
	list = models.List.query.first()
	tag = models.Tag.query.first()
	tag.list = list.id
	self.user = models.db.session.merge(self.user)
	self.user.lists = [list]
	models.db.session.commit()
        result = self.app.get("tags/" + str(list.id))
        self.assertIn("200", result.status)
	expected = json.dumps(["Tag1"])
	self.assertEquals(expected, result.data)
	

    def test_add_list(self):
	user = self.user
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

    def test_multi_user(self):
	self.setup_multi_user()
	models.db.session.commit()

	users = len(models.User.query.all())
	self.assertEquals(2, users)

    def test_new_task_invalid_list(self):
	user2 = self.setup_multi_user()
	self.user.lists = [self.list]
        self.setup_tasks(1)
        result = self.app.post("newTask", data=dict(
                title="New", listId=user2.lists[0].id))
        self.assertIn("401", result.status)

    def test_add_tag_invalid_tag(self):
	user2 = self.setup_multi_user()
        self.user.lists = [self.list]
        task = self.setup_tasks(1)
        list = user2.lists[0]
        models.db.session.commit()
        task.tags = []
        task.list = list.id
        models.db.session.commit()
        task = models.db.session.merge(task)
        result = self.app.post("addTag", data=dict(
                taskId=str(task.id),tag="New"))
        self.assertIn("401", result.status)

    def test_get_tags_invalid_list(self):
        user2 = self.setup_multi_user()
        self.user.lists = [self.list]
        result = self.app.get("/tags/250")
        self.assertIn("401", result.status)


if __name__ == '__main__':
    unittest.main()



