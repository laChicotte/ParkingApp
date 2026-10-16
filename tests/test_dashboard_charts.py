"""Vérifie les figures réellement affichées sans ouvrir de fenêtre Tkinter."""
from datetime import date, timedelta
from decimal import Decimal
import unittest

from matplotlib.backends.backend_agg import FigureCanvasAgg

from app.components.dashboard_charts import movement_figure, category_figure


class DashboardChartTests(unittest.TestCase):
    def assert_labels_inside(self, figure):
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        for text in figure.findobj(lambda artist: hasattr(artist, 'get_text')):
            if text.get_visible() and text.get_text():
                box = text.get_window_extent(renderer)
                self.assertGreaterEqual(box.x0, -1, text.get_text())
                self.assertGreaterEqual(box.y0, -1, text.get_text())
                self.assertLessEqual(box.x1, figure.bbox.width + 1, text.get_text())
                self.assertLessEqual(box.y1, figure.bbox.height + 1, text.get_text())

    def test_periods_have_short_labels_and_separate_counts(self):
        for days in (7, 15, 30):
            with self.subTest(days=days):
                data = [{'date': date(2026, 9, 17) + timedelta(days=i),
                         'entries': i % 4, 'exits': i % 3} for i in range(days)]
                figure = movement_figure(data)
                figure.set_size_inches(4.2, 2.8)
                axes = figure.axes[0]
                self.assertEqual(sum(patch.get_height() for patch in axes.containers[0]),
                                 sum(row['entries'] for row in data))
                self.assertEqual(sum(patch.get_height() for patch in axes.containers[1]),
                                 sum(row['exits'] for row in data))
                self.assertLessEqual(len(axes.get_xticklabels()), 7)
                self.assert_labels_inside(figure)

    def test_category_counts_and_percentages_fit_small_panel(self):
        figure = category_figure({'Etudiant': Decimal(552), 'Enseignant': 30, 'Personnel': 31})
        figure.set_size_inches(3.1, 2.8)
        texts = [text.get_text() for text in figure.axes[0].texts]
        self.assertIn('552  (90,0 %)', texts)
        self.assertIn('31  (5,1 %)', texts)
        self.assertIn('Enseignants', texts)
        self.assert_labels_inside(figure)

    def test_empty_data_has_explanation(self):
        for figure in (movement_figure([]), category_figure({})):
            self.assertTrue(figure.axes[0].texts)
            self.assert_labels_inside(figure)


if __name__ == '__main__':
    unittest.main()
