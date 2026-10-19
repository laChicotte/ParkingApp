"""Photos : suppression, changement d'identifiant et échecs sans perte."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pymysql
from app.database.mysql import Bdonnee
from app.utils.photos import photo_path, save_photo_atomic


class PhotoLifecycleTests(unittest.TestCase):
    def setUp(self):
        build = Path(__file__).resolve().parents[1] / 'build'
        build.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=build)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.images = self.root / 'images'
        self.images.mkdir()
        override = patch('app.config.paths.IMAGES_DIR', self.images)
        override.start()
        self.addCleanup(override.stop)
        popup = patch('app.database.mysql.messagebox')
        popup.start()
        self.addCleanup(popup.stop)
        self.db = Bdonnee.__new__(Bdonnee)
        self.db.tables = ['historique', 'users', 'owners']
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.db._connecter = MagicMock()
        self.db._connecter.return_value.__enter__.return_value = self.connection
        self.old = self.images / '005315.png'
        self.new = self.images / '005316.png'
        self.old.write_bytes(b'original photo')
        self.cursor.fetchone.side_effect = [('005315',), None]

    def test_owner_deletion_removes_photo_after_commit(self):
        self.connection.commit.side_effect = lambda: self.assertTrue(self.old.exists())
        self.assertTrue(self.db.supprimer(2, 1))
        self.assertFalse(self.old.exists())

    def test_account_deletion_removes_phone_photo(self):
        phone = self.images / '628123456.png'
        phone.write_bytes(b'account photo')
        self.cursor.fetchone.side_effect = [('628123456',), None]
        self.assertTrue(self.db.supprimer(1, 1))
        self.assertFalse(phone.exists())
        self.assertTrue(self.old.exists())

    def test_failed_delete_commit_keeps_photo(self):
        self.connection.commit.side_effect = pymysql.OperationalError('Unavailable')
        self.assertFalse(self.db.supprimer(2, 1))
        self.assertEqual(self.old.read_bytes(), b'original photo')

    def test_photo_still_referenced_by_another_record_is_preserved(self):
        self.cursor.fetchone.side_effect = [('005315',), (1,)]
        self.assertTrue(self.db.supprimer(2, 1))
        self.assertTrue(self.old.exists())

    def test_barcode_change_moves_photo_without_changing_content(self):
        self.assertTrue(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertFalse(self.old.exists())
        self.assertEqual(self.new.read_bytes(), b'original photo')

    def test_phone_change_moves_account_photo(self):
        self.cursor.fetchone.side_effect = [('005315',), None]
        self.assertTrue(self.db.modifier(1, 1, {'telephone': '628123456'}, notify=False))
        self.assertFalse(self.old.exists())
        self.assertEqual((self.images / '628123456.png').read_bytes(), b'original photo')

    def test_shared_photo_is_copied_for_new_identifier(self):
        self.cursor.fetchone.side_effect = [('005315',), (1,)]
        self.assertTrue(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertTrue(self.old.exists())
        self.assertEqual(self.new.read_bytes(), self.old.read_bytes())

    def test_failed_update_commit_keeps_old_photo_and_removes_copy(self):
        self.connection.commit.side_effect = pymysql.OperationalError('Unavailable')
        self.assertFalse(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertEqual(self.old.read_bytes(), b'original photo')
        self.assertFalse(self.new.exists())

    def test_existing_destination_is_never_overwritten(self):
        self.new.write_bytes(b'another photo')
        self.assertFalse(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertEqual(self.old.read_bytes(), b'original photo')
        self.assertEqual(self.new.read_bytes(), b'another photo')
        self.connection.commit.assert_not_called()

    def test_connection_close_error_after_commit_cannot_remove_new_photo(self):
        self.db._connecter.return_value.__exit__.side_effect = pymysql.OperationalError('Close failed')
        self.assertTrue(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertEqual(self.new.read_bytes(), b'original photo')
        self.assertFalse(self.old.exists())
        self.assertTrue(self.db.last_warning)

    def test_missing_photo_does_not_prevent_editing(self):
        self.old.unlink()
        self.assertTrue(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertFalse(self.new.exists())

    def test_unchanged_identifier_does_not_touch_photo(self):
        self.assertTrue(self.db.modifier(2, 1, {'code_barre': '005315'}, notify=False))
        self.assertEqual(self.old.read_bytes(), b'original photo')

    def test_cleanup_failure_is_reported_after_successful_commit(self):
        with patch('app.utils.photos.PhotoChange.finish', side_effect=PermissionError('File locked')):
            self.assertTrue(self.db.modifier(2, 1, {'code_barre': '005316'}, notify=False))
        self.assertIn('photo', self.db.last_warning)
        self.assertTrue(self.old.exists())
        self.assertTrue(self.new.exists())

    def test_invalid_photo_key_cannot_escape_image_directory(self):
        for key in ('../profil', '..\\profil', 'C:\\profil', 'folder/name'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                photo_path('owners', key)

    def test_new_capture_replaces_old_photo_in_same_file(self):
        save_photo_atomic(self.old, b'new photo')
        self.assertEqual(self.old.read_bytes(), b'new photo')
        self.assertEqual(list(self.images.iterdir()), [self.old])

    def test_failed_capture_preserves_existing_photo(self):
        with patch('app.utils.photos.Path.replace', side_effect=PermissionError('File locked')):
            with self.assertRaises(PermissionError):
                save_photo_atomic(self.old, b'new photo')
        self.assertEqual(self.old.read_bytes(), b'original photo')
        self.assertEqual(list(self.images.iterdir()), [self.old])

    def test_shared_reference_query_checks_owners_and_accounts(self):
        storage = sqlite3.connect(':memory:')
        self.addCleanup(storage.close)
        storage.create_function('CHAR_LENGTH', 1, len)
        storage.create_function('LPAD', 3, lambda value, width, char: value.rjust(width, char))
        storage.execute('CREATE TABLE owners (code_barre TEXT)')
        storage.execute('CREATE TABLE users (telephone TEXT)')
        cursor = MagicMock()
        sql_cursor = storage.cursor()
        cursor.execute.side_effect = lambda query, params: sql_cursor.execute(query.replace('%s', '?'), params)
        cursor.fetchone.side_effect = sql_cursor.fetchone
        self.assertFalse(self.db._photo_referenced(cursor, self.old))
        storage.execute("INSERT INTO owners VALUES ('5315')")
        self.assertTrue(self.db._photo_referenced(cursor, self.old))
        storage.execute('DELETE FROM owners')
        storage.execute("INSERT INTO users VALUES ('005315')")
        self.assertTrue(self.db._photo_referenced(cursor, self.old))


if __name__ == '__main__':
    unittest.main()
