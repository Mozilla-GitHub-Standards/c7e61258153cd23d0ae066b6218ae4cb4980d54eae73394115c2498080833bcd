import unittest
from loads.case import TestCase, TestResult


class _MyTestCase(TestCase):
    def test_one(self):
        pass

    def test_two(self):
        raise AttributeError()

    def test_three(self):
        self.assertTrue(False)


class TestTestCase(unittest.TestCase):

    def test_fake(self):
        results = TestResult()
        loads_status = 1, 1, 1, 1

        case = _MyTestCase('test_one', test_result=results)
        case(loads_status=loads_status)
        self.assertEqual(results.testsRun, 1)
        self.assertEqual(results.wasSuccessful(), True)
        self.assertEqual(len(results.errors), 0)

        case = _MyTestCase('test_two', test_result=results)
        case(loads_status=loads_status)
        self.assertEqual(results.testsRun, 2)
        self.assertEqual(results.wasSuccessful(), False)
        self.assertEqual(len(results.errors), 1)

        case = _MyTestCase('test_three', test_result=results)
        case(loads_status=loads_status)
        self.assertEqual(results.testsRun, 3)
        self.assertEqual(results.wasSuccessful(), False)
        self.assertEqual(len(results.errors), 1)

        self.assertRaises(ValueError, case.app.get, 'boh')