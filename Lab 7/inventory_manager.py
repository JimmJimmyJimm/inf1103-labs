import json
import os
from pathlib import Path
import tempfile

from physical_product import PhysicalProduct
from digital_product import DigitalProduct


class Inventory:
    def __init__(self):
        self.__products = []

    def add_product(self, product):
        if self.search_product(product.get_product_id()) is not None:
            return False

        self.__products.append(product)
        return True

    def search_product(self, product_id):
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product

        return None

    def display_all(self):
        print("Current Inventory")
        print("------------------------------------------------")

        if not self.__products:
            print("No products found.")

        for product in self.__products:
            product.display_information()

        print("------------------------------------------------")

    def get_products(self):
        return self.__products.copy()


def product_from_record(data):
    if not isinstance(data, dict):
        raise ValueError("Each inventory record must be an object.")
    try:
        common = (data["id"], data["name"], data["price"], data["stock"])
        if data["type"] == "physical":
            return PhysicalProduct(*common, data["weight"])
        if data["type"] == "digital":
            return DigitalProduct(*common, data["download_size"])
        raise ValueError("Unknown product type.")
    except KeyError as error:
        raise ValueError(f"Missing product field: {error.args[0]}") from error


def product_to_record(product):
    data = {
        "id": product.get_product_id(),
        "name": product.get_name(),
        "price": product.get_price(),
        "stock": product.get_stock()
    }
    if isinstance(product, PhysicalProduct):
        data.update(type="physical", weight=product.get_weight())
    elif isinstance(product, DigitalProduct):
        data.update(type="digital", download_size=product.get_download_size())
    else:
        raise ValueError("Unsupported product type.")
    return data


def backup_inventory(path, original):
    backup = path.with_name(path.name + ".bak")
    number = 1
    while True:
        try:
            with backup.open("xb") as file:
                file.write(original)
            return backup
        except FileExistsError:
            backup = path.with_name(f"{path.name}.bak.{number}")
            number += 1


def load_inventory(filename="inventory.json", classify_legacy=None):
    path = Path(filename)
    inventory = Inventory()
    try:
        original = path.read_bytes()
    except FileNotFoundError:
        print(f"{path} not found. Starting with an empty inventory.")
        return inventory
    saved_products = json.loads(original)
    if not isinstance(saved_products, list):
        raise ValueError("Inventory JSON must contain a list.")
    if any(not isinstance(data, dict) for data in saved_products):
        raise ValueError("Each inventory record must be an object.")
    has_legacy = any("type" not in data for data in saved_products)
    if has_legacy:
        if classify_legacy is None:
            raise ValueError("Legacy inventory requires classification through main.py.")
        backup = backup_inventory(path, original)
        print(f"Original inventory backed up to {backup}.")
    for data in saved_products:
        if "type" not in data:
            details = classify_legacy(data.copy())
            data = dict(data)
            data["type"] = details["type"]
            field = "weight" if details["type"] == "physical" else "download_size"
            data[field] = details[field]
        product = product_from_record(data)
        if not inventory.add_product(product):
            raise ValueError(f"Duplicate product ID: {product.get_product_id()}")
    if has_legacy:
        print("Migration validated. Choose option 5 to save; option 6 leaves the original unchanged.")
    return inventory


def save_inventory(inventory, filename="inventory.json"):
    path = Path(filename)
    records = [product_to_record(product) for product in inventory.get_products()]
    for record in records:
        product_from_record(record)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as file:
            temporary_path = Path(file.name)
            json.dump(records, file, indent=4, allow_nan=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    print("Inventory saved successfully!")
