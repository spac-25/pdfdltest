import pytest
from pytest_httpserver import HTTPServer

import test_util
import Downloader

import time
from pathlib import Path

def download(name: str, dir: Path, httpserver: HTTPServer, data: bytes, content_type: str, status: int, fallback=False) -> Path:
    URL_FIRST = '/first'
    URL_LAST = '/last'

    if fallback:
        httpserver.expect_ordered_request(URL_FIRST).respond_with_data(test_util.DATA_HTML, content_type=test_util.CONTENT_TYPE_HTML, status=404)
        httpserver.expect_ordered_request(URL_LAST).respond_with_data(data, content_type=content_type, status=status)
    else:
        httpserver.expect_ordered_request(URL_FIRST).respond_with_data(data, content_type=content_type, status=status)

    path = dir.joinpath(f'{name}.pdf')
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
    path, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_PDF, 200)
    assert result == True

    with open(path, 'br') as file:
        data = file.read()
        assert data == test_util.DATA_PDF

def test_pdf_pdf_200_fallback(request, tmp_path: Path, httpserver: HTTPServer):
    path, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_PDF, 200)
    assert result == True

    with open(path, 'br') as file:
        data = file.read()
        assert data == test_util.DATA_PDF

def test_pdf_pdf_404(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_PDF, 404)
    assert result == False

def test_pdf_html_200(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_HTML, 200)
    assert result == False

def test_pdf_html_404(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_PDF, test_util.CONTENT_TYPE_HTML, 404)
    assert result == False

def test_html_pdf_200(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_PDF, 200)
    assert result == False

def test_html_pdf_404(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_PDF, 404)
    assert result == False

def test_html_html_200(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_HTML, 200)
    assert result == False

def test_html_html_404(request, tmp_path: Path, httpserver: HTTPServer):
    _, result = download(request.node.name, tmp_path, httpserver, test_util.DATA_HTML, test_util.CONTENT_TYPE_HTML, 404)
    assert result == False

def test_timeout(request, tmp_path: Path, httpserver: HTTPServer):
    httpserver.expect_request("").respond_with_handler(lambda _: time.sleep(2))
    assert Downloader.Downloader().download(httpserver.url_for(''), f'{request.node.name}.pdf') == False
