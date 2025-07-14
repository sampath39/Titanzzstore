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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if we're being blocked (login or captcha page)
        if "Login" in response.text or soup.title is None:
            print("⚠️ Detected bot block - returning fallback data.")
            return [{
                "name": "Sample Product",
                "price": "999",
                "url": "https://www.flipkart.com",
                "website": "flipkart",
                "image_url": "https://via.placeholder.com/200x200.png?text=Sample"
            }]

        cards = soup.find_all("div", class_="cPHDOP col-12-12")
        
        price_pattern = r"₹([\d,]*)"
        name_pattern = r'<div class="KzDlHZ">(.*?)</div>'
        link_pattern = r"href=\"([a-zA-Z0-9\/-]*)"
        image_pattern = r"(https:\/\/rukminim2\.flixcart\.com\/image\/[^\"]+)"

        details = []
        for card in cards[3:-5]:
            html = str(card)

            name = re.findall(name_pattern, html)
            price = re.findall(price_pattern, html)
            url_part = re.findall(link_pattern, html)
            image = re.findall(image_pattern, html)

            if name and price and url_part and image:
                details.append({
                    "name": name[0],
                    "price": price[0],
                    "url": "https://www.flipkart.com" + url_part[0],
                    "website": "flipkart",
                    "image_url": image[0]
                })

        return details

    except Exception as e:
        print("❌ Error:", e)
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
    query = data.get('item')

    if query:
        items = flipkart_search(query)
        if items is None or len(items) == 0:
            return "No products found. <a href='/'>Try again</a>"
        return render_template('temp.html', items=items)
    else:
        return "Invalid input. <a href='/'>Try again</a>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
