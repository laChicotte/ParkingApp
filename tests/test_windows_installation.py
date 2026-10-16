"""Chemins de distribution et préparation MySQL sans installation ni fenêtre."""
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import MagicMock, patch

import pymysql

from app.config.installation import prepare_database


class WindowsInstallationTests(unittest.TestCase):
    def test_frozen_paths_keep_configuration_outside_installation(self):
        with patch.object(sys, 'frozen', True, create=True), patch.object(sys, '_MEIPASS', 'C:/bundle/_internal', create=True), patch.dict('os.environ', {'LOCALAPPDATA': 'C:/user/AppData/Local'}):
            paths = runpy.run_path('app/config/paths.py')
        self.assertEqual(paths['RESOURCES_DIR'], Path('C:/bundle/_internal/resources'))
        self.assertEqual(paths['CONFIG_FILE'], Path('C:/user/AppData/Local/UKAG Parking/config/config.json'))
        self.assertEqual(paths['IMAGES_DIR'], Path('C:/user/AppData/Local/UKAG Parking/images'))

    def test_missing_database_is_created_after_connecting(self):
        config = dict(host='127.0.0.1', port=3306, user='root', password='', db_name='parkingapp')
        connection = MagicMock()
        connection.select_db.side_effect = [pymysql.OperationalError(1049, 'Unknown database'), None]
        with patch('app.config.installation.pymysql.connect') as connect:
            connect.return_value.__enter__.return_value = connection
            prepare_database(config)
        connection.cursor.return_value.__enter__.return_value.execute.assert_called_once()
        self.assertEqual(connection.select_db.call_count, 2)

    def test_existing_database_is_not_modified(self):
        config = dict(host='127.0.0.1', port=3306, user='root', password='', db_name='parkingapp')
        with patch('app.config.installation.pymysql.connect') as connect:
            connection = connect.return_value.__enter__.return_value
            prepare_database(config)
            connection.cursor.assert_not_called()

    def test_unsafe_database_name_is_rejected_before_connecting(self):
        config = dict(host='127.0.0.1', port=3306, user='root', password='', db_name='bad`; DROP DATABASE x')
        with patch('app.config.installation.pymysql.connect') as connect:
            with self.assertRaises(ValueError):
                prepare_database(config)
            connect.assert_not_called()


if __name__ == '__main__':
    unittest.main()
