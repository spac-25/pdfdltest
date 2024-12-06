import pytest
from pytest_httpserver import HTTPServer

import test_util
import Polar_File_Handler

from dataclasses import dataclass
from typing import Optional, List
import time
from pathlib import Path
import polars as pl

PATH_SOURCE = 'source.xlsx'
PATH_METADATA = 'metadata.xlsx'
PATH_FILES = 'files'
FILE_SUFFIX = '.pdf'
COLUMN_ID = 'BRnum'
COLUMN_RESULT = 'pdf_downloaded'
RESULT_SUCCESS = 'yes'
RESULT_FAILURE = 'no'

@dataclass
class Source:
    id: str
    url: Optional[test_util.HTTPHandler]
    fallback: Optional[test_util.HTTPHandler]

    def is_valid(self) -> bool:
        return (self.url and self.url.enabled) or (self.fallback and self.fallback.enabled)

# creates ids and sparse urls with sparser disabled fallback urls
def create_sources(server: HTTPServer, count=15) -> List[Source]:
    return [
        Source(
            f'BR{i+1}',
            test_util.HTTPHandler(server, f'{i+1}').enable() if i % 3 != 0 else None,
            test_util.HTTPHandler(server, f'{i+1}_alt') if i % 2 != 0 else None,
        )
        for i in range(count)
    ]

# writes source file that ids and potential urls
def create_source_file(dir: Path, data: List[Source]):
    columns = {'BRnum': [], 'Pdf_URL': [], 'Report Html Address': []}
    for row in data:
        columns['BRnum'].append(row.id)
        columns['Pdf_URL'].append(row.url.url() if row.url else '')
        columns['Report Html Address'].append(row.fallback.url() if row.fallback else '')

    df = pl.from_dict(columns)
    df.write_excel(dir.joinpath(PATH_SOURCE))

    return data

# starts the file handler
def download(dir: Path):
    Polar_File_Handler.FileHandler().start_download(dir.joinpath(PATH_SOURCE), dir.joinpath(PATH_METADATA), dir.joinpath(PATH_FILES))

# test if file handler raises an exception when there is no source file
def test_no_source(tmp_path: Path, httpserver: HTTPServer):
    with pytest.raises(FileNotFoundError):
        download(tmp_path)

# test that file handler creates the metadata file
def test_no_metadata(tmp_path: Path, httpserver: HTTPServer):
    create_source_file(tmp_path, [])

    download(tmp_path)

    assert tmp_path.joinpath(PATH_METADATA).exists()

# test that file handler runs without any sources
def test_no_files(tmp_path: Path, httpserver: HTTPServer):
    create_source_file(tmp_path, [])

    download(tmp_path)

# test that the file handler runs with sources
def test_cold_download(tmp_path: Path, httpserver: HTTPServer):
    sources = create_sources(httpserver)
    create_source_file(tmp_path, sources)

    download(tmp_path)

# test that the enabled sources have been downloaded
def test_cold_files(tmp_path: Path, httpserver: HTTPServer):
    sources = create_sources(httpserver)
    create_source_file(tmp_path, sources)

    download(tmp_path)

    for source in sources:
        if source.is_valid():
            assert tmp_path.joinpath(PATH_FILES, f'{source.id}{FILE_SUFFIX}').exists()

# test that the download results have been noted correctly in the metadata file
def test_cold_metadata(tmp_path: Path, httpserver: HTTPServer):
    sources = create_sources(httpserver)
    create_source_file(tmp_path, sources)

    download(tmp_path)

    metadata = pl.read_excel(tmp_path.joinpath(PATH_METADATA), columns=[COLUMN_ID, COLUMN_RESULT])

    for source in sources:
        rows = metadata.filter(pl.col(COLUMN_ID) == source.id)
        assert not rows.is_empty()

        assert len(rows) == 1

        result_expected = RESULT_SUCCESS if source.is_valid() else RESULT_FAILURE
        assert rows[0, COLUMN_RESULT] == result_expected

# test that rerunning after enabling the alternative urls downloads (only) the newly valid urls
def test_continued_files(tmp_path: Path, httpserver: HTTPServer):
    sources = create_sources(httpserver)
    create_source_file(tmp_path, sources)

    download(tmp_path)

    time.sleep(0.01)
    timestamp = time.time_ns()
    time.sleep(0.01)

    enabled = []
    for source in sources:
        if not source.is_valid() and source.fallback:
            source.fallback.enable()
            enabled.append(source)

    download(tmp_path)

    tmp_path.joinpath(PATH_FILES, f'{source.id}{FILE_SUFFIX}').stat().st_ctime_ns

    for source in sources:
        if source.is_valid():
            path = tmp_path.joinpath(PATH_FILES, f'{source.id}{FILE_SUFFIX}')

            assert path.exists()

            mtime = path.stat().st_mtime_ns
            if source in enabled:
                assert mtime > timestamp
            else:
                assert mtime < timestamp

# test that rerunning after enabling the alternative urls updates the metadata correctly
def test_continued_metadata(tmp_path: Path, httpserver: HTTPServer):
    sources = create_sources(httpserver)
    create_source_file(tmp_path, sources)

    download(tmp_path)

    enabled = []
    for source in sources:
        if not source.is_valid() and source.fallback:
            source.fallback.enable()
            enabled.append(source)

    download(tmp_path)

    metadata = pl.read_excel(tmp_path.joinpath(PATH_METADATA), columns=[COLUMN_ID, COLUMN_RESULT])

    for source in enabled:
        rows = metadata.filter(pl.col(COLUMN_ID) == source.id)
        assert not rows.is_empty()

        assert len(rows) == 1

        result_expected = RESULT_SUCCESS
        assert rows[0, COLUMN_RESULT] == result_expected