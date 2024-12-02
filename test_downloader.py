import pytest
from pytest_httpserver import HTTPServer

import test_util
import Downloader

import time
from pathlib import Path

def download(dir: Path, httpserver: HTTPServer, data: bytes, content_type: str, status: int, fallback=False) -> Path:
    URL_FIRST = '/first'
    URL_LAST = '/last'

    if fallback:
        httpserver.expect_ordered_request(URL_FIRST).respond_with_data(test_util.DATA_HTML, content_type=test_util.CONTENT_TYPE_HTML, status=404)
        httpserver.expect_ordered_request(URL_LAST).respond_with_data(data, content_type=content_type, status=status)
    else:
        httpserver.expect_ordered_request(URL_FIRST).respond_with_data(data, content_type=content_type, status=status)

    path = dir.joinpath(f'test.pdf')
    return \
        path, \
        Downloader.Downloader().download(
            url=httpserver.url_for(URL_FIRST),
            destination_path=path,
            alt_url=httpserver.url_for(URL_LAST) if fallback else None,
            timeout=1,
        ),

# def test_{data}_{content type}_{status code}

def test_pdf_pdf_200(request, tmp_path: Path, httpserver: HTTPServer):
    path, result = download(tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_PDF, 200)
    assert result == True

    with open(path, 'br') as file:
        data = file.read()
        assert data == test_util.DATA_PDF

def test_pdf_pdf_200_fallback(request, tmp_path: Path, httpserver: HTTPServer):
    path, result = download(tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_PDF, 200, True)
    assert result == True

    with open(path, 'br') as file:
        data = file.read()
        assert data == test_util.DATA_PDF

def test_pdf_pdf_404(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_PDF, 404)
    assert result == False

def test_pdf_html_200(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_HTML, 200)
    assert result == False

def test_pdf_html_404(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_HTML, 404)
    assert result == False

def test_html_pdf_200(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_PDF, 200)
    assert result == False

def test_html_pdf_404(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_PDF, 404)
    assert result == False

def test_html_html_200(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_HTML, 200)
    assert result == False

def test_html_html_404(tmp_path: Path, httpserver: HTTPServer):
    _, result = download(tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_HTML, 404)
    assert result == False

def test_timeout(tmp_path: Path, httpserver: HTTPServer):
    httpserver.expect_request("").respond_with_handler(lambda _: time.sleep(2))
    assert Downloader.Downloader().download(httpserver.url_for(''), tmp_path.joinpath('test.pdf'), timeout=1) == False
