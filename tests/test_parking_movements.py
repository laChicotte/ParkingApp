"""Règle d'alternance des passages et verrouillage de la moto."""
from datetime import date, time
import unittest
from unittest.mock import MagicMock

import pymysql

from app.database.mysql import Bdonnee


class ParkingMovementTests(unittest.TestCase):
    def database(self, previous=None, owner_exists=True):
        database = Bdonnee.__new__(Bdonnee)
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.side_effect = [(42,) if owner_exists else None,
                                       (previous,) if previous is not None else None]
        database._connecter = MagicMock()
        database._connecter.return_value.__enter__.return_value = connection
        return database, connection, cursor

    def insert(self, database, movement):
        return database.ajouter_historique('16-10-2026', 42, movement, '14h20min')

    def test_first_entry_is_allowed(self):
        database, connection, cursor = self.database()
        self.assertTrue(self.insert(database, 'Entrée'))
        self.assertEqual(cursor.execute.call_args.args[1], (date(2026, 10, 16), 42, 'Entrée', time(14, 20)))
        connection.commit.assert_called_once()

    def test_first_exit_is_refused(self):
        database, connection, cursor = self.database()
        self.assertFalse(self.insert(database, 'Sortie'))
        self.assertIn('aucune entrée', database.last_error)
        connection.commit.assert_not_called()
        connection.rollback.assert_called_once()
        self.assertEqual(cursor.execute.call_count, 2)

    def test_repeated_entry_and_repeated_exit_are_refused(self):
        for movement in ('Entrée', 'Sortie'):
            with self.subTest(movement=movement):
                database, connection, cursor = self.database(movement)
                self.assertFalse(self.insert(database, movement))
                self.assertIn('déjà', database.last_error)
                self.assertEqual(cursor.execute.call_count, 2)
                connection.commit.assert_not_called()
                connection.rollback.assert_called_once()

    def test_alternating_movements_are_allowed(self):
        for previous, movement in (('Entrée', 'Sortie'), ('Sortie', 'Entrée')):
            with self.subTest(previous=previous):
                database, connection, cursor = self.database(previous)
                self.assertTrue(self.insert(database, movement))
                self.assertEqual(database.last_error, '')
                connection.commit.assert_called_once()

    def test_moto_is_locked_before_last_movement_is_read(self):
        database, connection, cursor = self.database()
        self.insert(database, 'Entrée')
        connection.begin.assert_called_once()
        queries = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertIn('owners', queries[0])
        self.assertIn('FOR UPDATE', queries[0])
        self.assertIn('ORDER BY id DESC', queries[1])
        self.assertIn('FOR UPDATE', queries[1])
        self.assertIn('INSERT INTO historique', queries[2])

    def test_deleted_moto_is_refused(self):
        database, connection, cursor = self.database(owner_exists=False)
        self.assertFalse(self.insert(database, 'Entrée'))
        self.assertEqual(cursor.execute.call_count, 1)
        connection.commit.assert_not_called()

    def test_invalid_movement_does_not_connect(self):
        database, _, _ = self.database()
        self.assertFalse(self.insert(database, 'Autre'))
        database._connecter.assert_not_called()

    def test_database_failure_has_message_without_ui_popup(self):
        database, connection, cursor = self.database()
        cursor.execute.side_effect = pymysql.OperationalError('Test database unavailable')
        self.assertFalse(self.insert(database, 'Entrée'))
        self.assertIn('Impossible', database.last_error)
        connection.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
