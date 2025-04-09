from __future__ import annotations

import time

import pyttsx3

from .. import logger
from ..preprocess import get_sentences


class Audio:
    def __init__(self,
                 rate: float = 140,
                 volume: float = 0.9,
                 voice: str | None = None,
                 pause_seconds: float = 0.1):
        """A class to configure the audio.

        Args:
            rate (float, optional): Number of words per minute. Defaults to 140.
            volume (float, optional): Volume. Defaults to 0.9.
            voice (Optional[str], optional): Voice id.
            The available voice ids can be found with `list_voices()`.
            Defaults to None.
            pause_seconds (float, optional): Duration of pause between sentences. Defaults to 0.1.
        """
        self.engine = pyttsx3.init()
        self._available_voices = None
        self.rate = rate
        self.volume = volume
        self.voice = voice
        self.pause_seconds = pause_seconds

    @property
    def available_voices(self) -> list:
        """Get the available voices.

        Returns:
            list: The available voices.
        """
        if self._available_voices is None:
            self._available_voices = self.engine.getProperty('voices')
        return self._available_voices

    @property
    def rate(self) -> float:
        """Get the speech rate (words per minutes.)

        Returns:
            float: Words per minutes.
        """
        return self._rate

    @rate.setter
    def rate(self, rate: float):
        """
        Set the speech rate (words per minute).

        Args:
            rate (float): Number of words per minute.
            Restricted to be between 50 and 500.
        """
        self._rate = max(50, min(500, rate))
        self.engine.setProperty('rate', rate)

    @property
    def volume(self) -> float:
        """Get the volume.

        Returns:
            float: Volume.
        """
        return self._volume

    @volume.setter
    def volume(self, volume: float):
        """Set the volume (0.0 to 1.0).

        Args:
            volume (float): Volume. Restricted to be between 0 and 1.
        """
        self._volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', volume)

    @property
    def voice(self) -> str:
        """Get the voice id.

        Returns:
            str: Voice id.
        """
        return self._voice

    @voice.setter
    def voice(self,
              voice: int | str | None):
        """Set the voice by index or ID.

        Args:
            voice (Union[int, str]): You can either provide the index (int) or the ID (str) of the voice.
            The list of available_voices can be retrieved from the attribute available_voices.
        """
        if isinstance(voice, int):
            if 0 <= voice < len(self.available_voices):
                self._voice = self.available_voices[voice].id
            else:
                logger.error(f'Invalid voice index = {voice}. Keeping current voice.')
                return
        elif isinstance(voice, str):
            if voice in [v.id for v in self.available_voices]:
                self._voice = voice
            else:
                logger.error(f'Invalid voice ID = {voice}. Keeping current voice.')
                return
        elif voice is None:
            self._voice = self.engine.getProperty('voice')
        else:
            logger.error(f'Unsupported datatype of voice = {type(voice)}. It must be either int or str.')
            return
        self.engine.setProperty('voice', self._voice)

    @property
    def pause_seconds(self) -> float:
        """The duration of pause between sentences.

        Returns:
            float: Duration of pause between sentences in second.
        """
        return self._pause_seconds

    @pause_seconds.setter
    def pause_seconds(self, value: float):
        """Set the duration of pause between sentences.

        Args:
            value (float): Duration of pause between sentences.
        """
        if value < 0:
            logger.error(f'pause = {value} must be non-negative. Keeping the current pause.')
            return
        self._pause_seconds = value

    def list_voices(self):
        """Print available voices with their index and details."""
        for i, voice in enumerate(self.available_voices):
            logger.info(f"Index {i}: {voice.name} (ID: {voice.id})")

    def clean_text(self, text: str) -> str:
        """Clean the text for smoother reading.

        '\n' is replaced with a white space.

        Args:
            text (str): Text.

        Returns:
            str: Cleaned text.
        """
        return " ".join(text.split()).replace('\n', ' ').strip()

    def read_article(self,
                     article: str):
        """Read the article aloud, splitting it into sentences.

        Args:
            article (str): Article.
        """
        if not isinstance(article, str):
            logger.warning(f'article = {article} is not str. Skipping.')
            return
        cleaned_text = self.clean_text(article)
        sentences = get_sentences(cleaned_text)
        for sentence in sentences:
            self.engine.say(sentence)
            self.engine.runAndWait()
            time.sleep(self.pause_seconds)

    @property
    def settings(self) -> dict:
        """Get the settings.

        Returns:
            dict: Settings.
        """
        return {
            'rate': self.rate,
            'volume': self.volume,
            'voice': self.voice,
            'pause_seconds': self.pause_seconds,
        }

    @settings.setter
    def settings(self, values: dict):
        for key in ['rate', 'volume', 'voice', 'pause_seconds']:
            if key in values:
                setattr(self, key, values[key])

    def stop(self):
        """Stop the current speech."""
        self.engine.stop()
