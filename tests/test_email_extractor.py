from pathlib import Path
import subprocess
import sys
import unittest

from email_extractor import extract_emails


ROOT = Path(__file__).resolve().parents[1]


class ExtractorTests(unittest.TestCase):
    def test_entities_mailto_multi_recipient_and_order(self):
        html = ('<p>forms&#64;example.org.</p>'
                '<a HREF="MAILTO:desk%2Bkit@example.org,queue@example.org'
                '?subject=hidden@example.org">queue@example.org</a>')
        self.assertEqual(extract_emails(html), [
            'forms@example.org', 'desk+kit@example.org', 'queue@example.org'])

    def test_dedup_uses_first_spelling_and_position(self):
        html = ('<a href="mailto:Desk@EXAMPLE.ORG">desk@example.org</a>'
                '<p>studio@example.org, DESK@example.org.</p>')
        self.assertEqual(extract_emails(html), ['Desk@example.org', 'studio@example.org'])

    def test_ignored_content_and_empty_input(self):
        html = ('<!-- draft@example.org --><script>draft@example.org</script>'
                '<style>/* paint@example.org */</style>'
                '<a href="https://example.org/?q=file@example.org">read more</a>')
        for value in ('', html):
            with self.subTest(html=value):
                self.assertEqual(extract_emails(value), [])

    def run_cli(self, filename):
        return subprocess.run([sys.executable, str(ROOT / 'email_extractor.py'),
                               str(ROOT / 'examples' / filename)],
                              capture_output=True, text=True)

    def test_documented_demo(self):
        result = self.run_cli('workshop.html')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'studio@example.org\npaper+kit@example.org\n')

    def test_no_result_is_success_without_output(self):
        result = self.run_cli('no-addresses.html')
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))

    def test_missing_file_has_cli_error(self):
        result = self.run_cli('missing.html')
        self.assertEqual(result.returncode, 2)
        self.assertIn('missing.html', result.stderr)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
