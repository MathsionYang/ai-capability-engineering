import unittest

from src.total import total


class TotalTest(unittest.TestCase):
    def test_total_adds_two_numbers(self):
        self.assertEqual(total(2, 3), 5)


if __name__ == "__main__":
    unittest.main()
