import time
import logging
import requests
from requests.exceptions import HTTPError
import json
import re
import os
import pickle
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Ghi log ra file crawl_tiki.log
logging.basicConfig(filename='crawl_tiki.log',filemode='a',format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# file lưu data từ ram vào file
PICKLE_FILE = "crawled_ids.txt"

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

# load checkpoint sử dụng pickle để đọc file crawled_ids.txt
def load_crawled_ids():
    if os.path.exists(PICKLE_FILE):
        try:
            with open(PICKLE_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logging.error(f"Error loading crawled_ids from {PICKLE_FILE}: {e}")
            return set()
    return set()

# Save product id từ ram về file
def save_crawled_ids(crawled_ids):
    try:
        with open(PICKLE_FILE, "wb") as f:
            pickle.dump(crawled_ids, f)
    except Exception as e:
        logging.error(f"Error saving crawled_ids to {PICKLE_FILE}: {e}")

# để đọc được batch number của file 
def get_next_batch_number(output_dir="."):
    existing_batches = []
    try:
        for f in os.listdir(output_dir):
            match = re.match(r"data_tiki_batch_(\d+)\.json", f)
            if match:
                try:
                    existing_batches.append(int(match.group(1)))
                except Exception as e:
                    logging.error(f"Error parsing batch number from file {f}: {e}")
        if not existing_batches:
            return 0
        return max(existing_batches) + 1
    except Exception as e:
        logging.error(f"Error reading batch files in {output_dir}: {e}")
        return 0


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
        logging.error(f"HTTP Error: {exception.response.status_code} - ProductID: {product_id}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error send message: {e}")
        return []

# Loại bỏ các đoạn HTML trong text
def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)



def main():
    try:
        start_time = time.time() 
        data_tiki = read_file_csv('ids_part1.csv')
        all_products = []
        crawled_ids = load_crawled_ids()
        batch_size = 1000
        batch_number = get_next_batch_number()

        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = []
            for data in data_tiki:
                if data in crawled_ids:
                    logging.info(f"[Skip] Already crawled: {data}")
                    continue
                future = executor.submit(get_product_from_tiki, data)
                futures.append((data, future))  # Lưu kèm ID

            for product_id, future in futures:
                try:
                    product_info = future.result()
                    if product_info and isinstance(product_info, dict):
                        id = product_info.get('id', [])
                        name = product_info.get('name', [])
                        url_key = product_info.get('url_key', [])
                        price = product_info.get('price', [])
                        description = product_info.get('description', [])
                        images_url = product_info.get('images', [])
                        base_urls = [item['base_url'] for item in images_url]

                        info = {
                            "id": id,
                            "name": clean_html(name),
                            "url_key": url_key,
                            "description": clean_html(description),
                            "price": price,
                            "images_url": base_urls
                        }
                        all_products.append(info)
                        logging.info(json.dumps(info, indent=2))

                        if len(all_products) == batch_size:
                            batch_filename = f'data_tiki_batch_{batch_number}.json'
                            write_file_json(batch_filename, all_products)

                            # Sau khi ghi file thành công => mới cập nhật pickle
                            for p in all_products:
                                crawled_ids.add(str(p["id"]))
                            save_crawled_ids(crawled_ids)

                            logging.info(f"[OK] Batch {batch_number} saved: {len(all_products)} products")
                            batch_number += 1
                            all_products = []
                    else:
                        logging.info(f"[Fail] Could not get product info: {product_id}")
                except Exception as e:
                    logging.error(f"[ERROR] {product_id}: {e}")
    finally:
        if all_products:
            batch_filename = f'data_tiki_batch_{batch_number}.json'
            write_file_json(batch_filename, all_products)

            for p in all_products:
                crawled_ids.add(str(p["id"]))
            save_crawled_ids(crawled_ids)

            logging.info(f"[OK] Final batch {batch_number} saved: {len(all_products)} products")

        elapsed_time = time.time() - start_time
        logging.info(f"Total time: {elapsed_time:.2f} seconds")
        if data_tiki:
            logging.info(f"Average time: {(elapsed_time * 1000) / len(data_tiki):.2f} ms")
        else:
            logging.info("No products fetched!")
if __name__ == "__main__":
    main()
