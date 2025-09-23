import unittest
from unittest.mock import Mock
from library import library, patron
from unittest.mock import patch
import json

class TestLibrary(unittest.TestCase):

    def setUp(self):
        self.lib = library.Library()
        with open('tests_data/ebooks.txt', 'r') as f:
            self.ebooks_data = json.loads(f.read())
        with open('tests_data/book_data.txt', 'r') as f:
            self.book_data = json.loads(f.read())

    def test_is_ebook_true(self):
        self.lib.api.get_ebooks = Mock(return_value=self.ebooks_data)
        tst_value = "learning python"
        
        result = self.lib.is_ebook(tst_value)
        
        self.lib.api.get_ebooks.assert_called_once_with(tst_value)
        self.assertTrue(result)
        
    def test_is_ebook_false(self):
        self.lib.api.get_ebooks = Mock(return_value=self.ebooks_data)
        tst_value = "eating python"
        
        result = self.lib.is_ebook(tst_value)
        
        self.lib.api.get_ebooks.assert_called_once_with(tst_value)
        self.assertFalse(result)
        
    def test_is_ebook_uppercase_true(self):
        self.lib.api.get_ebooks = Mock(return_value=self.ebooks_data)
        tst_value = "LEARNING PyThOn"
        
        result = self.lib.is_ebook(tst_value)
        
        self.lib.api.get_ebooks.assert_called_once_with(tst_value)
        self.assertTrue(result)

    def test_get_ebooks_count(self):
        self.lib.api.get_ebooks = Mock(return_value=self.ebooks_data)
        tst_value = "learning python"
        
        actual = self.lib.get_ebooks_count(tst_value)
        expected = 8
        
        self.lib.api.get_ebooks.assert_called_once_with(tst_value)
        self.assertEqual(actual, expected)

    def test_is_book_by_author(self):
        book_data = ["book1", "book2"]
        self.lib.api.books_by_author = Mock(return_value=book_data)
        tst_value_author = "author name"
        tst_value_book = "book2"
        
        result = self.lib.is_book_by_author(tst_value_author, tst_value_book)
        
        self.lib.api.books_by_author.assert_called_once_with(tst_value_author)
        self.assertTrue(result)

    def test_is_book_by_author_false(self):
        book_data = ["book1", "book2"]
        self.lib.api.books_by_author = Mock(return_value=book_data)
        tst_value_author = "author name"
        tst_value_book = "book3"
        
        result = self.lib.is_book_by_author(tst_value_author, tst_value_book)
        
        self.lib.api.books_by_author.assert_called_once_with(tst_value_author)
        self.assertFalse(result)

    def test_is_book_by_author_not_found(self):
        book_data = []
        self.lib.api.books_by_author = Mock(return_value=book_data)
        tst_value_author = "author name"
        tst_value_book = "book2"
        
        result = self.lib.is_book_by_author(tst_value_author, tst_value_book)
        
        self.lib.api.books_by_author.assert_called_once_with(tst_value_author)
        self.assertFalse(result)

    def test_languages_for_book_all(self):
        self.lib.api.get_book_info = Mock(return_value=self.book_data)
        tst_value_book = "Way of Kings"
        
        actual = self.lib.get_languages_for_book(tst_value_book)
        expected = set(["por", "pol", "ger", "eng", "spa", "tst"])
        
        self.lib.api.get_book_info.assert_called_once_with(tst_value_book)
        self.assertSetEqual(actual, expected)
    
    @patch('library.patron.Patron', new=lambda:"")
    def test_register_patron(self):
        tst_value_fname = "fname"
        tst_value_lname = "lname"
        tst_value_age = "age"
        tst_value_memberID = "memberID"
        self.lib.db.insert_patron = Mock(return_value=tst_value_memberID)
        
        actual = self.lib.register_patron(tst_value_fname, tst_value_lname, tst_value_age, tst_value_memberID)
        expected = tst_value_memberID
        
        self.lib.db.insert_patron.assert_called_once()
        self.assertEqual(actual, expected)
        
    @patch('library.patron.Patron')
    def test_is_patron_registered_true(self, mock_Patron):
        tst_value_memberID = "memberID"
        self.lib.db.retrieve_patron = Mock(return_value=True)
        
        mock_Patron.get_memberID.return_value = tst_value_memberID
        result = self.lib.is_patron_registered(mock_Patron)
        
        self.lib.db.retrieve_patron.assert_called_once_with(tst_value_memberID)
        self.assertTrue(result)
        
    @patch('library.patron.Patron')
    def test_is_patron_registered_false(self, mock_Patron):
        tst_value_memberID = "memberID"
        self.lib.db.retrieve_patron = Mock(return_value=False)
        
        mock_Patron.get_memberID.return_value = tst_value_memberID
        result = self.lib.is_patron_registered(mock_Patron)
        
        self.lib.db.retrieve_patron.assert_called_once_with(tst_value_memberID)
        self.assertFalse(result)
    
    @patch('library.patron.Patron')
    def test_borrow_book(self, mock_Patron):
        tst_value_book_name = "Way of Kings"
        self.lib.db.update_patron = Mock()
        
        self.lib.borrow_book(tst_value_book_name, mock_Patron)
        
        mock_Patron.add_borrowed_book.assert_called_once_with("way of kings")
        self.lib.db.update_patron.assert_called_once_with(mock_Patron)
    
    @patch('library.patron.Patron')
    def test_return_borrowed_book(self, mock_Patron):
        tst_value_book_name = "Way of Kings"
        mock_Patron.return_borrowed_book.return_value = tst_value_book_name
        self.lib.db.update_patron = Mock()
        
        self.lib.return_borrowed_book(tst_value_book_name, mock_Patron)
        
        mock_Patron.return_borrowed_book.assert_called_once_with("way of kings")
        self.lib.db.update_patron.assert_called_once_with(mock_Patron)
    
    @patch('library.patron.Patron')
    def test_is_book_borrowed_true(self, mock_Patron):
        tst_value_book_name = "Way of Kings"
        tst_value_borrowed_books = ["way of kings"]
        mock_Patron.get_borrowed_books.return_value = tst_value_borrowed_books
        
        result = self.lib.is_book_borrowed(tst_value_book_name, mock_Patron)
        
        mock_Patron.get_borrowed_books.assert_called_once()
        self.assertTrue(result)
    
    @patch('library.patron.Patron')
    def test_is_book_borrowed_false(self, mock_Patron):
        tst_value_book_name = "Way of Kings"
        tst_value_borrowed_books = []
        mock_Patron.get_borrowed_books.return_value = tst_value_borrowed_books
        
        result = self.lib.is_book_borrowed(tst_value_book_name, mock_Patron)
        
        mock_Patron.get_borrowed_books.assert_called_once()
        self.assertFalse(result)
        
        
    
    
