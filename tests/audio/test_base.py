from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import pyttsx3

from audioarxiv.audio.base import Audio, validate_audio_arguments


# Mock pyttsx3.init to avoid actual engine initialization during testing
@pytest.fixture
def mock_pyttsx3_init(monkeypatch):
    mock_engine = MagicMock()
    monkeypatch.setattr(pyttsx3, "init", lambda: mock_engine)
    return mock_engine


def test_validate_audio_arguments_valid(mock_pyttsx3_init):
    # Mocking valid parameters
    mock_engine = mock_pyttsx3_init()  # noqa: F841
    result = validate_audio_arguments(150, 0.8, "voice_id", 0.5)
    assert result['rate'] == 150
    assert result['volume'] == 0.8
    assert result['voice'] is None
    assert result['pause_seconds'] == 0.5


def test_validate_audio_arguments_invalid_voice_index(mock_pyttsx3_init):
    mock_engine = mock_pyttsx3_init()  # noqa: F841
    result = validate_audio_arguments(150, 0.8, 99, 0.5)  # Invalid voice index  # noqa: F841
    assert result['voice'] is None  # Voice should be set to None for invalid index


def test_validate_audio_arguments_invalid_voice_id(mock_pyttsx3_init):
    mock_engine = mock_pyttsx3_init()  # noqa: F841
    result = validate_audio_arguments(150, 0.8, "invalid_voice_id", 0.5)  # Invalid voice ID
    assert result['voice'] is None  # Voice should be set to None for invalid voice ID


def test_validate_audio_arguments_invalid_voice_type(mock_pyttsx3_init):
    mock_engine = mock_pyttsx3_init()  # noqa: F841
    result = validate_audio_arguments(150, 0.8, 12345, 0.5)  # Invalid voice type
    assert result['voice'] is None  # Voice should be set to None for invalid type


def test_validate_audio_arguments_invalid_pause_seconds(mock_pyttsx3_init):
    mock_engine = mock_pyttsx3_init()  # noqa: F841
    result = validate_audio_arguments(150, 0.8, "voice_id", -1)  # Invalid pause seconds (negative)
    assert result['pause_seconds'] == 0.1  # Pause seconds should be set to the default value 0.1


@pytest.fixture
def audio_instance(mock_pyttsx3_init):
    mock_engine = mock_pyttsx3_init()  # noqa: F841
    return Audio(rate=150, volume=0.8, voice="voice_id", pause_seconds=0.5, validate_arguments=True)


def test_audio_initialization(audio_instance):
    assert audio_instance.engine is not None  # Ensure engine is initialized
    assert audio_instance.pause_seconds == 0.5  # Check if pause_seconds is set correctly


@patch('audioarxiv.audio.base.time.sleep')  # prevent actual sleeping
@patch('audioarxiv.audio.base.get_sentences')  # control sentence splitting
@patch('audioarxiv.audio.base.pyttsx3.init')  # control TTS engine
def test_read_article(mock_init, mock_get_sentences, mock_sleep):
    # Create a mock engine with say() and runAndWait()
    mock_engine = MagicMock()
    mock_init.return_value = mock_engine

    # Mock get_sentences to return predictable output
    mock_get_sentences.return_value = ['Sentence 1', 'Sentence 2']

    # Create Audio instance and run test
    audio = Audio()
    audio.read_article("Some article.")

    # Verify say() was called with the expected sentence
    mock_engine.say.assert_any_call('Sentence 1')
    mock_engine.say.assert_any_call('Sentence 2')
    assert mock_engine.runAndWait.call_count == 2
    assert mock_sleep.call_count == 2


def test_save_article(audio_instance, monkeypatch):
    # Mocking pyttsx3 save_to_file method
    mock_save = MagicMock()
    monkeypatch.setattr(audio_instance.engine, "save_to_file", mock_save)

    article = "This is an article."
    filename = "test_audio.mp3"
    audio_instance.save_article(filename, article)

    # Ensure the save_to_file method was called once with the cleaned text and filename
    mock_save.assert_called_once_with("This is an article.", filename)


def test_pause_seconds_setter(audio_instance):
    audio_instance.pause_seconds = 1.0  # Setting a valid value
    assert audio_instance.pause_seconds == 1.0  # Check if the setter works correctly

    audio_instance.pause_seconds = -1.0  # Setting an invalid value (negative)
    assert audio_instance.pause_seconds == 1.0  # The value should remain 1.0


@patch('audioarxiv.audio.base.logger')
@patch('audioarxiv.audio.base.pyttsx3.init')
def test_list_voices(mock_init, mock_logger):
    mock_engine = MagicMock()
    mock_voice = MagicMock()
    mock_voice.name = "Voice 1"
    mock_voice.id = "voice1"
    mock_engine.getProperty.return_value = [mock_voice]
    mock_init.return_value = mock_engine

    audio = Audio()
    audio.list_voices()

    mock_logger.info.assert_any_call("Index %s: %s (ID: %s)", 0, "Voice 1", "voice1")
