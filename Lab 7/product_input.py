from product import validate_measurement
from physical_product import SHIPPING_RATE_PER_KG


def read_product_details():
    while True:
        product_type = input("Product type (1 physical / 2 digital): ").strip().lower()
        product_type = {"1": "physical", "2": "digital"}.get(product_type, product_type)
        if product_type in ("physical", "digital"):
            break
        print("Choose physical or digital.")
    field = "weight" if product_type == "physical" else "download_size"
    label = "Weight (kg)" if product_type == "physical" else "Download size (MB)"
    while True:
        try:
            measurement = float(input(f"{label}: "))
            validate_measurement(measurement, label)
            if product_type == "physical":
                validate_measurement(measurement * SHIPPING_RATE_PER_KG, "Shipping cost")
            return {"type": product_type, field: measurement}
        except ValueError as error:
            print(f"Invalid input: {error}")
