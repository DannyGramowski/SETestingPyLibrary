import unittest
from library import ext_api_interface
from unittest.mock import Mock
import requests
import json
from urllib.parse import urlparse, parse_qs
import os

class TestExtApiInterface(unittest.TestCase):
    def _get_books(self, url: str):
        with open('tests_data/api_data.json') as file:
            file_data = file.read()
            books = json.loads(file_data)['docs']
        queries = parse_qs(urlparse(url).query)
        queried_books = []
        if 'q' in queries:
            for book in books:
                # for title in book['title']:
                if queries['q'][0].upper() in book['title'].upper() or any([queries['q'][0].upper() in author.upper() for author in book['author_name']]):
                    queried_books.append(book)
        elif 'author' in queries:
            queried_books = [book for book in books if any([queries['author'][0].upper() in author.upper() for author in book['author_name']])]
        
        return queried_books

    def make_request_mock(self, url: str):
        #will not work if q and author are specified
        result = {
            'numFound': 10802937,
            'start': 0,
            'numFoundExact': True,
            'num_found': 10802937,
            'documentation_url': 'https://openlibrary.org/dev/docs/api/search',
            'q': 'the',
            'offset': None,
            'docs': self._get_books(url)
        }
        return result
    
    def setUp(self):
        self.api = ext_api_interface.Books_API()
        self.book = "learning python"

    def test_make_request_404(self):
        res = requests.Response()
        res.status_code = 404
        requests.get = Mock(return_value=res)

        self.assertIsNone(self.api.make_request('abc'), None)

    def test_make_request_error(self):
        requests.get = Mock(side_effect=requests.ConnectionError)
        self.assertIsNone(self.api.make_request('abc'))

    def test_make_request_valid(self):
        res = requests.Response()
        res.json
        res.json = Mock(return_value={'doc': [{'title': 'book1'}]})
        res.status_code = 200
        requests.get = Mock(return_value=res)
        self.assertEqual(self.api.make_request('abc'), {'doc': [{'title': 'book1'}]})
        # requests.get = Mock(return_value={'doc': [{'title': 'book1'}]})

    def test_mock_make_request_q(self):
        self.api.make_request = Mock(side_effect=self.make_request_mock)
        results = self.api.make_request(self.api.API_URL + '?q=the')
        self.assertEqual(len(results['docs']), 88)

    def test_mock_make_request_author(self):
        self.api.make_request = Mock(side_effect=self.make_request_mock)
        results = self.api.make_request(self.api.API_URL + '?author=da')
        self.assertEqual(len(results['docs']), 7)

    def test_book_available_t(self):
        self.api.make_request = Mock(side_effect=self.make_request_mock)
        self.assertTrue(self.api.is_book_available('The Lion, the Witch and the Wardrobe'))
    
    def test_book_available_f(self):
        self.api.make_request = Mock(side_effect=self.make_request_mock)
        self.assertFalse(self.api.is_book_available('A very very specific title'))

    def test_by_author_bad_request(self):
        self.api.make_request = Mock(return_value=None)
        self.assertEqual(self.api.books_by_author('bob'), [])

    def test_by_author_no_author(self):
        self.api.make_request = Mock(return_value={'docs': []})
        self.assertEqual(self.api.books_by_author('Very very specific author'), [])
    
    def test_by_author_no_author(self):
        self.api.make_request = Mock(return_value={'docs': [{'title': 'book1', 'title_suggest': 'sug1'}, {'title': 'book2', 'title_suggest': 'sug2'}]})

        results = self.api.books_by_author('book')
        self.assertEqual(results, ['sug1', 'sug2'])

    def test_book_info_none(self):
        self.api.make_request = Mock(return_value=None)
        self.assertEqual(self.api.get_book_info('book'), [])
   
    def test_book_info_all_fields(self):
        self.api.make_request = Mock(return_value={'docs': [{'title': 'book1', 'publisher': 'pub', 'publish_year': '01/01/2001', 'language': 'en', 'author_name': 'joe smith', 'edition_count': 100}]})
        
        info = self.api.get_book_info('book')
        self.assertEqual(info, [{'title': 'book1', 'publisher': 'pub', 'publish_year': '01/01/2001', 'language': 'en'}])
    
    def test_book_info_no_fields(self):
        self.api.make_request = Mock(return_value={'docs': [{'title': 'book1', 'author_name': 'joe smith', 'edition_count': 100}]})
        
        info = self.api.get_book_info('book')
        self.assertEqual(info, [{'title': 'book1'}])

    def test_ebooks_none(self):
        self.api.make_request = Mock(return_value=None)
        self.assertEqual(self.api.get_ebooks('book'), [])

    def test_ebooks_no_ebooks_count(self):
        self.api.make_request = Mock(return_value={'docs': [{'title': 'book1', 'author_name': 'joe smith', 'ebook_count_i': 0}]})
        self.assertEqual(self.api.get_ebooks('book'),[])
    
    def test_ebooks_ebooks(self):
        self.api.make_request = Mock(return_value={'docs': [{'title': 'book1', 'author_name': 'joe smith', 'ebook_count_i': 2}, {'title': 'book2', 'author_name': 'joe smith', 'ebook_count_i': 5}, {'title': 'book3', 'author_name': 'joe smith', 'ebook_count_i': 0}]})
        self.assertEqual(self.api.get_ebooks('book'),[{'title': 'book1', 'ebook_count': 2}, {'title': 'book2', 'ebook_count': 5}])
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
