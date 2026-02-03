#!/usr/bin/env python3
"""
Standalone Zoom Bot Runner
Runs independently from the main backend service
"""

import sys
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/botzoom/zoom-bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Run Zoom Bot')
    parser.add_argument('meeting_link', help='Zoom meeting link or ID')
    parser.add_argument('--bot-id', help='Bot UUID (auto-generated if not provided)')
    parser.add_argument('--bot-name', default='Meeting Transcript Bot', help='Bot display name')
    parser.add_argument('--duration', type=int, default=7200, help='Max recording duration in seconds')
    parser.add_argument('--output-dir', default='storage/zoom_recordings', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting Zoom bot for meeting: {args.meeting_link}")
        
        from integrations.zoom.bot import ZoomBot
        from integrations.zoom.bot_utils import clean_meeting_link
        
        # Clean meeting link
        cleaned_link = clean_meeting_link(args.meeting_link)
        
        # Create and run bot
        bot = ZoomBot(
            meeting_link=cleaned_link,
            bot_name=args.bot_name,
            min_record_time=args.duration,
            output_dir=args.output_dir,
            bot_id=args.bot_id  # Pass bot_id if provided
        )
        
        logger.info(f"Bot ID: {bot.id}")
        
        # Run bot (blocking)
        bot.run()
        
        logger.info("Bot session completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Bot failed: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
