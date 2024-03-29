import sys
sys.path.append("../..")
from taskmanager.models import *
from taskmanager.utils import *
import unittest

class TaskReorganizerTestCase(unittest.TestCase):
    def test_ordering_up(self):
        self.__run_test([0,1,2,3,8,4,5,6,7,9])

    def test_ordering_down(self):
        self.__run_test([0,1,2,4,5,6,3,7,8,9])

    def test_first(self):
        self.__run_test([1,2,3,5,6,0,7,8,9])
        
    def test_last(self):
        self.__run_test([0,1,2,3,4,5,6,9,7,8])        
        
    def test_to_first(self):
        self.__run_test([3,0,1,2,4,5,6,7,8,9])        

    def test_to_last(self):
        self.__run_test([0,1,2,4,5,6,7,8,9,3]) 
        
    def __run_test(self, new_order):
        tasks = []
        for nextid in range(10):
            t = Task()
            t.id = nextid
            t.priority = 110000 - (nextid * 10000)
            tasks.append(t)
        
        updated = ["item%s" % (q) for q in new_order]
        
        to = TaskReorganizer(updated, tasks)
        result = to.process()
        actual = [task.id for task in result]
        self.assertEquals(actual, new_order, "Correct Order")
        
        priority = 1000000
        for next_task in result:
            self.assertTrue(next_task.priority < priority, "Expected lower priority %s < %s - id: %s" % (next_task.priority, priority, next_task.id))
            priority = next_task.priority

    def test_same_priority(self):
	tasks = [Task(id=1, priority=85000), Task(id=2, priority=85000)]
	to = TaskReorganizer(["item1","item2"], tasks)
	result = to.process()
	assert result[0].priority != result[1].priority

class UtilsUnitTests(unittest.TestCase):
    def test_list_id_valid_for_user(self):
	user = User()
	list1 = List(id=1)
    	list2 = List(id=2)
	user.lists = [list1,list2]
	self.assertTrue(list_id_valid_for_user(user, 1))
	self.assertFalse(list_id_valid_for_user(user, 3))
		


if __name__ == '__main__':
    unittest.main()
