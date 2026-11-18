# Local HTML email extractor

Find email addresses in a saved HTML file. The CLI prints one address per line in document order. It reads a local UTF-8 file and writes the results to standard output. The examples use fictional workshop addresses.

## Quick start

From the repository root, run with Python 3.9 or newer. All dependencies ship with Python.

```sh
python3 email_extractor.py examples/workshop.html
```

Expected output:

```text
studio@example.org
paper+kit@example.org
```

To try a file with no addresses, run `python3 email_extractor.py examples/no-addresses.html`. It exits successfully and prints nothing. An unreadable file or invalid UTF-8 produces a diagnostic on standard error and exit code 2.

## Extraction rules

The parser reads individual HTML text nodes and the primary recipients in `mailto:` links. It decodes HTML character references, decodes percent-encoded recipients, and skips comments, scripts, styles, and link query parameters. A link's recipients occur before its label in document order.

Matching covers common ASCII addresses with dotted domains and includes plus addressing. Quoted local parts, internationalized addresses, and addresses split across text nodes are outside the supported format. Matching treats the whole address case-insensitively for deduplication, preserves the first local-part spelling, and lowercases the domain. Each address appears once. Parsing runs entirely on the supplied HTML.

## Python API

```python
from email_extractor import extract_emails

assert extract_emails('<p>studio&#64;example.org</p>') == ['studio@example.org']
```

## Tests

```sh
python3 -m unittest discover -s tests -v
```
