from __future__ import annotations

import json
import os
import signal
import sys
import time

import configargparse
from platformdirs import user_config_dir

from ..audio import Audio
from ..resources import Paper
from ..utils import logger


def handle_exit(signum:int , frame: object): #
    """Handle the exit.

    Args:
        signum (int): Signal number.
        frame (object): A frame object.
    """
    logger.info("\nReceived signal %s. Exiting cleanly.", signum)
    sys.exit(0)


def save_settings(config_path: str, settings: dict):
    """Save the settings to file.

    Args:
        config_path (str): Path to the configuration file.
        settings (dict): Dictionary of the settings.
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logger.error('Error saving settings: %s', e)


def main():
    """Main function.
    """
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    parser = configargparse.ArgParser()
    parser.add_argument('--id', help='arXiv paper ID.')
    parser.add_argument('--output', type=str, help='Output to audio file if provided.')
    parser.add_argument('--rate', type=float, help='Number of words per minute between 50 and 500.')
    parser.add_argument('--volume', type=float, help='Volume between 0 and 1.')
    parser.add_argument('--voice', type=str, help='Voice.')
    parser.add_argument('--pause-seconds', type=float, help='Duration of pause between sentences in second.')
    parser.add_argument('--page-size', type=int, help='Maximum number of results fetched in a single API request.')
    parser.add_argument('--delay-seconds', type=float, help='Number of seconds to wait between API requests.')
    parser.add_argument('--num-retries', type=int, help='Number of times to retry a failing API request before raising an Exception.')
    parser.add_argument('--list-voices', action='store_true', help='List the available voices.')

    args = parser.parse_args()

    config_dir = user_config_dir('audioarxiv')
    os.makedirs(config_dir, exist_ok=True)
    config_file = 'config.json'
    config_path = os.path.join(config_dir, config_file)
    # Default settings.
    settings = {
        'audio': {
            'rate': 140,
            'volume': 0.9,
            'voice': None,
            'pause_seconds': 0.1
        },
        'paper': {
            'page_size': 100,
            'delay_seconds': 3.0,
            'num_retries': 3
        }
    }

    audio = Audio(**settings['audio'])

    if args.list_voices:
        audio.list_voices()
        return

    # Update the settings.
    # There may be some internal rules in the Audio class setting limits.
    settings['audio'].update(audio.settings)

    if os.path.exists(config_path):
        # Load the settings from the config file.
        try:
            with open(config_path) as f:
                loaded_settings = json.load(f)
                settings.update(loaded_settings)
                audio.settings = settings['audio']
        except Exception as e:
            logger.error('Error loading settings: %s. Using defaults.', e)
    else:
        logger.info(f'Saving default settings to {config_path}...')
        save_settings(config_path, settings)

    # Check audio properties
    audio_properties = list(settings['audio'].keys())
    audio_settings_changed = False
    for prop in audio_properties:
        value = getattr(args, prop)
        if value is not None:
            # Compare with the existing setting
            if value != settings['audio'][prop]:
                setattr(audio, prop, value)
                audio_settings_changed = True
    if audio_settings_changed:
        settings['audio'].update(audio.settings)

    # Load the paper.
    paper = Paper(**settings['paper'])
    paper_properties = list(settings['paper'].keys())
    paper_settings_changed = False
    for prop in paper_properties:
        value = getattr(args, prop)
        if value is not None:
            # Compare with the existing setting
            if value != settings['paper'][prop]:
                setattr(paper, prop, value)
                paper_settings_changed = True
    if paper_settings_changed:
        settings['paper'].update(paper.settings)

    # Write the settings to file if there are changes.
    if audio_settings_changed or paper_settings_changed:
        logger.info('Saving updated settings to %s...', config_path)
        save_settings(config_path=config_path, settings=settings)

    # Search the paper.
    if args.id is not None:
        # Print the information
        logger.info(f'Configuration file: {config_path}')
        logger.info('Audio settings')
        for key, value in settings['audio'].items():
            logger.info('%s: %s', key, value)

        logger.info('Paper settings')
        for key, value in settings['paper'].items():
            logger.info('%s: %s', key, value)

        logger.info('Searching arxiv: %s...', args.id)
        paper.search_by_arxiv_id(arxiv_id=args.id)
        # Get the sections
        sections = paper.sections
        for section in sections:
            audio.read_article(section['header'])
            time.sleep(1)
            for content in section['content']:
                audio.read_article(content)
                time.sleep(1)
