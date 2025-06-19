import csv
import logging
import requests
from requests.exceptions import HTTPError
import json

logging.basicConfig(filename='crawl_tiki.log',filemode='a',format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def read_file_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.readlines()
            logging.info(f"Read file successfully: {file_path}, line number: {len(data)}")
            return [line.strip() for line in data]
    except Exception as e:
        logging.error(f"Error read file {file_path}: {e}")
        return []

def write_file_csv(file_path, data):
    try: 
        with open(file_path,'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow    (data)
    except Exception as e:
        logging.error(f"Error write file {file_path}: {e}")
        return []

def get_product_from_tiki(product_id: str):
    URL = f"https://api.tiki.vn/product-detail/api/v1/products/{product_id}"
    payload = {}
    headers = {
    "User-Agent": "PostmanRuntime/7.44.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}
    try:
        response = requests.request("GET", URL, headers=headers, data=payload)
        response.raise_for_status() 
        logging.info("Message sent successfully")
        logging.info(response)
        return response.json()
    except HTTPError as exception:
        logging.error(f"HTTP Error: {exception.response.status_code}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error send message: {e}")
        return []

def main():
    data_tiki = read_file_csv('products.csv')

    for data in data_tiki:
        try:
            product_info = get_product_from_tiki(data)
            print(data)
            if product_info:
                id = product_info.get('id','N/A')
                name = product_info.get('name','N/A')
                url_key = product_info.get('url_key','N/A')
                description = product_info.get('description','N/A')
                images_url = product_info.get('images','N/A')
                info = {
                    "id":id,
                    "name":name,
                    "url_key":url_key,
                    "description":description,
                    "images_url":images_url
                }
                pretty_json = json.dumps(info,indent=2)
                logging.info(f"Product information id: {data}")
                logging.info(pretty_json)
            else:
                logging.info(f"Could not get product information id: {data}")
        except Exception as e:
            logging.error(f"Unknown error with product {data}: {e}")
        write_file_csv('data_tiki.csv',pretty_json)
if __name__ == "__main__":
    main()
