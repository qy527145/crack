import json
import os

import grequests
import requests

# 过期时间
EXPIRE_DATE = os.environ.get("EXPIRE_DATE", "9999-12-31")


def search(name=None, show_code=False):
    # types = {'FREE', 'FREEMIUM', 'PAID'}
    types = {"FREEMIUM", "PAID"}
    params = {
        "offset": 0,
        "max": 10000,
        "pricingModels": types,
    }
    if name:
        params["search"] = name
    plugins = (
        requests.get("https://plugins.jetbrains.com/api/searchPlugins", params=params)
        .json()
        .get("plugins", [])
    )
    if show_code:
        for plugin in plugins:
            yield (
                str(plugin["id"]),
                plugin["name"],
                plugin["pricingModel"],
                get_plugin_code(plugin["id"]),
            )
    else:
        for plugin in plugins:
            yield str(plugin["id"]), plugin["name"]


def get_plugin_code(plugin_id):
    plugin_info = requests.get(
        f"https://plugins.jetbrains.com/api/plugins/{plugin_id}"
    ).json()
    if plugin_info.get("purchaseInfo"):
        return plugin_info["purchaseInfo"].get("productCode")


def get_plugin_codes(plugin_ids):
    reqs = [
        grequests.get(f"https://plugins.jetbrains.com/api/plugins/{plugin_id}")
        for plugin_id in plugin_ids
    ]
    for rsp in grequests.imap(reqs):
        if rsp.status_code == 200:
            rsp_json = rsp.json()
            yield str(rsp_json["id"]), rsp_json["purchaseInfo"].get("productCode")


class JetBrainPlugin:
    def __init__(self):
        if os.path.isfile("plugins.json"):
            self.id_map = json.load(open("plugins.json", "r"))
        else:
            self.id_map = dict()

    def update(self):
        remote_id_map = {i[0]: i[1] for i in search()}
        keys = remote_id_map.keys() - self.id_map.keys()
        for plugin_id, plugin_code in get_plugin_codes(keys):
            self.id_map[plugin_id] = {
                "name": remote_id_map[plugin_id],
                "code": plugin_code,
                "extended": True,
            }
        self.dump()
        return self

    def make_licenses(self):
        license_data = json.load(open("licenses_base.json"))
        products_json = []
        for product in self.id_map.values():
            products_json.append(
                {
                    "code": product["code"],
                    "fallbackDate": EXPIRE_DATE,
                    "paidUpTo": EXPIRE_DATE,
                    "extended": product["extended"],
                }
            )
        for ide in license_data["products"]:
            ide["fallbackDate"] = EXPIRE_DATE
            ide["paidUpTo"] = EXPIRE_DATE
        license_data["products"].extend(products_json)
        json.dump(license_data, open("licenses.json", "w"), indent=2)
        return self

    def dump(self):
        json.dump(self.id_map, open("plugins.json", "w"), indent=2, sort_keys=True)


if __name__ == "__main__":
    obj = JetBrainPlugin()
    obj.update()
    obj.make_licenses()
