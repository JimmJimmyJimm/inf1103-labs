print("========================================")
print("Welcome here")
print("My first post!")
print("========================================")

username = "cool_creator"
bio = "Fun Blogger"
followers = 100

print("Username:", username)
print("Bio:", bio)
print("Followers:", followers)

followers = 100

followers += 50
print("Day 1", followers)

followers += 20
print("Day 2", followers)

followers += 10
print("Day 3", followers)

username = input("Enter your new username: ")
age = int(input("Enter your age: "))
category = input("Enter Content Category: ")

print("\nInstagram Profile:")
print("=========================================")
print("Username:", username)
print("Age:", age)
print("Category:", category)

if age>40 and category=="fun":
    print("You are old what is fun for you?")