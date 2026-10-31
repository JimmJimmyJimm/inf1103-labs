from abc import ABC, abstractmethod
from math import isfinite


def validate_measurement(value, label):
    try:
        valid = type(value) in (int, float) and isfinite(value) and value >= 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{label} must be a finite, non-negative number.")


class Product(ABC):
    def __init__(self, product_id, name, price, stock):
        if not isinstance(product_id, str) or not product_id.strip():
            raise ValueError("Product ID cannot be empty.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name cannot be empty.")
        validate_measurement(price, "Price")
        if type(stock) is not int or stock < 0:
            raise ValueError("Stock must be a non-negative whole number.")

        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        if type(quantity) is not int or quantity < 0:
            return False

        self.__stock = quantity
        return True

    def display_information(self):
        print(
            f"ID: {self.__product_id} | "
            f"Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | "
            f"Stock: {self.__stock}"
        )

    @abstractmethod
    def get_fulfilment_info(self):
        pass
