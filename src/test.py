import unittest
import utils

class TestMain(unittest.TestCase):
    def test_dot_times0(self):
        lst1 = [1,2,3]
        lst2 = [2,3,4]
        expected = 20
        actual = utils.dot_times(lst1, lst2)
        self.assertEquals(actual, expected)

    def test_vec_abs0(self):
        lst = [3,4]
        expected = 5.0
        actual = utils.vec_abs(lst)
        self.assertEquals(actual, expected)

    def test_cos_sim0(self):
        lst1 = [1,2,3]
        expected = 1.0
        actual = utils.cos_sim(lst1, lst1)
        self.assertEquals(actual, expected)

    def test_cos_sim1(self):
        lst1 = [4,0,0]
        lst2 = [0,4,0]
        expected = 0.0
        actual = utils.cos_sim(lst1, lst2)
        self.assertEquals(actual, expected)

    def test_cos_sim2(self):
        expected = 0.0
        actual = utils.cos_sim([], [])
        self.assertEquals(actual, expected)


    def test_vec_sum0(self):
        vec_lst = [[1,0,3], [0,4,0]]
        expected = [1, 4, 3]
        actual = utils.vec_sum(vec_lst)
        self.assertEquals(actual, expected)

    def test_vec_mean0(self):
        vec_lst = [[1,0,3], [0,4,0]]
        expected = [0.5, 2.0, 1.5]
        actual = utils.vec_mean(vec_lst)
        self.assertEquals(actual, expected)

    def test_vec_mean1(self):
        vec_lst = []
        expected = []
        actual = utils.vec_mean(vec_lst)
        self.assertEquals(actual, expected)

    def test_normalize_vec0(self):
        lst = [1,0,0]
        expected = [1, 0, 0]
        actual = utils.normalize_vec(lst)
        self.assertEquals(actual, expected)

    def test_normalize_vec1(self):
        lst = [3,4]
        expected = [0.6, 0.8]
        actual = utils.normalize_vec(lst)
        self.assertEquals(actual, expected)

if __name__ == '__main__':
    unittest.main()
