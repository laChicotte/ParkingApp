"""Connexion : erreurs intégrées et succès sans boîte de dialogue."""
import unittest
from unittest.mock import MagicMock, patch

from app.views.connexion_dialog import ConnexionDialog


class LoginFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.login = ConnexionDialog.__new__(ConnexionDialog)
        for name in ('user_entry', 'password_entry', 'user_field', 'password_field',
                     'error_label', 'dialog', 'main_window'):
            setattr(self.login, name, MagicMock())
        self.login.user_entry.get.return_value = 'alpha'
        self.login.password_entry.get.return_value = 'secret'
        self.login._show_error = MagicMock()

    def test_missing_fields_show_inline_errors_without_connecting(self):
        self.login.user_entry.get.return_value = ''
        with patch('app.views.connexion_dialog.Bdonnee') as database:
            self.login.me_connecter()
        database.assert_not_called()
        self.login.user_field.set_error.assert_called_with('Indiquez votre nom d’utilisateur.')
        self.login.dialog.destroy.assert_not_called()

    def test_wrong_credentials_keep_both_fields(self):
        with patch('app.views.connexion_dialog.Bdonnee') as factory:
            factory.return_value.last_error = ''
            factory.return_value.get_user.return_value = None
            self.login.me_connecter()
        self.assertIn('incorrect', self.login.password_field.set_error.call_args.args[0])
        self.login.user_entry.delete.assert_not_called()
        self.login.password_entry.delete.assert_not_called()
        self.login.dialog.destroy.assert_not_called()

    def test_database_error_stays_in_login_window(self):
        with patch('app.views.connexion_dialog.Bdonnee', side_effect=RuntimeError('Unavailable')):
            self.login.me_connecter()
        self.login._show_error.assert_called_once()
        self.login.dialog.destroy.assert_not_called()

    def test_success_closes_login_and_uses_temporary_notification(self):
        with patch('app.views.connexion_dialog.Bdonnee') as factory, \
             patch('app.views.connexion_dialog.User') as model, \
             patch('app.config.settings.current_user'), patch('app.config.settings.is_connected', False):
            factory.return_value.last_error = ''
            factory.return_value.get_user.return_value = dict(id=1, username='alpha', email='alpha@example.org', password='hash', role=0)
            model.return_value.verify_password.return_value = True
            model.return_value.name.return_value = 'alpha'
            self.login.me_connecter()
        self.login.dialog.destroy.assert_called_once()
        self.login.main_window.show_notification.assert_called_once_with('Connexion réussie. Bienvenue alpha !')
        self.login.main_window.refresh_permissions.assert_called_once()


if __name__ == '__main__':
    unittest.main()
