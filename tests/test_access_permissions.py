"""État des droits et protection des actions désactivées."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.config.permissions import has_permission
from app.models.user import User
from app.views.owners_view import OwnersView
from app.views.user_management_view import UserManagementView


class AccessPermissionTests(unittest.TestCase):
    def test_standard_user_can_scan_but_cannot_administer(self):
        with patch('app.config.settings.is_connected', True), patch('app.config.settings.current_user', User(role=0)):
            self.assertTrue(has_permission('scan_entries'))
            self.assertTrue(has_permission('edit_owners'))
            for permission in ('manage_owners', 'manage_users', 'manage_admins'):
                self.assertFalse(has_permission(permission))
            for permission in ('view_dashboard', 'view_owners', 'view_history'):
                self.assertTrue(has_permission(permission))

    def test_admin_and_super_admin_keep_their_actions(self):
        for role in (1, 2):
            with self.subTest(role=role), patch('app.config.settings.is_connected', True), patch('app.config.settings.current_user', User(role=role)):
                for permission in ('edit_owners', 'manage_owners', 'manage_users', 'view_dashboard'):
                    self.assertTrue(has_permission(permission))

    def test_disconnected_session_cannot_use_privileged_actions(self):
        with patch('app.config.settings.is_connected', False), patch('app.config.settings.current_user', User(role=1)):
            self.assertFalse(has_permission('manage_users'))
            self.assertTrue(has_permission('scan_entries'))
            self.assertTrue(has_permission('scan_exits'))
            for permission in ('view_owners', 'view_history', 'view_dashboard', 'edit_owners', 'manage_owners'):
                self.assertFalse(has_permission(permission))

    def test_agent_can_open_add_and_edit_forms_but_cannot_delete_or_export(self):
        view = SimpleNamespace(main_window=MagicMock(), _show_owner_form=MagicMock(), tree=MagicMock())
        view.tree.selection.return_value = ('42',)
        with patch('app.config.settings.is_connected', True), patch('app.config.settings.current_user', User(role=0)):
            OwnersView.add_owner(view)
            view._show_owner_form.assert_called_once_with()
            view._show_owner_form.reset_mock()
            OwnersView.update_owner(view)
            view._show_owner_form.assert_called_once_with(42)
            self.assertFalse(OwnersView.supprimer(view))
            self.assertFalse(OwnersView.exporter(view))

    def test_agent_buttons_enable_editing_but_keep_delete_and_export_grey(self):
        buttons = [MagicMock() for _ in range(5)]
        photo = MagicMock()
        view = SimpleNamespace(action_buttons=buttons, change_photo_btn=photo)
        with patch('app.config.settings.is_connected', True), patch('app.config.settings.current_user', User(role=0)):
            OwnersView.update_permissions(view)
        for button in (buttons[1], buttons[2], photo):
            button.state.assert_called_once_with(['!disabled'])
        for button in (buttons[3], buttons[4]):
            button.state.assert_called_once_with(['disabled'])

    def test_anonymous_search_cannot_load_personal_data(self):
        with patch('app.config.settings.is_connected', False), patch('app.views.owners_view.Bdonnee') as database:
            self.assertEqual(OwnersView._load_search('Diallo'), ([], 'Accès refusé.'))
            database.assert_not_called()

    def test_anonymous_cannot_load_lists_even_by_calling_view_methods(self):
        from app.views.historique_view import HistoriqueView
        from app.views.dashboard_view import DashboardView
        view = SimpleNamespace(main_window=MagicMock())
        with patch('app.config.settings.is_connected', False), \
             patch('app.views.owners_view.Bdonnee') as owners, \
             patch('app.views.historique_view.Bdonnee') as history, \
             patch('app.views.dashboard_view.Bdonnee') as dashboard, \
             patch('app.views.user_management_view.Bdonnee') as accounts:
            for action in (OwnersView.afficher_owners, OwnersView.rechercher,
                           HistoriqueView.afficher_historique, DashboardView.refresh,
                           UserManagementView.load_users):
                self.assertFalse(action(view))
            for database in (owners, history, dashboard, accounts):
                database.assert_not_called()

    def test_existing_role_zero_is_displayed_as_parking_agent(self):
        self.assertEqual(User(role=0).get_role_name(), 'Agent de parking')

    def test_direct_owner_actions_cannot_bypass_disabled_buttons(self):
        view = SimpleNamespace(main_window=MagicMock())
        with patch('app.config.settings.is_connected', False), patch('app.views.owners_view.Bdonnee') as db:
            for action in (OwnersView.add_owner, OwnersView.update_owner, OwnersView.supprimer,
                           OwnersView.exporter, OwnersView.change_photo):
                self.assertFalse(action(view))
            self.assertFalse(OwnersView._save_owner(view, {}, 1, MagicMock()))
            db.assert_not_called()

    def test_user_actions_are_guarded_after_session_expires(self):
        view = SimpleNamespace(main_window=MagicMock())
        with patch('app.config.settings.is_connected', False), patch('app.views.user_management_view.Bdonnee') as db:
            for action in (UserManagementView.add_user, UserManagementView.edit_user, UserManagementView.delete_user):
                self.assertFalse(action(view))
            self.assertFalse(UserManagementView._save_user(view, {}, 1, MagicMock()))
            db.assert_not_called()


if __name__ == '__main__':
    unittest.main()
