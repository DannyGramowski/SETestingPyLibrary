import os
import unittest
from unittest.mock import patch

from library import library_db_interface as ldi


class DummyPatron:
    """
    Minimal test class for library.patron.Patron
    """
    def __init__(self, fname, lname, age, memberID, borrowed_books=None):
        self._fname = fname
        self._lname = lname
        self._age = age
        self._memberID = memberID
        self._borrowed_books = borrowed_books if borrowed_books is not None else []

    # Getters expected by Library_DB.convert_patron_to_db_format
    def get_fname(self):
        return self._fname

    def get_lname(self):
        return self._lname

    def get_age(self):
        return self._age

    def get_memberID(self):
        return self._memberID

    def get_borrowed_books(self):
        return self._borrowed_books


class LibraryDBTests(unittest.TestCase):
    def setUp(self):
        # Create a temp file path for TinyDB and patch the class constant
        self.tmpdir = "tests_data"
        self.db_path = os.path.join(self.tmpdir, "test_db.json")
        # Ensure the file exists
        open(self.db_path, "a").close()

        # Patch the class-level DATABASE_FILE before constructing instances
        self._dbfile_patch = patch.object(ldi.Library_DB, "DATABASE_FILE", self.db_path)
        self._dbfile_patch.start()

        # Patch the Patron used *inside* library_db_interface to be our DummyPatron
        self._patron_patch = patch.object(ldi, "Patron", DummyPatron)
        self._patron_patch.start()

        # Create fresh DB instance per test
        self.db = ldi.Library_DB()

    def tearDown(self):
        # Close and clean up
        try:
            self.db.close_db()
        except Exception:
            pass
        self._patron_patch.stop()
        self._dbfile_patch.stop()
        os.remove(self.db_path)

    # ---------- helpers ----------

    def _make_patron(self, memberID="P001", fname="Test", lname="Person",
                     age=36, borrowed=None):
        return DummyPatron(fname, lname, age, memberID, borrowed)

    # ---------- tests ----------

    def test_insert_patron_success_returns_id_and_increases_count(self):
        p = self._make_patron()
        patron_id = self.db.insert_patron(p)
        self.assertIsInstance(patron_id, int)
        self.assertEqual(self.db.get_patron_count(), 1)

        # Validate the stored record structure via get_all_patrons
        all_rows = self.db.get_all_patrons()
        self.assertEqual(len(all_rows), 1)
        self.assertEqual(all_rows[0]["memberID"], p.get_memberID())
        self.assertEqual(all_rows[0]["fname"], p.get_fname())
        self.assertEqual(all_rows[0]["lname"], p.get_lname())
        self.assertEqual(all_rows[0]["age"], p.get_age())
        self.assertEqual(all_rows[0]["borrowed_books"], p.get_borrowed_books())

    def test_insert_patron_none_returns_none(self):
        result = self.db.insert_patron(None)
        self.assertIsNone(result)
        self.assertEqual(self.db.get_patron_count(), 0)

    def test_insert_patron_duplicate_by_memberID_returns_none_and_no_new_row(self):
        p1 = self._make_patron(memberID="X001", fname="Test")
        p2 = self._make_patron(memberID="X001", fname="DifferentName")  # same ID
        first_id = self.db.insert_patron(p1)
        self.assertIsNotNone(first_id)
        dup_id = self.db.insert_patron(p2)
        self.assertIsNone(dup_id)
        self.assertEqual(self.db.get_patron_count(), 1)

    def test_get_all_patrons_returns_dicts_not_objects(self):
        p = self._make_patron()
        self.db.insert_patron(p)
        rows = self.db.get_all_patrons()
        self.assertIsInstance(rows, list)
        self.assertTrue(rows, "Expected at least one row")
        self.assertIsInstance(rows[0], dict)

    def test_update_patron_updates_existing_record(self):
        # Insert
        p = self._make_patron(memberID="U123", borrowed=["book1"])
        self.db.insert_patron(p)
        # Update: change multiple fields
        p_updated = self._make_patron(memberID="U123", fname="Ada-Updated",
                                      lname="Lovelace-Updated", age=37,
                                      borrowed=["book1", "book2"])
        self.db.update_patron(p_updated)

        # Retrieve and assert changes
        got = self.db.retrieve_patron("U123")
        self.assertIsInstance(got, DummyPatron)
        self.assertEqual(got.get_fname(), "Ada-Updated")
        self.assertEqual(got.get_lname(), "Lovelace-Updated")
        self.assertEqual(got.get_age(), 37)
        self.assertEqual(got.get_memberID(), "U123")

        rows = self.db.get_all_patrons()
        self.assertEqual(rows[0]["borrowed_books"], ["book1", "book2"])

    def test_update_patron_none_is_noop_and_returns_none(self):
        # Insert one row
        self.db.insert_patron(self._make_patron(memberID="N1"))
        before = self.db.get_patron_count()
        result = self.db.update_patron(None)
        after = self.db.get_patron_count()
        self.assertIsNone(result)
        self.assertEqual(before, after)

    def test_retrieve_patron_existing_returns_patron_object(self):
        p = self._make_patron(memberID="R42", fname="Alan", lname="Turing",
                              age=41, borrowed=["The Imitation Game"])
        self.db.insert_patron(p)
        got = self.db.retrieve_patron("R42")
        self.assertIsInstance(got, DummyPatron)
        self.assertEqual(got.get_fname(), "Alan")
        self.assertEqual(got.get_lname(), "Turing")
        self.assertEqual(got.get_age(), 41)
        self.assertEqual(got.get_memberID(), "R42")
        self.assertEqual(got.get_borrowed_books(), [])

    def test_retrieve_patron_nonexistent_returns_none(self):
        self.assertIsNone(self.db.retrieve_patron("NOPE"))

    def test_convert_patron_to_db_format_has_expected_shape(self):
        p = self._make_patron(memberID="S9", fname="Sophie", lname="Wilson",
                              age=25, borrowed=["b1", "b2"])
        data = self.db.convert_patron_to_db_format(p)
        self.assertEqual(
            set(data.keys()),
            {"fname", "lname", "age", "memberID", "borrowed_books"}
        )
        self.assertEqual(data["fname"], "Sophie")
        self.assertEqual(data["lname"], "Wilson")
        self.assertEqual(data["age"], 25)
        self.assertEqual(data["memberID"], "S9")
        self.assertEqual(data["borrowed_books"], ["b1", "b2"])

    def test_get_patron_count_reflects_number_of_rows(self):
        self.assertEqual(self.db.get_patron_count(), 0)
        self.db.insert_patron(self._make_patron(memberID="C1"))
        self.db.insert_patron(self._make_patron(memberID="C2"))
        self.assertEqual(self.db.get_patron_count(), 2)

    def test_close_db_is_safe_to_call(self):
        # Insert something
        self.db.insert_patron(self._make_patron(memberID="Z1"))
        # Should not raise
        self.db.close_db()
        # Re-open a new instance against same file: data persists to disk
        db2 = ldi.Library_DB()
        count = db2.get_patron_count()
        db2.close_db()
        self.assertEqual(count, 1)

