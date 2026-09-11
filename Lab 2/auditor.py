inventory = 0
failedEntries = 0

while True:
    stock = input("Please enter the inventory count (or type 'quit' to quit):")
    print(stock)
    if stock.isdigit(): #Cheking if the input is a positive digit

            inventory = int(stock) + inventory
            print("Inventory count is: ", inventory)

            if inventory > 500: #Checking if the inventory is more than 500
                print("Warning: Inventory count is above 500, it is currently", inventory, "and the failed entries are", failedEntries )
                break
    else:
        if stock.lower() == 'quit': #Checking if the iput is "quit" to exit the program
            print("The amount of stocks are", stock,"and the failed entries is", failedEntries)
            break #This command exits the program.
        elif stock[0] == '-' and stock[1:].isdigit(): #For checking negative numbers
            print("Invalid due to negative inventory count.")
            failedEntries += 1
        else:
            print("Invalid input. Please enter a valid inventory count or type 'quit' to exit.")
            failedEntries += 1