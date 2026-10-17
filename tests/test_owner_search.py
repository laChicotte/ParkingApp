"""Recherche multi-champs et affichage d'une liste sans résultats."""
import sqlite3
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.database.mysql import Bdonnee
from app.views.owners_view import OwnersView


class OwnerSearchTests(unittest.TestCase):
    def setUp(self):
        self.storage = sqlite3.connect(':memory:')
        self.addCleanup(self.storage.close)
        self.storage.row_factory = sqlite3.Row
        self.storage.execute('CREATE TABLE owners (id INTEGER PRIMARY KEY, nom TEXT, prenom TEXT, matricule TEXT, telephone TEXT, immatriculation TEXT, code_barre TEXT)')
        self.storage.executemany('INSERT INTO owners VALUES (?, ?, ?, ?, ?, ?, ?)', [
            (1, 'Diallo', 'Mamadou Alpha', 'UKAG-2026-123', '628123456', 'RG 123 AD', '005315'),
            (2, "O'Connor", 'Marie', None, '621987654', 'RG 456 AB', '005316'),
            (3, 'Test%_=', 'Paul', '', '620000000', 'RG 000 ZZ', '005317'),
        ])
        self.database = Bdonnee.__new__(Bdonnee)
        self.database._connecter = MagicMock()
        connection = self.database._connecter.return_value.__enter__.return_value
        cursor = connection.cursor.return_value.__enter__.return_value
        sql_cursor = self.storage.cursor()
        cursor.execute.side_effect = lambda query, params: sql_cursor.execute(query.replace('%s', '?'), params)
        cursor.fetchall.side_effect = lambda: [dict(row) for row in sql_cursor.fetchall()]

    def ids(self, query):
        return [row['id'] for row in self.database.rechercher_owner(query)]

    def test_partial_match_in_each_searchable_field(self):
        for query in ('dial', 'mamad', '2026-123', '628123', '123 AD', '5315'):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), [1])

    def test_full_name_in_either_order(self):
        for query in ('Diallo Mamadou', 'Alpha DIALLO', '  dial  alpha  '):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), [1])

    def test_words_must_all_match(self):
        self.assertEqual(self.ids('Diallo Marie'), [])

    def test_special_characters_are_literal(self):
        for query in ('%', '_', '='):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), [3])
        self.assertEqual(self.ids("O'Con"), [2])

    def test_empty_query_returns_everyone(self):
        self.assertEqual(sorted(self.ids('   ')), [1, 2, 3])

    def test_unknown_value_returns_empty_list(self):
        self.assertEqual(self.ids('introuvable'), [])

    def test_query_cannot_change_sql(self):
        self.assertEqual(self.ids("' OR 1=1 --"), [])

    def test_empty_result_clears_previous_table(self):
        view = SimpleNamespace(search_var=MagicMock(), results_var=MagicMock(), tree=MagicMock())
        view.search_var.get.return_value = 'introuvable'
        view.tree.get_children.return_value = ('old',)
        with patch('app.config.permissions.has_permission', return_value=True):
            OwnersView._render_search_results(view, [])
        view.tree.delete.assert_called_once_with('old')
        view.results_var.set.assert_called_once_with('Aucun résultat')
        view.tree.insert.assert_not_called()


if __name__ == '__main__':
    unittest.main()
