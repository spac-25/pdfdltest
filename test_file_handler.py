import pytest
from pytest_httpserver import HTTPServer

import test_util
import Polar_File_Handler

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import polars as pl

@dataclass
class SourceRow:
    id: str
    url: Optional[str]
    url_alt: Optional[str]
    valid: bool

    def sub_path(self) -> Optional[str]:
        sub_path = self.url
        if not sub_path:
            sub_path = self.url_alt

        return sub_path

    def expects(self) -> bool:
        True if self.sub_path() else False

    def expect_request(self, httpserver: HTTPServer) -> bool:
        sub_path = self.sub_path()
        if not sub_path:
            return False

        if self.valid:
            httpserver.expect_request(sub_path).respond_with_data(test_util.DATA_PDF, content_type=test_util.CONTENT_TYPE_PDF, status=200)
        else:
            httpserver.expect_request(sub_path).respond_with_data(test_util.DATA_HTML, content_type=test_util.CONTENT_TYPE_HTML, status=404)

        return True

SOURCES = [
    SourceRow(
        f'BR{i}',
        f'/{i}' if i % 5 != 0 else None,
        f'/{i}' if i % 2 != 0 else None,
        i % 3 != 0
    )
    for i in range(50)
]

def create_source_file(dir: Path, httpserver: HTTPServer, data: List[SourceRow]):
    columns = {'BRnum': [], 'Pdf_URL': [], 'Report Html Address': []}
    for row in data:
        columns['BRnum'].append(row.id)
        columns['Pdf_URL'].append(httpserver.url_for(row.url) if row.url else '')
        columns['Report Html Address'].append(row.url_alt if row.url_alt else '')

    df = pl.from_dict(columns)
    df.write_excel(dir.joinpath('source.xlsx'))

    return data

def download(dir: Path):
    Polar_File_Handler.FileHandler().start_download(dir.joinpath('source.xlsx'), dir.joinpath('metadata.xlsx'), dir.joinpath('files'))

def test_no_source(tmp_path: Path, httpserver: HTTPServer):
    with pytest.raises(FileNotFoundError):
        download(tmp_path)

def test_no_metadata(tmp_path: Path, httpserver: HTTPServer):
    create_source_file(tmp_path, httpserver, [])

    download(tmp_path)

def test_no_files(tmp_path: Path, httpserver: HTTPServer):
    create_source_file(tmp_path, httpserver, [])

    download(tmp_path)

def test_cold_download(tmp_path: Path, httpserver: HTTPServer):
    create_source_file(tmp_path, httpserver, SOURCES)

    for source in SOURCES:
        source.expect_request(httpserver)

    download(tmp_path)

def test_cold_files(tmp_path: Path, httpserver: HTTPServer):
    create_source_file(tmp_path, httpserver, SOURCES)

    for source in SOURCES:
        source.expect_request(httpserver)

    download(tmp_path)