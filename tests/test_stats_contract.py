import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StatsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_source = (ROOT / 'app.py').read_text(encoding='utf-8')
        cls.main_source = (ROOT / 'static' / 'js' / 'main.js').read_text(encoding='utf-8')
        cls.production_template = (ROOT / 'templates' / 'production.html').read_text(encoding='utf-8')

    def test_every_stats_fetch_has_a_flask_route(self):
        paths = re.findall(r"fetch\('(/api/[^']+)'\)", self.main_source)
        self.assertEqual(
            paths,
            ['/api/dashboard-stats', '/api/production-stats', '/api/quality-stats', '/api/equipment-stats'],
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertIn(f"@app.route('{path}')", self.app_source)

    def test_production_stats_route_returns_fields_used_by_refresh(self):
        route = self.app_source.split("@app.route('/api/production-stats')", 1)[1].split('@app.route(', 1)[0]
        stats_method = self.app_source.split('def get_production_stats(self):', 1)[1].split('def get_quality_stats(self):', 1)[0]
        for field in ('total', 'completed', 'in_progress', 'completion_rate'):
            with self.subTest(field=field):
                self.assertIn(f"'{field}'", stats_method)
        for field in ('running', 'paused', 'pending'):
            with self.subTest(field=field):
                self.assertIn(f"'{field}'", route)

    def test_production_page_has_no_missing_runtime_helpers(self):
        self.assertNotIn('moment()', self.production_template)
        self.assertNotIn("querySelectorAll('#task-row-' + taskId)", self.production_template)


if __name__ == '__main__':
    unittest.main()
