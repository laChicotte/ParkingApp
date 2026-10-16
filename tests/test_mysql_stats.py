"""Régressions des compteurs MySQL consommés par le tableau de bord."""
from decimal import Decimal
from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from app.database.mysql import Bdonnee


class MySQLStatsTests(unittest.TestCase):
    def database_returning(self, row):
        database = Bdonnee.__new__(Bdonnee)
        connection = MagicMock()
        connection.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = row
        database._connecter = MagicMock(return_value=connection)
        return database

    def test_decimal_counts_render_in_matplotlib_pie(self):
        database = self.database_returning((Decimal('5'), Decimal('3'), Decimal('2'), 10))
        stats = database.get_global_stats()
        self.assertTrue(all(type(value) is int for value in stats.values()))
        figure = Figure()
        axes = figure.subplots()
        wedges, _, _ = axes.pie(list(stats.values()), labels=list(stats), autopct='%1.1f%%')
        FigureCanvasAgg(figure).draw()
        self.assertEqual(len(wedges), 3)
        self.assertEqual(stats, {'etudiants': 5, 'enseignants': 3, 'Administratif': 2})

    def test_daily_decimal_counts_include_integer_balance(self):
        database = self.database_returning((Decimal('8'), Decimal('3')))
        stats = database.get_tab_values()
        self.assertEqual(list(stats.values()), [8, 3, 5])
        self.assertTrue(all(type(value) is int for value in stats.values()))

    def test_empty_tables_return_zero_counts(self):
        database = self.database_returning((None, None, None, 0))
        self.assertEqual(list(database.get_global_stats().values()), [0, 0, 0])
        database = self.database_returning((None, None))
        self.assertEqual(list(database.get_tab_values().values()), [0, 0, 0])

    def test_daily_movements_are_sorted_and_include_empty_days(self):
        database = self.database_returning(None)
        today = datetime.now().date()
        cursor = database._connecter.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [(today, Decimal('2'), Decimal('1'))]
        rows = database.get_daily_movements(7)
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0]['date'], today - timedelta(days=6))
        self.assertEqual(rows[0]['entries'], 0)
        self.assertEqual(rows[-1], {'date': today, 'entries': 2, 'exits': 1})
        cursor.execute.assert_called_once()
        self.assertEqual(cursor.execute.call_args.args[1], (today - timedelta(days=6), today))


if __name__ == '__main__':
    unittest.main()
