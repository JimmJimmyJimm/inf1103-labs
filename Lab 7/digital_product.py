from product import Product, validate_measurement


class DigitalProduct(Product):
    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        validate_measurement(download_size, "Download size")
        self.__download_size = download_size

    def get_download_size(self):
        return self.__download_size

    def display_information(self):
        super().display_information()
        print(f"Download size: {self.__download_size} MB")
        print(self.get_fulfilment_info())

    def get_fulfilment_info(self):
        return "Delivered digitally through a download."
