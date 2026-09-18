MAX_CAPACITY = 500
TAX_RATE = 0.1

def main():
    inventory = 0
    failedEntries = 0
    tax_amount = 0
    exit_program = False

    while not exit_program:        
        order = get_valid_input()
        if order == "quit":
            exit_program = True
            break
        elif order == "invalid":
            failedEntries += 1
            continue
        else:
            inventory = process_delivery(inventory, order)
            tax_amount = calculate_tax(inventory)
            print("Inventory count is: ", inventory)
            if inventory > MAX_CAPACITY: #Checking if the inventory is more than the maximum capacity
                print("Warning: Inventory count is above maximum capacity")
                exit_program = True
                break   
    generate_report(inventory, failedEntries)      


def get_valid_input():
    order = input("Please enter the order quantity (or type 'quit' to quit):")

    if order.isdigit(): #Cheking if the input is a positive digit
        return int(order)
    else:
        if order.lower() == 'quit': #Checking if the iput is "quit" to exit the program
            return "quit"  

        elif order == "": #Checking if the input is empty
            print("Input cannot be empty. Please enter a valid order quantity or type 'quit' to exit.")
            return "invalid"
                          
        elif order[0] == '-' and order[1:].isdigit(): #For checking negative numbers
            print("Invalid due to negative order quantity")
            return "invalid"
        else:
            print("Invalid input. Please enter a valid order quantity or type 'quit' to exit.")
            return "invalid"


def calculate_tax(amount):
    tax = amount * TAX_RATE
    return tax


def process_delivery(current_total, new_value):
    return current_total + new_value


def generate_report(total_inventory, failed_entries):
    print("Generating report...")
    print("The amount of orders are", total_inventory,"and the failed entries is", failed_entries)

# __name__ (Program Entry Point)
if __name__=="__main__":
    main()