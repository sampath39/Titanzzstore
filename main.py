from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app)

def flipkart_search(product):
    try:
        query = quote_plus(product)
        url = f'https://www.flipkart.com/search?q={query}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        cards = soup.find_all("div", class_="cPHDOP col-12-12")
        
        # Regex patterns
        price_pattern = r"₹([\d,]*)"
        product_name_pattern = r'<div class="KzDlHZ">(.*?)</div>'
        link_pattern = r"href=\"([a-zA-Z-0-9\/]*)"
        image_url_pattern = r"(https:\/\/rukminim2\.flixcart\.com\/image\/[^\"]+)"

        details = []
        for card in cards[3:-5]:
            data = str(card)

            name_match = re.findall(product_name_pattern, data)
            price_match = re.findall(price_pattern, data)
            link_match = re.findall(link_pattern, data)
            image_match = re.findall(image_url_pattern, data)

            if name_match and price_match and link_match and image_match:
                res = {
                    "name": name_match[0],
                    "price": price_match[0],
                    "url": "https://www.flipkart.com" + link_match[0],
                    "website": "flipkart",
                    "image_url": image_match[0]
                }
                details.append(res)

        return details

    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
        return None

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
        return "BuyHatke URL scraping still requires Selenium (JavaScript interaction). <a href='/'>Go back</a>"
    else:
        items = flipkart_search(data['item'])
        if items is None:
            return "Try again <a href='/'>Go back</a>"
        return render_template('temp.html', items=items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
