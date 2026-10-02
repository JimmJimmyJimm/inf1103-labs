import json


def main():

    inventory = load_inventory()
    display_menu(inventory)

#Display the menu
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
            display_all(inventory)

        elif choice == "2":
            add_product(inventory)

        elif choice == "3":
            update_stock(inventory)

        elif choice == "4":
            search_product(inventory)

        elif choice == "5":
            save_inventory(inventory)

        elif choice == "6":
            print("Saving inventory before exit...")
            save_inventory(inventory)
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break

        else:
            print("Invalid option.")


def load_inventory():

    inventory = []

    #Try to do the following code, if it fails, it will go to the except block.
    try:
        with open ("inventory.json", "r") as file:

            #Opens the inventory.json file and loads the data into the inventory list.
            inventory = json.load(file)

        #The value that is returned if the function is called.
        return inventory

    #If the try fails.
    except FileNotFoundError:
        print("inventory.json not found.")
        return inventory

def save_inventory(inventory):

    #Opens the inventory.json file in write mode and saves the current inventory data to it.
    with open("inventory.json", "w") as file:
        #Update the inventory.json file with the current inventory data.
        json.dump(inventory, file, indent=4)

    print("Inventory saved successfully!")



def display_all(inventory):

    print("Current Inventory")
    print("------------------------------------------------")

    for product in inventory:

        print(
            f"ID: {product['id']} | "
            f"Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | "
            f"Stock: {product['stock']}"
        )

    print("------------------------------------------------")

#Needs to pass inventory into it. Rn iventory is a list of dictionaries and we need to pass it in so that we can add more dictionaries to the list.
def add_product(inventory):

    print("Add New Product")

    product_id = input("Product ID: ")
    product_name = input("Product Name: ")
    price = float(input("Price: "))
    stock = int(input("Stock Quantity: "))

    product = {
        "id": product_id,
        "name": product_name,
        "price": price,
        "stock": stock
    }

    inventory.append(product)

    print("Product added successfully!")


def update_stock(inventory):

    print("Update Stock")

    product_id = input("Enter Product ID: ")

    for product in inventory:

        if product["id"] == product_id:

            print("Product Found:")
            print("Name:", product["name"])
            print("Current Stock:", product["stock"])

            new_stock = int(input("New Stock Quantity: "))

            product["stock"] = new_stock

            print("Stock updated successfully!")
            return


def search_product(inventory):

    print("Search Product")

    product_id = input("Enter Product ID: ")

    for product in inventory:

        if product["id"] == product_id:

            print("Product Found")
            print("--------------------------------")
            print("ID:", product["id"])
            print("Name:", product["name"])
            print(f"Price: ${product['price']:.2f}")
            print("Stock:", product["stock"])
            print("--------------------------------")

            return

    print("Product not found.")




# __name__ (Program Entry Point)
if __name__=="__main__":
    main()