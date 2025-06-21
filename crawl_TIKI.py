import time
import logging
import requests
from requests.exceptions import HTTPError
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Ghi log
logging.basicConfig(filename='crawl_tiki.log',filemode='a',format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)



# Đọc file product_id để lấy id
def read_file_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.readlines()
            logging.info(f"Read file successfully: {file_path}, line number: {len(data)}")
            return [line.strip() for line in data]
    except Exception as e:
        logging.error(f"Error read file {file_path}: {e}")
        return []

# ghi ra file json
def write_file_json(file_path, products):
    try: 
        with open(file_path,'w', encoding='utf-8') as outfile:
            json.dump(products, outfile, ensure_ascii=False, indent=2)
        logging.info(f"Json saved to {file_path}")
    except Exception as e:
        logging.error(f"Error Json file {file_path}: {e}")
        return []

# Get sp từ tiki
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
# Parse html
def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def main():
    start_time = time.time() 
    data_tiki = read_file_csv('products.csv')
    all_products = []
    batch_size = 1000
    batch_number = 1

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        for data in data_tiki:
            future = executor.submit(get_product_from_tiki, data)
            futures.append(future)
        for data in futures:
            try:
                product_info = data.result()
                
                if product_info and isinstance(product_info, dict):
                    id = product_info.get('id',[])
                    name = product_info.get('name',[])
                    url_key = product_info.get('url_key',[])
                    price = product_info.get('price',[])
                    description = product_info.get('description',[]) 
                    images_url = product_info.get('images', [])
                    base_urls = []
                    for item in images_url:
                        base_urls.append(item['base_url'])
                    info = {
                        "id":id,
                        "name":clean_html(name),
                        "url_key":url_key,
                        "description":clean_html(description),
                        "price":price,
                        "images_url":base_urls
                    }
                    all_products.append(info)
                    logging.info(f"Product information id: {data}")
                    logging.info(json.dumps(info, indent=2))
                    
                    # Ghi batch file 1000 request/batch
                    if len(all_products) == batch_size:
                        batch_filename = f'data_tiki_batch_{batch_number}.json'
                        write_file_json(batch_filename, all_products)
                        logging.info(f"Batch {batch_number} saved: {len(all_products)} products")
                        batch_number += 1
                        all_products = []
                  
                else:
                    logging.info(f"Could not get product information id: {data}")
            except Exception as e:
                logging.error(f"Unknown error with product {data}: {e}")
        if all_products:
            batch_filename = f'data_tiki_batch_{batch_number}.json'
            write_file_json(batch_filename, all_products)
            logging.info(f"Batch {batch_number} saved: {len(all_products)} products")
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Total time: {elapsed_time:.2f} seconds")
    if data_tiki:
        logging.info(f"Average time: {(elapsed_time * 1000) / len(data_tiki):.2f} ms")
    else:
        logging.info("No products fetched!")
if __name__ == "__main__":
    main()
