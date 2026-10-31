#Main
from product import Product
from inventory_manager import load_inventory, save_inventory


def main():
    inventory = load_inventory()
    display_menu(inventory)


def display_menu(inventory):
    while True:
        print("\n========================================")
        print("INVENTORY MANAGEMENT SYSTEM")
        print("========================================")
        print("----------- MENU -----------")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")
        print("----------------------------")

        choice = input("Enter option: ")

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option.")


def add_product(inventory):
    print("Add New Product")
    product_id = input("Product ID: ").strip()
    product_name = input("Product Name: ").strip()

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        product = Product(product_id, product_name, price, stock)
    except ValueError:
        print("Invalid input! Price must be a number and stock must be a whole number.")
        return

    if inventory.add_product(product):
        print("Product added successfully!")
    else:
        print("A product with that ID already exists.")


def update_stock(inventory):
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip()
    product = inventory.search_product(product_id)

    if product is None:
        print("Product not found.")
        return

    print("Product Found:")
    print("Name:", product.get_name())
    print("Current Stock:", product.get_stock())

    try:
        new_stock = int(input("New Stock Quantity: "))
    except ValueError:
        print("Stock must be a whole number.")
        return

    if product.update_stock(new_stock):
        print("Stock updated successfully!")
    else:
        print("Stock quantity cannot be negative.")


def search_product(inventory):
    print("Search Product")
    product_id = input("Enter Product ID: ").strip()
    product = inventory.search_product(product_id)

    if product is None:
        print("Product not found.")
    else:
        print("Product Found")
        print("--------------------------------")
        product.display_information()
        print("--------------------------------")


if __name__ == "__main__":
    main()