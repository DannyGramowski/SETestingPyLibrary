import unittest
from library import patron

class TestPatron(unittest.TestCase):

    def setUp(self):
        self.pat = patron.Patron('fname', 'lname', '20', '1234')

    def test_valid_name(self):
        self.assertTrue(isinstance(self.pat, patron.Patron))

    def test_invalid_name(self):
        self.assertRaises(patron.InvalidNameException, patron.Patron, '1fname', '1lname', '20', '1234')
    
    def test_no_borrowed_books(self):
        actual = self.pat.get_borrowed_books()
        expected = []
        self.assertSequenceEqual(actual, expected)
        
    def test_one_borrowed_book(self):
        self.pat.add_borrowed_book("testbook")
        actual = self.pat.get_borrowed_books()
        expected = ["testbook"]
        self.assertSequenceEqual(actual, expected)
        
    def test_two_borrowed_books(self):
        self.pat.add_borrowed_book("testbook1")
        self.pat.add_borrowed_book("testbook2")
        actual = self.pat.get_borrowed_books()
        expected = ["testbook1", "testbook2"]
        self.assertSequenceEqual(actual, expected)
        
    def test_returned_book(self):
        self.pat.add_borrowed_book("testbook")
        self.pat.return_borrowed_book("testbook")
        actual = self.pat.get_borrowed_books()
        expected = []
        self.assertSequenceEqual(actual, expected)
        
    def test_duplicate_borrowed_book(self):
        self.pat.add_borrowed_book("testbook")
        self.pat.add_borrowed_book("testbook")
        actual = self.pat.get_borrowed_books()
        expected = ["testbook"]
        self.assertSequenceEqual(actual, expected)
        
    def test_two_borrowed_books_one_returned(self):
        self.pat.add_borrowed_book("testbook1")
        self.pat.add_borrowed_book("testbook2")
        self.pat.return_borrowed_book("testbook1")
        actual = self.pat.get_borrowed_books()
        expected = ["testbook2"]
        self.assertSequenceEqual(actual, expected)
        
    def test_lowercase_books(self):
        self.pat.add_borrowed_book("TESTBOOK")
        actual = self.pat.get_borrowed_books()
        expected = ["testbook"]
        self.assertSequenceEqual(actual, expected)
        
    def test_return_unborrowed_book(self):
        self.pat.add_borrowed_book("testbook1")
        self.pat.add_borrowed_book("testbook2")
        self.pat.return_borrowed_book("testbook3")
        actual = self.pat.get_borrowed_books()
        expected = ["testbook1", "testbook2"]
        self.assertSequenceEqual(actual, expected)
    
    def test_get_fname(self):
        actual = self.pat.get_fname()
        expected = "fname"
        self.assertSequenceEqual(actual, expected)
    
    def test_get_lname(self):
        actual = self.pat.get_lname()
        expected = "lname"
        self.assertSequenceEqual(actual, expected)
    
    def test_get_age(self):
        actual = self.pat.get_age()
        expected = "20"
        self.assertSequenceEqual(actual, expected)
    
    def test_get_memberID(self):
        actual = self.pat.get_memberID()
        expected = "1234"
        self.assertSequenceEqual(actual, expected)
    
    def test_ne_same(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fname', 'lname', '20', '1234')
        self.assertFalse(pat1 != pat2)
        
    def test_ne_fname(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fnamee', 'lname', '20', '1234')
        self.assertTrue(pat1 != pat2)
    
    def test_ne_lname(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fname', 'lnamee', '20', '1234')
        self.assertTrue(pat1 != pat2)
        
    def test_ne_age(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fnamee', 'lname', '200', '1234')
        self.assertTrue(pat1 != pat2)
        
    def test_ne_memberID(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fnamee', 'lname', '20', '12344')
        self.assertTrue(pat1 != pat2)
        
    def test_eq_same(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fname', 'lname', '20', '1234')
        self.assertTrue(pat1 == pat2)
        
    def test_eq_fname(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fnamee', 'lname', '20', '1234')
        self.assertFalse(pat1 == pat2)
    
    def test_eq_lname(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fname', 'lnamee', '20', '1234')
        self.assertFalse(pat1 == pat2)
        
    def test_eq_age(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fnamee', 'lname', '200', '1234')
        self.assertFalse(pat1 == pat2)
        
    def test_eq_memberID(self):
        pat1 = patron.Patron('fname', 'lname', '20', '1234')
        pat2 = patron.Patron('fnamee', 'lname', '20', '12344')
        self.assertFalse(pat1 == pat2)