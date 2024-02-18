# flake8: noqa: D101, D102
import unittest


class TestPath(unittest.TestCase):
    def test_nothing(self):
        self.assertTrue(True)  # pylint: disable=W1503


if __name__ == "__main__":
    unittest.main()
