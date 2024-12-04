from typing import Self
from dataclasses import dataclass
import base64
import time
from pathlib import Path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pytest_httpserver import HTTPServer

# https://www.emcken.dk/programming/2024/01/12/very-small-pdf-for-testing/
DATA_PDF = base64.b64decode('JVBERi0xLjQKMSAwIG9iago8PC9UeXBlIC9DYXRhbG9nCi9QYWdlcyAyIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagozIDAgb2JqCjw8L1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PC9Qcm9jU2V0IFsvUERGIC9UZXh0XQovRm9udCA8PC9GMSA0IDAgUj4+Cj4+Cj4+CmVuZG9iago0IDAgb2JqCjw8L1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9OYW1lIC9GMQovQmFzZUZvbnQgL0hlbHZldGljYQovRW5jb2RpbmcgL01hY1JvbWFuRW5jb2RpbmcKPj4KZW5kb2JqCjUgMCBvYmoKPDwvTGVuZ3RoIDUzCj4+CnN0cmVhbQpCVAovRjEgMjAgVGYKMjIwIDQwMCBUZAooRHVtbXkgUERGKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZgowMDAwMDAwMDA5IDAwMDAwIG4KMDAwMDAwMDA2MyAwMDAwMCBuCjAwMDAwMDAxMjQgMDAwMDAgbgowMDAwMDAwMjc3IDAwMDAwIG4KMDAwMDAwMDM5MiAwMDAwMCBuCnRyYWlsZXIKPDwvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0OTUKJSVFT0YK')
# https://www.w3schools.com/html/
DATA_HTML = '<!DOCTYPE html><html><head><title>Page Title</title></head><body><h1>This is a Heading</h1><p>This is a paragraph.</p></body></html>'
CONTENT_TYPE_HTML = 'text/html'
CONTENT_TYPE_PDF = 'application/pdf'

class HTTPHandler:
    def __init__(self, server: HTTPServer, subpath: str):
        self.server = server
        self.subpath = f'/{subpath}'
        self.enabled = False

    def url(self) -> str:
        return self.server.url_for(self.subpath)

    def enable(self, data: bytes=DATA_PDF, content_type: str=CONTENT_TYPE_PDF, status: int=200) -> Self:
        if not self.enabled:
            self.server.expect_request(self.subpath) \
                .respond_with_data(data, content_type=content_type, status=status)

            self.enabled = True

        return self

class HTTPHandlers:
    def __init__(self, server: HTTPServer, timeout=5.0):
        self.server = server

        server.expect_request("/timeout") \
            .respond_with_handler(lambda _: time.sleep(timeout))

        self._timeout = server.url_for('/timeout')

        self.pdf_pdf_200 = HTTPHandler(server, 'pdf_pdf_200') \
            .enable(DATA_PDF, content_type=CONTENT_TYPE_PDF, status=200)
        self.pdf_pdf_404 = HTTPHandler(server, 'pdf_pdf_404') \
            .enable(DATA_PDF, content_type=CONTENT_TYPE_PDF, status=404)
        self.pdf_html_200 = HTTPHandler(server, 'pdf_html_200') \
            .enable(DATA_PDF, content_type=CONTENT_TYPE_HTML, status=200)
        self.pdf_html_404 = HTTPHandler(server, 'pdf_html_404') \
            .enable(DATA_PDF, content_type=CONTENT_TYPE_HTML, status=404)
        self.html_pdf_200 = HTTPHandler(server, 'html_pdf_200') \
            .enable(DATA_HTML, content_type=CONTENT_TYPE_PDF, status=200)
        self.html_pdf_404 = HTTPHandler(server, 'html_pdf_404') \
            .enable(DATA_HTML, content_type=CONTENT_TYPE_PDF, status=404)
        self.html_html_200 = HTTPHandler(server, 'html_html_200') \
            .enable(DATA_HTML, content_type=CONTENT_TYPE_HTML, status=200)
        self.html_html_404 = HTTPHandler(server, 'html_html_404') \
            .enable(DATA_HTML, content_type=CONTENT_TYPE_HTML, status=404)

    def none(self) -> str:
        return ''

    def timeout(self) -> str:
        return self._timeout

    def valid(self) -> str:
        return self.pdf_pdf_200.url()

    def invalid(self) -> str:
        return self.html_html_404.url()