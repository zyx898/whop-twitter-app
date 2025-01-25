import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from whop_api import WhopAPI
from image_gen import ImageGenerator
from text_gen import TextGenerator
import twikit
import logging
import time
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(__file__), '.env')
)

class WhopGeneratorBot:
    def __init__(self):
        try:
            # Initialize Twitter API client using twikit
            self.client = twikit.Client('en-US')
            
            # Store the last processed tweet's timestamp
            self.last_processed_time = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            raise

    async def _login(self):
        """Login to Twitter"""
        try:
            # Login using email and password
            await self.client.login(
                auth_info_1='0x_LucasZ',  # username
                auth_info_2='',  # email
                password=''  # password
            )
            logger.info("Successfully logged in to Twitter")
            
        except Exception as e:
            logger.error(f"Failed to login: {str(e)}")
            raise

    async def get_latest_mention(self):
        """Get only the latest mention"""
        try:
            # Search for mentions after the last processed time
            query = f"@0x_LucasZ -is:retweet"
            
            # Use twikit's search method
            tweets = await self.client.search_tweet(
                query,
                'Latest',
                count=1  # Only get the latest tweet
            )
            
            if not tweets:
                return None
                
            # Get the latest tweet
            latest_tweet = tweets[0] if tweets else None
            
            if latest_tweet:
                # Update the last processed time
                self.last_processed_time = latest_tweet.created_at
                logger.info(f"Found new mention from: {latest_tweet.created_at}")
                
            return latest_tweet
            
        except Exception as e:
            logger.error(f"Error getting latest mention: {str(e)}")
            return None

    async def process_mention(self, tweet):
        """Process a mention and generate a Whop store"""
        if not tweet:
            return
            
        try:
            logger.info(f"Processing mention from tweet ID: {tweet.id}")
            logger.info(f"Tweet text: {tweet.text}")
            
            # Reply to the tweet
            await self.client.create_tweet(
                text="Thanks for your request! Working on generating your Whop store...",
                reply_to=tweet.id
            )
            
            # Generate store title
            text_gen = TextGenerator()
            title = text_gen.generate_title(tweet.text).replace(" ", "")
            
            # Create Whop store
            whop_api = WhopAPI(title)
            whop_api.start()

            # Reply with store link
            await self.client.create_tweet(
                text=f"Your Whop store is ready! Check it out at: https://whop.com/{title}",
                reply_to=tweet.id
            )
            
        except Exception as e:
            logger.error(f"Error processing mention: {str(e)}")

    async def start(self):
        """Start the bot and poll for mentions"""
        logger.info("Starting WhopGeneratorBot...")
        
        # Login first
        await self._login()
        
        while True:
            try:
                # Get the latest mention
                latest_mention = await self.get_latest_mention()
                
                # Process the mention if found
                if latest_mention:
                    await self.process_mention(latest_mention)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    try:
        bot = WhopGeneratorBot()
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
