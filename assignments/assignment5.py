buffer = []
while True:
    choice = input("Enter text to write to file: ")

    if choice == "q":
        break
    elif choice == "o":
        with open("./assignment5.txt", mode="r") as f:
            print(f.read())
    else:
        with open("./assignment5.txt", mode="a") as f:
            f.write(f"{choice}\n")
