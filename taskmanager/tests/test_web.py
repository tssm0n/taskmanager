import sys
import os
sys.path.append("..")
import config
import unittest
import tempfile

class TaskManagerTestCase(unittest.TestCase):

    def setUp(self):
	self.db_fd, self.db_file = tempfile.mkstemp()
	config.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_file
	config.app.config['TESTING'] = True
	self.app = config.app.test_client()
	global models
	import models
	models.db.create_all()

    def tearDown(self):
	os.close(self.db_fd)
	os.unlink(self.db_file)

    def test_mock_database(self):
	self.assertEquals(0,len(models.Task.query.all()))
	t = models.Task()
	t.title = "Test!"
	t.priority = 1
	t.complete = False
	models.db.session.add(t)
	models.db.session.commit()
	self.assertEquals(1,len(models.Task.query.all())) 

if __name__ == '__main__':
    unittest.main()



