import unittest
from src.dgarbsutils import utils


class TestUtils(unittest.TestCase):
    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_get_content_type(self):
        self.assertEqual(
            utils.get_content_type("xlsx"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertEqual(utils.get_content_type("png"), "image/png")
        self.assertEqual(utils.get_content_type("jpg"), "image/jpeg")
        self.assertEqual(utils.get_content_type("jpeg"), "image/jpeg")
        self.assertEqual(utils.get_content_type("pdf"), "application/pdf")
        self.assertEqual(utils.get_content_type("txt"), None)


if __name__ == "__main__":
    unittest.main()
