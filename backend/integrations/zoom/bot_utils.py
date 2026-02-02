"""
Zoom Bot utilities for meeting integration.
Extracted from cuemeet-zoom-bot.
"""

import tarfile
import logging
import re
import os
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timezone


def extract_zoom_details(url):
    """
    Extract meeting ID and password from Zoom URL.
    
    Args:
        url: Zoom meeting URL
        
    Returns:
        tuple: (meeting_id, passcode)
    """
    # Regular expression to find the meeting ID and password in the URL
    # Supports /j/, /wc/join/, and /s/ formats
    meeting_id_pattern = r'/(?:j|wc/join|s)/(\d+)'
    passcode_pattern = r'[?&]pwd=([\w.]+)'

    # Search for meeting ID and passcode
    meeting_id_match = re.search(meeting_id_pattern, url)
    passcode_match = re.search(passcode_pattern, url)

    # Extract meeting ID and passcode if found
    meeting_id = meeting_id_match.group(1) if meeting_id_match else None
    passcode = passcode_match.group(1) if passcode_match else None

    return meeting_id, passcode


def clean_meeting_link(link: str) -> str:
    """Clean and normalize meeting link."""
    parsed = urlparse(link)
    cleaned_link = urlunparse(parsed)
    return cleaned_link


def convert_timestamp_to_utc(js_timestamp):
    """Convert JavaScript timestamp to UTC datetime."""
    return datetime.fromtimestamp(js_timestamp / 1000, tz=timezone.utc)


def create_tar_archive(json_file, opus_file, output_file):
    """
    Create tar archive of transcript and audio files.
    
    Args:
        json_file: Path to JSON transcript
        opus_file: Path to audio file
        output_file: Output tar filename (without extension)
        
    Returns:
        str: Path to created tar file or None on error
    """
    try:
        full_path = os.path.join(os.getcwd(), f'{output_file}.tar')

        with tarfile.open(full_path, 'w') as tar:
            if os.path.exists(json_file):
                tar.add(json_file, arcname=os.path.basename(json_file))
            else:
                logging.warning(f"File not found: {json_file} - Skipping it.")

            if os.path.exists(opus_file):
                tar.add(opus_file, arcname=os.path.basename(opus_file))
            else:
                logging.warning(f"File not found: {opus_file} - Skipping it.")
                
        logging.info(f"Files successfully archived into {full_path}")
        return full_path
        
    except PermissionError as e:
        logging.error(f"Permission denied: {e.filename}")
    except tarfile.TarError as e:
        logging.error(f"Error creating tar archive: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
    return None


def audio_file_path(audio_file):
    """Get full path to audio file."""
    return os.path.join(os.getcwd(), audio_file)


def manage_cookies(username):
    """
    Session cookies for automatic joining process - Zoom Web.
    
    Args:
        username: Bot display name in meeting
        
    Returns:
        list: Cookie dictionaries for Selenium
    """
    cookies = [
        {
            "domain": ".zoom.us",
            "hostOnly": False,
            "httpOnly": False,
            "name": "_zm_lang",
            "path": "/",
            "secure": True,
            "session": False,
            "storeId": "1",
            "value": "en-US",
            "id": 1
        },
        {
            "domain": ".zoom.us",
            "hostOnly": False,
            "httpOnly": True,
            "name": "_zm_wc_remembered_name",
            "path": "/",
            "secure": True,
            "session": False,
            "storeId": "1",
            "value": username,
            "id": 2
        },
        {
            "domain": ".zoom.us",
            "hostOnly": False,
            "httpOnly": False,
            "name": "OptanonAlertBoxClosed",
            "path": "/",
            "secure": False,
            "session": False,
            "storeId": "1",
            "value": "2021-12-09",
            "id": 3
        },
        {
            "domain": ".zoom.us",
            "hostOnly": False,
            "httpOnly": False,
            "name": "OptanonConsent",
            "path": "/",
            "secure": False,
            "session": False,
            "storeId": "1",
            "value": "isGpcEnabled=1&datestamp=0&version=6.21.0&isIABGlobal=false&hosts=&consentId=0&interactionCount=1&landingPath=NotLandingPage&groups=0&geolocation=0&AwaitingReconsent=false",
            "id": 4
        }
    ]

    return cookies
