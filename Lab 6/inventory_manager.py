import json
from product import Product


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


def load_inventory():
    inventory = Inventory()

    try:
        with open("inventory.json", "r") as file:
            saved_products = json.load(file)

        for data in saved_products:
            product = Product(
                data["id"],
                data["name"],
                float(data["price"]),
                int(data["stock"])
            )
            inventory.add_product(product)

    except FileNotFoundError:
        print("inventory.json not found. Starting with an empty inventory.")

    return inventory


def save_inventory(inventory):
    saved_products = []

    for product in inventory.get_products():
        saved_products.append({
            "id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock()
        })

    with open("inventory.json", "w") as file:
        json.dump(saved_products, file, indent=4)

    print("Inventory saved successfully!")