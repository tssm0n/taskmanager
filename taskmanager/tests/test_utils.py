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
    
if __name__ == '__main__':
    unittest.main()
