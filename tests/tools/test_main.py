from __future__ import annotations

import os
import signal
import tempfile
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from audioarxiv.tools.main import (handle_exit, initialize_configuration, main,
                                   save_settings)


# Patch where classes/functions are used, not defined
@pytest.mark.integration
@patch("audioarxiv.tools.main.Audio")
@patch("audioarxiv.tools.main.Paper")
@patch("audioarxiv.tools.main.configargparse.ArgParser.parse_args")
def test_main_with_id_and_output(mock_parse_args, mock_Paper, mock_Audio):
    mock_args = MagicMock()
    mock_args.id = "1234.5678"
    mock_args.output = "output.mp3"
    mock_args.list_voices = False
    mock_args.rate = None
    mock_args.volume = None
    mock_args.voice = None
    mock_args.pause_seconds = None
    mock_args.page_size = None
    mock_args.delay_seconds = None
    mock_args.num_retries = None
    mock_parse_args.return_value = mock_args

    mock_audio = mock_Audio.return_value
    mock_paper = mock_Paper.return_value
    mock_paper.sections = [
        {'header': "Introduction", 'content': ["This is content."]},
        {'header': None, 'content': ["More content."]}
    ]

    with patch("audioarxiv.tools.main.initialize_configuration") as mock_init_config:
        mock_init_config.return_value = ({"audio": {}, "paper": {}}, "mock/config/path")

        main()

    mock_audio.save_article.assert_called_once()
    assert mock_audio.save_article.call_args[1]["filename"] == "output.mp3"


@pytest.mark.integration
@patch("audioarxiv.tools.main.Audio")
@patch("audioarxiv.tools.main.configargparse.ArgParser.parse_args")
def test_main_list_voices(mock_parse_args, mock_Audio):
    mock_args = MagicMock()
    mock_args.list_voices = True
    mock_parse_args.return_value = mock_args

    mock_audio = mock_Audio.return_value

    main()

    mock_audio.list_voices.assert_called_once()


@pytest.mark.integration
@patch("audioarxiv.tools.main.validate_audio_arguments")
@patch("audioarxiv.tools.main.validate_paper_arguments")
def test_initialize_configuration_defaults(mock_validate_paper, mock_validate_audio):
    mock_validate_audio.return_value = {'rate': 140, 'volume': 0.9, 'voice': None, 'pause_seconds': 0.1}
    mock_validate_paper.return_value = {'page_size': 100, 'delay_seconds': 3.0, 'num_retries': 3}

    dummy_args = MagicMock()
    for attr in ['rate', 'volume', 'voice', 'pause_seconds', 'page_size', 'delay_seconds', 'num_retries']:
        setattr(dummy_args, attr, None)

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        config_path = os.path.join(tmp_dir_name, 'config.json')  # noqa: F841 # pylint: disable=unused-variable

        with patch("audioarxiv.tools.main.user_config_dir", return_value=tmp_dir_name):
            settings, path = initialize_configuration(dummy_args)
            assert settings['audio']['rate'] == 140
            assert os.path.exists(path)


@pytest.mark.integration
@patch("builtins.open", new_callable=mock.mock_open)
def test_save_settings(mock_open_func):
    settings = {"audio": {"rate": 150}, "paper": {"page_size": 50}}
    save_settings("config.json", settings)
    mock_open_func.assert_called_once_with("config.json", 'w', encoding='utf-8')
    handle = mock_open_func()
    handle.write.assert_called()


@pytest.mark.integration
@patch("audioarxiv.tools.main.sys.exit")
def test_handle_exit(mock_exit):
    with patch("audioarxiv.tools.main.logger.info") as mock_logger:
        handle_exit(signal.SIGINT, None)
        mock_logger.assert_called_once()
        mock_exit.assert_called_once_with(0)
