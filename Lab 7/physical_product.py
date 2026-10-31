from product import Product, validate_measurement
from can_be_shipped import CanBeShipped


SHIPPING_RATE_PER_KG = 5.0


class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)
        validate_measurement(weight, "Weight")
        validate_measurement(weight * SHIPPING_RATE_PER_KG, "Shipping cost")
        self.__weight = weight

    def get_weight(self):
        return self.__weight

    def display_information(self):
        super().display_information()
        print(f"Weight: {self.__weight} kg")
        print(self.get_fulfilment_info())
        print(f"Shipping cost: ${self.calculate_shipping_cost():.2f}")

    def get_fulfilment_info(self):
        return "Requires physical shipping."

    def calculate_shipping_cost(self):
        return self.__weight * SHIPPING_RATE_PER_KG
