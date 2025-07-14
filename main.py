from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import re
import time
from urllib.parse import quote_plus
import pyperclip

# ✅ No need to override template_folder if using /templates folder
app = Flask(__name__)  
CORS(app)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def flipkart_search(product):
    try:
        query = quote_plus(product)
        url = f'https://www.flipkart.com/search?q={query}'

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        time.sleep(3)

        products = driver.find_elements(By.XPATH, "//div[@class='cPHDOP col-12-12']")
        price_pattern = r"<div class=\"Nx9bqj _4b5DiR\">₹([\d,]*)</div>"
        product_name_pattern = '<div class="KzDlHZ">(.*?)</div>'
        link_pattern = r"href=\"([a-zA-Z-0-9\/]*)"
        image_url = r"src=\"(https:\/\/rukminim2\.flixcart\.com\/image\/[^\"]+)\""

        details = []
        for i in products[3:-5]:
            data = i.get_attribute("outerHTML")
            res = {
                "name": re.findall(product_name_pattern, data)[0],
                "price": re.findall(price_pattern, data)[0],
                "url": re.findall(link_pattern, data)[0],
                "website": "flipkart",
                "image_url": re.findall(image_url, data)[0]
            }
            details.append(res)

        driver.quit()
        return details

    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
        return None

def aggrigate(item):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://buyhatke.com')
    pyperclip.copy(item)

    inp = driver.find_element(By.XPATH, "//input[@id='product-search-bar']")
    inp.send_keys(Keys.CONTROL, 'v')

    time.sleep(5)
    try:
        driver.find_element(By.XPATH, '/html/body/div/div[1]/div[1]/main/section/div[2]/section[1]/button').click()
    except Exception as e:
        print(f'None {e}')

    driver.implicitly_wait(5)
    itms = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[1]/main/section/div[2]/section[1]')
    data = itms.get_attribute('outerHTML')
    prod = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[1]/main/section/div[1]')
    prodata = prod.get_attribute('outerHTML')
    driver.quit()

    return {"data": data, "productData": prodata}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getproducts')
def get_products():
    item = request.args.get('item')
    products = flipkart_search(item)
    return jsonify(products)

@app.route('/getSuggestions', methods=['POST'])
def get_suggestion():
    data = request.form
    print(data)

    if data['item'].startswith('https'):
        details = aggrigate(data['item'])
        return render_template('aggrigate.html', content=details['data'], product=details['productData'])
    else:
        items = flipkart_search(data['item'])
        if items is None:
            return "Try again <a href='/'>Go back</a>"
        return render_template('temp.html', items=items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
