import os
from typing import Optional
from dotenv import load_dotenv
from whop_api import WhopAPI
from image_gen import ImageGenerator
from text_gen import TextGenerator
import tweepy
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
            # Validate required environment variables
            required_env_vars = [
                'TWITTER_API_KEY',
                'TWITTER_API_SECRET', 
                'TWITTER_ACCESS_TOKEN',
                'TWITTER_ACCESS_TOKEN_SECRET',
                'TWITTER_BEARER_TOKEN'
            ]
            self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'), 
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            )

            # Test authentication
            me = self.client.get_me()
            logger.info(f"Twitter API v2 authentication successful. Connected as: {me.data.username}")
            
            # Store the last processed tweet's timestamp
            self.last_processed_time = datetime.now(timezone.utc)
            
        except tweepy.errors.Unauthorized as e:
            logger.error(f"Twitter API authentication failed: {str(e)}")
            logger.error("Please check your Twitter API credentials")
            raise
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            raise

    def get_latest_mention(self):
        """Get only the latest mention"""
        try:
            # Search for mentions after the last processed time
            # This query searches for tweets mentioning the bot's username (@botname) but excludes retweets
            query = f"@{self.client.get_me().data.username} -is:retweet"
            
            # Use OAuth 1.0a User Context authentication
            tweets = self.client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'author_id', 'text'],
                expansions=['author_id'],
                max_results=1,  # Only get the latest tweet
                start_time=self.last_processed_time,
                user_auth=True
            )
            
            if not tweets.data:
                return None
                
            # Get the single tweet returned
            latest_tweet = tweets.data[0] if tweets.data else None
            
            if latest_tweet:
                # Update the last processed time
                self.last_processed_time = latest_tweet.created_at
                logger.info(f"Found new mention from: {latest_tweet.created_at}")
                
            return latest_tweet
            
        except Exception as e:
            logger.error(f"Error getting latest mention: {str(e)}")
            return None

    def process_mention(self, tweet):
        """Process a mention and generate a Whop store"""
        if not tweet:
            return
            
        try:
            logger.info(f"Processing mention from tweet ID: {tweet.id}")
            logger.info(f"Tweet text: {tweet.text}")
            
            # Reply to the tweet
            self.client.create_tweet(
                text=f"Thanks for your request! Working on generating your Whop store...",
                in_reply_to_tweet_id=tweet.id,
                user_auth=True  # Use OAuth 1.0a authentication
            )
            
            text_gen = TextGenerator()
            title = text_gen.generate_title(tweet.text)
            
            self.whop_api = WhopAPI(title)
            self.whop_api.start()

            # Reply to the tweet
            self.client.create_tweet(
                text=f"Thanks for your request! Working on generating your Whop store... link: https://whop.com/{title}",
                in_reply_to_tweet_id=tweet.id,
                user_auth=True  # Use OAuth 1.0a authentication
            )
            
        except Exception as e:
            logger.error(f"Error processing mention: {str(e)}")

    def start(self):
        """Start the bot and poll for mentions"""
        logger.info("Starting WhopGeneratorBot...")
        
        while True:
            try:
                # Get the latest mention
                latest_mention = self.get_latest_mention()
                
                # Process the mention if found
                if latest_mention:
                    self.process_mention(latest_mention)
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    try:
        bot = WhopGeneratorBot()
        bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")