import DB
import unittest

class TestRegistrationAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.db = DB.DB()
        self.informations = {
            "host": "host",
            "port": 1,
            "query_parameters": {
                "ep": "name",
                "et": "type"
            },
            "links": [
                {
                    "path": "/path",
                    "title": "titel"
                }
            ]
        }

    def test_create_endpoint_1(self):
        self.db.create_endpoint(self.informations)
        result = self.db.execute("""
                        SELECT * FROM endpoints
                        """)
        self.assertNotEqual(len(result), 0)

    def test_create_endpoint_2(self):
        self.db.create_endpoint(self.informations)
        result = self.db.execute("""
                        SELECT * FROM endpoints
                        WHERE ep LIKE '{ep}'
                        """.format(ep=self.informations["query_parameters"]["ep"]))
        self.assertEqual(result[0]["et"], self.informations["query_parameters"]["et"])

if __name__ == '__main__':
    unittest.main()