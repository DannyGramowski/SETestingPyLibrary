import unittest
from library import ext_api_interface
from unittest.mock import Mock
import requests
import json
from urllib.parse import urlparse, parse_qs
import os

class TestExtApiInterface(unittest.TestCase):
    def override_request(self, url: str):
        #will not work if q and author are specified
        print(os.getcwd())
        with open('SETestingPyLibrary/tests_data/api_data.json') as file:
            books = json.loads(file.read())['docs']
        queries = parse_qs(urlparse(url).query)
        result = []
        if 'q' in queries:
            for book in books:
                # for title in book['title']:
                if queries['q'][0].upper() in book['title'].upper() or any([queries['q'][0].upper() in author.upper() for author in book['author_name']]):
                    result.append(book)
        elif 'author' in queries:
            result = [book for book in books if any([queries['author'][0].upper() in author.upper() for author in book['author_name']])]

        return result
    
    def setUp(self):
        self.api = ext_api_interface.Books_API()
        self.book = "learning python"
        self.api.make_request = self.override_request

    def test_make_request_q_result(self):
        results = self.api.make_request(self.api.API_URL + '?q=the')
        self.assertEqual(len(results), 88)

    def test_make_request_author_result(self):
        results = self.api.make_request(self.api.API_URL + '?author=da')
        print(results)
        self.assertEqual(len(results), 7)

    # def test_make_request_connection_error(self):
    #     ext_api_interface.requests.get = Mock(side_effect=requests.ConnectionError)
    #     url = "some url"
    #     self.assertEqual(self.api.make_request(url), None)

    # def test_make_request_False(self):
    #     requests.get = Mock(return_value=Mock(status_code=100))
    #     self.assertEqual(self.api.make_request(""), None)

    # def test_get_ebooks(self):
    #     self.api.make_request = Mock(return_value=self.json_data)
    #     self.assertEqual(self.api.get_ebooks(self.book), self.books_data)
