import unittest

from src.dgarbsutils import utils


class TestUtils(unittest.TestCase):
    """Test suite for the utils library"""

    def test_get_content_type(self):
        """tests the get_content_type function"""
        self.assertEqual(
            utils.get_content_type("xlsx"),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(utils.get_content_type("png"), "image/png")
        self.assertEqual(utils.get_content_type("jpg"), "image/jpeg")
        self.assertEqual(utils.get_content_type("jpeg"), "image/jpeg")
        self.assertEqual(utils.get_content_type("pdf"), "application/pdf")
        self.assertEqual(utils.get_content_type("txt"), None)

    def test_make_json_from_csv(self):
        """tests the make_json_from_csv function"""
        self.assertEqual(
            utils.make_json_from_csv("tests/test_data/test_data.csv", ","),
            [
                {
                    "id": "1",
                    "name": "John",
                    "age": "25",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA",
                    "email": "john@gmail.com",
                }
            ],
        )
        self.assertNotEqual(
            utils.make_json_from_csv("tests/test_data/test_data.csv", ","),
            [
                {
                    "id": "1",
                    "age": "25",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA",
                    "email": "john@gmail.com",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
