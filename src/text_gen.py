import openai
import os
from dotenv import load_dotenv

load_dotenv()

class TextGenerator:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = os.getenv('OPENAI_API_KEY')
        
    def generate_title(self, tweet_text):
        """Generate a store title from tweet text
        
        Args:
            tweet_text (str): The text content of the tweet
            
        Returns:
            str: Generated store title
        """
        response = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates catchy store titles."},
                {"role": "user", "content": f"Generate a short, catchy store title based on this tweet: {tweet_text}"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip().replace("\"", "")
        
# if __name__ == "__main__":
#     text_gen = TextGenerator()
#     print(text_gen.generate_title("I want to sell AI generated images"))