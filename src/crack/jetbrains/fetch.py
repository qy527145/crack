import json
import requests
from bs4 import BeautifulSoup
from base64 import b64decode

if __name__ == '__main__':
    soup = BeautifulSoup(
        requests.get('https://hardbin.com/ipfs/bafybeia4nrbuvpfd6k7lkorzgjw3t6totaoko7gmvq5pyuhl2eloxnfiri/').text,
        "lxml"
    )
    keys = json.loads(soup.find_all('script')[-1].text.split('\n')[2][21:-1])
    infos = []
    product_set = set()
    for item in soup.findAll(name="article", attrs={"class": "card"}):
        short_name = item['data-sequence']
        name = item.h1.text
        version = item.button['data-version']
        key = keys[short_name][version]
        license_json = json.loads(b64decode(key.split('-')[1]).decode())
        products = [p['code'] for p in license_json['products']]
        product_set.update(products)
        infos.append((short_name, name, version, products))
    license_data = json.load(open('licenses.json'))
    products_json = []
    for product in product_set:
        products_json.append(
            {'code': product, 'extended': True, 'fallbackDate': '9999-12-31', 'paidUpTo': '9999-12-31'})
    license_data['products'] = products_json
    json.dump(license_data, open('licenses.json', 'w'))
    pass
