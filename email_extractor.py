"""Extract addresses from local HTML text and mailto recipients."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote


ATOM = r"[A-Za-z0-9_+%'-]+"
LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
ADDRESS = rf"{ATOM}(?:\.{ATOM})*@(?:{LABEL}\.)+[A-Za-z]{{2,63}}"
TEXT_ADDRESS = re.compile(rf"(?<![\w.+%@'-])({ADDRESS})(?![\w@-]|\.[A-Za-z0-9])", re.ASCII)


class _AddressParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.addresses = {}
        self.skipped = None

    def _remember(self, address):
        local, domain = address.rsplit('@', 1)
        self.addresses.setdefault(address.lower(), f'{local}@{domain.lower()}')

    def handle_starttag(self, tag, attrs):
        if self.skipped:
            return
        if tag in ('script', 'style'):
            self.skipped = tag
        elif tag == 'a':
            href = (dict(attrs).get('href') or '').strip()
            if href.lower().startswith('mailto:'):
                path = re.split(r'[?#]', href[7:], maxsplit=1)[0]
                for part in path.split(','):
                    address = unquote(part).strip()
                    if re.fullmatch(ADDRESS, address):
                        self._remember(address)

    def handle_endtag(self, tag):
        if tag == self.skipped:
            self.skipped = None

    def handle_data(self, data):
        if self.skipped is None:
            for match in TEXT_ADDRESS.finditer(data):
                self._remember(match.group(1))


def extract_emails(html: str) -> list[str]:
    """Return unique addresses in first-seen order, comparing without case."""
    parser = _AddressParser()
    parser.feed(html)
    parser.close()
    return list(parser.addresses.values())


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('file', type=Path, help='path to a UTF-8 HTML file')
    args = cli.parse_args()
    try:
        html = args.file.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        cli.exit(2, f'{cli.prog}: {exc}\n')
    for address in extract_emails(html):
        print(address)
    return 0


if __name__ == '__main__':
    sys.exit(main())
