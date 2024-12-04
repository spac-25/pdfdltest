import pytest
import pytest_mock

import Controller

from unittest.mock import DEFAULT

def test_paths(mocker):
    mock_run = mocker.patch.object(Controller.Controller, 'run', autospec=True)

    def side_effect(controller: Controller.Controller, **kwargs):
        assert controller.url_file_name == 'a'
        assert controller.report_file_name == 'b'
        assert controller.destination == 'c'
        return DEFAULT

    mock_run.side_effect = side_effect

    Controller.main(['--url_file', 'a', '--report_file', 'b', '--destination', 'c', '--threads', '2'])

def test_threads_float(mocker, capsys):
    mock_run = mocker.patch.object(Controller.Controller, 'run', autospec=True)

    Controller.main(['--threads', '1.5'])

    assert capsys.readouterr().out == 'Thread should be an integer\n'