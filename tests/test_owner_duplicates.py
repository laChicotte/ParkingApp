"""Doublons à l'ajout et lors de la modification de la même fiche."""
import sqlite3
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.database.mysql import Bdonnee
from app.views.owners_view import OwnersView


class OwnerDuplicateTests(unittest.TestCase):
    def setUp(self):
        allowed = patch('app.config.permissions.has_permission', return_value=True)
        allowed.start()
        self.addCleanup(allowed.stop)
        # Exécuter réellement le prédicat SQL, avec les paramètres du backend.
        self.storage = sqlite3.connect(":memory:")
        self.addCleanup(self.storage.close)
        self.storage.execute("CREATE TABLE owners (id INTEGER PRIMARY KEY, code_barre TEXT COLLATE NOCASE, immatriculation TEXT COLLATE NOCASE)")
        self.storage.executemany("INSERT INTO owners VALUES (?, ?, ?)",
                                 [(1, '005315', 'RG 123 AD'), (2, '005316', 'RG 456 AD')])
        self.database = Bdonnee.__new__(Bdonnee)
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        sql_cursor = self.storage.cursor()
        cursor.execute.side_effect = lambda query, params: sql_cursor.execute(query.replace('%s', '?'), params)
        cursor.fetchall.side_effect = sql_cursor.fetchall
        self.database._connecter = MagicMock()
        self.database._connecter.return_value.__enter__.return_value = connection

    def test_own_barcode_and_plate_can_be_kept(self):
        self.assertEqual(self.database.verifier_existence('005315', 'RG 123 AD', exclude_id=1), (False, ''))

    def test_other_barcode_is_refused_during_edit(self):
        conflict, message = self.database.verifier_existence('005316', 'RG 123 AD', exclude_id=1)
        self.assertTrue(conflict)
        self.assertIn('code-barre', message)
        self.assertNotIn('immatriculation', message)

    def test_other_plate_is_refused_during_edit(self):
        conflict, message = self.database.verifier_existence('005315', 'RG 456 AD', exclude_id=1)
        self.assertTrue(conflict)
        self.assertIn('immatriculation', message)
        self.assertNotIn('code-barre', message)

    def test_both_duplicates_are_reported_on_add(self):
        conflict, message = self.database.verifier_existence('005315', 'RG 456 AD')
        self.assertTrue(conflict)
        self.assertIn('code-barre', message)
        self.assertIn('immatriculation', message)

    def test_database_comparison_handles_plate_case(self):
        conflict, message = self.database.verifier_existence('new', 'rg 456 ad', exclude_id=1)
        self.assertTrue(conflict)
        self.assertIn('immatriculation', message)

    def test_unused_values_are_allowed(self):
        self.assertEqual(self.database.verifier_existence('005399', 'NEW'), (False, ''))

    def test_form_excludes_current_owner_and_saves(self):
        view = SimpleNamespace(afficher_owners=MagicMock(), _report_owner_conflict=OwnersView._report_owner_conflict)
        values = dict(nom='Diallo', prenom='Alpha', telephone='628123456', plaque='RG 123 AD',
                      code_barre='005315', couleur='Bleue', statut='Personnel')
        dialog = MagicMock()
        with patch('app.views.owners_view.Bdonnee') as factory, patch('app.views.owners_view.messagebox'):
            database = factory.return_value
            database.verifier_existence.side_effect = self.database.verifier_existence
            database.modifier.return_value = True
            OwnersView._save_owner(view, values, 1, dialog)
            database.verifier_existence.assert_called_once_with('005315', 'RG 123 AD', exclude_id=1)
            database.modifier.assert_called_once()
            dialog.destroy.assert_called_once()

    def test_conflict_prevents_saving_the_form(self):
        view = SimpleNamespace(afficher_owners=MagicMock(), _report_owner_conflict=OwnersView._report_owner_conflict)
        values = dict(nom='Diallo', prenom='Alpha', telephone='628123456', plaque='RG 123 AD',
                      code_barre='005316', couleur='Bleue', statut='Personnel')
        with patch('app.views.owners_view.Bdonnee') as factory, patch('app.views.owners_view.messagebox'):
            database = factory.return_value
            database.verifier_existence.side_effect = self.database.verifier_existence
            OwnersView._save_owner(view, values, 1, MagicMock())
            database.modifier.assert_not_called()


if __name__ == '__main__':
    unittest.main()
