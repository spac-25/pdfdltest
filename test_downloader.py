import pytest
from pytest_httpserver import HTTPServer

import test_util
import Downloader

from typing import Optional
from pathlib import Path

def download(dir: Path, url:str, fallback: Optional[str] = None, timeout: float=1.0) -> tuple[Path, bool]:
    path = dir.joinpath(f'test.pdf')
    result = Downloader.Downloader().download(
        url=url,
        destination_path=path,
        alt_url=fallback,
        timeout=timeout,
    )

    return path, result

# def test_{data}_{content type}_{status code}

def test_pdf_pdf_200(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    path, result = download(tmp_path, handlers.pdf_pdf_200.url())

    assert result == True

    with open(path, 'br') as file:
        data = file.read()
        assert data == test_util.DATA_PDF

def test_pdf_pdf_200_fallback(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    path, result = download(tmp_path, handlers.none(), handlers.pdf_pdf_200.url())
    assert result == True

    with open(path, 'br') as file:
        data = file.read()
        assert data == test_util.DATA_PDF

def test_pdf_pdf_404(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.pdf_pdf_404.url())
    assert result == False

def test_pdf_html_200(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.pdf_html_200.url())
    assert result == False

def test_pdf_html_404(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.pdf_html_404.url())
    assert result == False

def test_html_pdf_200(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.html_pdf_200.url())
    assert result == False

def test_html_pdf_404(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.html_pdf_404.url())
    assert result == False

def test_html_html_200(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.html_html_200.url())
    assert result == False

def test_html_html_404(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver)
    _, result = download(tmp_path, handlers.html_html_404.url())
    assert result == False

def test_timeout(tmp_path: Path, httpserver: HTTPServer):
    handlers = test_util.HTTPHandlers(httpserver, timeout=2.0)
    _, result = download(tmp_path, handlers.timeout(), timeout=1.0)
    assert result == False
