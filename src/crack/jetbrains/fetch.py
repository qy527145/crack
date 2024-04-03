import json
from base64 import b64decode

import requests
from bs4 import BeautifulSoup


def fetch():
    soup = BeautifulSoup(
        requests.get('https://hardbin.com/ipfs/bafybeia4nrbuvpfd6k7lkorzgjw3t6totaoko7gmvq5pyuhl2eloxnfiri/').text,
        "lxml"
    )
    keys = json.loads(soup.find_all('script')[-1].text.split('\n')[2][21:-1])
    product_infos = dict()
    for item in soup.findAll(name="article", attrs={"class": "card"}):
        if item.find_all(attrs={"class": "icon icon-plugin"}):
            continue
        short_name = item['data-sequence']
        name = item.h1.text
        version = item.button['data-version']
        key = keys[short_name][version]
        license_json = json.loads(b64decode(key.split('-')[1]).decode())
        product_infos[name] = license_json['products']
    return product_infos


def make_licenses(products):
    license_data = json.load(open('licenses_base.json'))
    products_json = []
    for name, code in products:
        products_json.append({
            'code': code,
            'fallbackDate': '9999-12-31',
            'paidUpTo': '9999-12-31',
            'extended': True,
        })
    # license_data['products'].extend(products_json)
    license_data['products'] = products_json
    json.dump(license_data, open('licenses_base.json', 'w'), indent=2)


if __name__ == '__main__':
    ides = []
    infos = fetch()
    for name, products in infos.items():
        for product in products:
            if not product['extended']:
                ides.append((name, product['code']))
    make_licenses(ides)
