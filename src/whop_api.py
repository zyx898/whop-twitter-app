import json
import time
from curl_cffi import requests
import os
from dotenv import load_dotenv

from image_gen import ImageGenerator
from text_gen import TextGenerator
import io
load_dotenv()

class WhopAPI:
    def __init__(self,title):
        self.title = title

    def parse_x_component(self,content):
        data = {}
        for line in content.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return data

        
    def create_store(self):
        headers = {}
        cookies = {}
        url = "https://whop.com/new/"
        data = [{"title":f"{self.title}","headline":"$undefined","participatingInCustomCreatorMilestones":True}]
        response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(data), impersonate="chrome")
        responseJson = json.loads(self.parse_x_component(response.text)['1'])
        print(responseJson)
        print(response.status_code)
        return responseJson

    
    
    def add_chat_app(self, storeJson):
        headers = {}
        cookies = {}
        url = f"https://whop.com/{self.title}/"
        data = [{"companyId":f"{storeJson['data']['company_id']}","accessPassId":f"{storeJson['data']['access_pass_id']}","productRoute":f"{self.title}","appId":f"app_xml5hbizmZPgUT","name":"Chat"}]
        response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(data), impersonate="chrome")

        print(response.text)
        print(response)

    def pre_fetch_image(self):
        headers = {}
        cookies = {}
        url = "https://whop.com/api/graphql/fetchPresignedUploadUrl/"
        data = {
            "query": "\n    mutation fetchPresignedUploadUrl($input: PresignedUploadInput!) {\n  presignedUpload(input: $input)\n}\n    ",
            "variables": {
                "input": {
                    "fileExtV2": "jpeg",
                    "isPublic": True
                }
            },
            "operationName": "fetchPresignedUploadUrl"
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        responseJson = json.loads(response.text)
        return responseJson['data']['presignedUpload']
    
    def upload_image(self, image_url, image_path):
        headers = {}

        

        with open(image_path, 'rb') as f:
            image_bytes = io.BytesIO(f.read())
        
        # Upload bytes directly
        response = requests.put(image_url, headers=headers, data=image_bytes.getvalue())
        if response.status_code != 200:
            raise Exception(f"Failed to upload image. Status code: {response.status_code}")

    def upload_image_from_url(self, image_url,storeJson):
        headers = {}
        cookies = {}
        url = f"https://whop.com/{self.title}/"
        data = [
        {
            "companyId":storeJson['data']['company_id'],
            "pass":{
            "id":storeJson['data']['access_pass_id'],
            "title":"$undefined",
            "headline":"$undefined",
            "shortenedDescription":"$undefined",
            "creatorPitch":"$undefined",
            "visibility":"$undefined",
            "globalAffiliateStatus":"$undefined",
            "globalAffiliatePercentage":"$undefined",
            "redirectPurchaseUrl":"$undefined",
            "route":"$undefined"
            },
            "images":[
            image_url.split("?")[0]
            ],
            "affiliateAssets":"$undefined",
            "productRoute":self.title,
            "category":"$undefined",
            "subcategory":"$undefined",
            "pathname":f"/{self.title}/",
            "upsells":"$undefined",
            "popupPromo":{
            "enabled":False,
            "discountPercentage":"$undefined"
            }
        }]

        response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(data))

        print(response.text)
        print(response.status_code)


    def start(self):
        
        storeJson = self.create_store()
        # #create chat app
        self.add_chat_app(storeJson)
        # #upload image
        # storeJson = {'data': {'success': 'true', 'worker': 'CompanyManager::CreateCompanyWorker', 'company_id': 'biz_f86kfUlgyQa7XJ', 'access_pass_id': 'prod_XReFtq1uUE7dw', 'jid': '47255f087dbe161ed25ff43e', 'status': 'complete', 'update_time': '1737775602', 'company_hub_route': '', 'access_pass_route': 'pixel-perfect-ai-creations'}, 'error': '$undefined', 'status': 'ok'}
        self.presigned_upload_url = self.pre_fetch_image()
        image_gen = ImageGenerator()
        image_path = image_gen.generate_logo(f"A logo for a store that {self.title}")
        time.sleep(3)
        self.upload_image(self.presigned_upload_url,image_path)
        #upload image from url
        self.upload_image_from_url(self.presigned_upload_url,storeJson)


# if __name__ == "__main__":
    # text_gen = TextGenerator()
    # title = text_gen.generate_title("I want to sell AI generated images")
    # whop_api = WhopAPI("pixel-perfect-ai-creations")
    # whop_api.start()