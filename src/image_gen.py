from PIL import Image
import requests
import os
from dotenv import load_dotenv


class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv('DEEPAI_KEY')
        
    def generate_logo(self, prompt):
        """Generate a logo using DeepAI's text2img API and save it locally
        
        Args:
            prompt (str): Text description of the desired logo
            
        Returns:
            str: Path to the saved image file
        """
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={
                'text': prompt,
            },
            headers={'Api-Key': "8dea421e-b86f-443e-8d90-bb82b778f248"}
        )
        print(response.json())
        if response.status_code != 200:
            raise Exception("Failed to generate image")
        
            
        image_url = response.json()['output_url']
        
        # Download and save the image
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            with open('image.png', 'wb') as f:
                f.write(img_response.content)
            return 'image.png'
        else:
            raise Exception("Failed to download image")
        
#test
if __name__ == "__main__":
    load_dotenv()

    image_gen = ImageGenerator()
    image_gen.generate_logo("A logo for a store that sells AI generated images")
