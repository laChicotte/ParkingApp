"""Retours non bloquants et protection contre les résultats de recherche périmés."""
import unittest
from types import SimpleNamespace, MethodType
from unittest.mock import MagicMock, patch

from app.views.accueil_view import AccueilView
from app.views.owners_view import OwnersView
from app.components.modern_form import ModernForm
from app.database.mysql import Bdonnee
from app.utils.sound import play_scan_sound
import pymysql


class FastScanTests(unittest.TestCase):
    def setUp(self):
        self.view = SimpleNamespace(_processing_scan=False, scanning=True, scan_mode=True,
                                     _display_owner=MagicMock(), set_photo=MagicMock(),
                                     _show_feedback=MagicMock(), hidden_entry=MagicMock(), hidden_entry1=MagicMock())
        self.factory = patch('app.views.accueil_view.Bdonnee').start()
        self.addCleanup(patch.stopall)
        patch('app.views.accueil_view.settings.is_connected', True).start()
        user = patch('app.views.accueil_view.settings.current_user').start()
        user.has_permission.return_value = True
        self.db = self.factory.return_value
        self.db.last_error = ''
        self.db.rechercher_par_code_barre.return_value = dict(id=1, nom='Diallo', prenom='Alpha')

    def test_success_and_next_scan_keep_reader_focus(self):
        self.db.ajouter_historique.return_value = True
        for _ in range(2):
            AccueilView.scan_display(self.view, '005315', True)
        self.assertEqual(self.db.ajouter_historique.call_count, 2)
        self.assertEqual(self.view.hidden_entry.focus_set.call_count, 2)
        self.assertEqual(self.view._show_feedback.call_args.kwargs, {'success': True})
        self.assertFalse(self.view._processing_scan)

    def test_refusal_explains_reason_and_does_not_stop_scanning(self):
        self.db.ajouter_historique.return_value = False
        self.db.last_error = 'Une entrée est déjà enregistrée.'
        AccueilView.scan_display(self.view, '005315', True)
        self.assertIn('déjà', self.view._show_feedback.call_args.args[0])
        self.assertEqual(self.view._show_feedback.call_args.kwargs, {'success': False})
        self.assertTrue(self.view.scanning)

    def test_unknown_code_clears_previous_person_without_insert(self):
        self.db.rechercher_par_code_barre.return_value = None
        AccueilView.scan_display(self.view, '005999', True)
        self.view._display_owner.assert_called_once_with({})
        self.db.ajouter_historique.assert_not_called()

    def test_invalid_code_does_not_connect(self):
        AccueilView.scan_display(self.view, 'abc', True)
        self.factory.assert_not_called()

    def test_anonymous_session_can_record_passage(self):
        with patch('app.views.accueil_view.settings.is_connected', False):
            AccueilView.scan_display(self.view, '005315', True)
        self.db.ajouter_historique.assert_called_once()
        self.view._display_owner.assert_called_once()

    def test_database_failure_restores_focus_and_processing_state(self):
        self.factory.side_effect = RuntimeError('Base indisponible')
        AccueilView.scan_display(self.view, '005315', True)
        self.view.hidden_entry.focus_set.assert_called_once()
        self.assertFalse(self.view._processing_scan)
        self.assertIn('non enregistré', self.view._show_feedback.call_args.args[0])


class LiveSearchTests(unittest.TestCase):
    def test_typing_cancels_pending_search_and_waits_for_pause(self):
        view = SimpleNamespace(_search_job='old', _search_poll=None, _search_future=None,
                               _search_generation=0, after_cancel=MagicMock(), after=MagicMock(), rechercher=MagicMock())
        view._cancel_search = MethodType(OwnersView._cancel_search, view)
        OwnersView._schedule_search(view)
        view.after_cancel.assert_called_once_with('old')
        view.after.assert_called_once_with(350, view.rechercher)

    def test_previous_results_cannot_replace_new_query(self):
        view = SimpleNamespace(_search_generation=2, _search_future=MagicMock(), _render_search_results=MagicMock())
        OwnersView._poll_search(view, 1)
        view._search_future.done.assert_not_called()
        view._render_search_results.assert_not_called()

    def test_worker_failure_returns_error_without_ui(self):
        with patch('app.views.owners_view.has_permission', return_value=True), patch('app.views.owners_view.Bdonnee', side_effect=RuntimeError('Unavailable')):
            self.assertEqual(OwnersView._load_search('Diallo'), ([], 'Unavailable'))


class InlineValidationTests(unittest.TestCase):
    def test_required_whitespace_is_refused_without_losing_other_values(self):
        name, phone = MagicMock(), MagicMock()
        name.get_value.return_value = '   '
        phone.get_value.return_value = '628123456'
        view = SimpleNamespace(fields={'nom': name, 'telephone': phone},
                               fields_config={'nom': {'label': 'Nom *'}, 'telephone': {'label': 'Téléphone *'}},
                               show_errors=MagicMock())
        self.assertFalse(ModernForm.validate(view))
        view.show_errors.assert_called_once_with({'nom': 'Ce champ est obligatoire.'})
        phone.set_value.assert_not_called()


class SilentFeedbackTests(unittest.TestCase):
    def test_database_errors_can_be_reported_without_popup(self):
        for method, arguments in (
            ('ajouter', (2, ['test'])), ('modifier', (2, 1, {'nom': 'test'})),
            ('rechercher_par_code_barre', ('005315',)), ('rechercher_owner', ('Diallo',)),
            ('get_user', ('test',)),
        ):
            with self.subTest(method=method), patch('app.database.mysql.messagebox') as popup:
                db = Bdonnee.__new__(Bdonnee)
                db.tables = ['historique', 'users', 'owners']
                db._connecter = MagicMock(side_effect=pymysql.OperationalError('Unavailable'))
                getattr(db, method)(*arguments, notify=False)
                self.assertIn('Unavailable', db.last_error)
                popup.showerror.assert_not_called()

    def test_success_and_refusal_use_distinct_async_sounds(self):
        sound = SimpleNamespace(PlaySound=MagicMock(), SND_ALIAS=1, SND_ASYNC=2)
        widget = MagicMock()
        with patch('app.utils.sound.winsound', sound):
            play_scan_sound(True, widget)
            play_scan_sound(False, widget)
        self.assertEqual([call.args for call in sound.PlaySound.call_args_list],
                         [('SystemAsterisk', 3), ('SystemHand', 3)])
        widget.bell.assert_not_called()


if __name__ == '__main__':
    unittest.main()
