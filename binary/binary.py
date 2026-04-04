def number_to_binary():
    binary_result = ""
    running = True

    while running:
        try:
            number = int(input("\nEnter a number (enter 0 to quit): "))
            specific = input("Do you want to see the steps? (type something for yes, enter for no): ")

            if number == 0:
                running = False

        except ValueError:
            print("Invalid input\n")
            continue

        bytes_count = number // 256
        bits_count = 8 * (bytes_count + 1)

        for i in range(bits_count):

            if number % 2 == 0:
                if specific != "":
                    print(f"0 {number}")
                binary_result = "0" + binary_result
            else:
                if specific != "":
                    print(f"1 {number}")
                binary_result = "1" + binary_result

            number = number // 2

        binary_result = binary_result.lstrip("0")

        if binary_result == "":
            binary_result = "0"

        print(f"Binary representation: {binary_result}")
        binary_result = ""

def binary_to_number():
    running = True

    while running:
        try:
            binary_input = input("\nEnter a binary number (enter 0 to quit): ")
            specific = input("Do you want to see the steps? (type something for yes, enter for no): ")
            
            if binary_input == "0":
                running = False

        except ValueError:
            print("Invalid input\n")
            continue

        if not all(bit in "01" for bit in binary_input):
            print("Invalid binary number")
            continue

        reversed_bits = binary_input[::-1]
        power = 0
        decimal_result = 0

        for bit in reversed_bits:
            bit = int(bit)
            value = bit * (2 ** power)
            decimal_result += value
            power += 1
            
            if specific != "":
                print(value)

        print(f"Decimal representation: {decimal_result}")

def main():
    while True:
        print("\n-----Binary Converter-----\n")
        print("1. Number to Binary")
        print("2. Binary to Number\n")

        try:
            option = int(input("Choose an option: "))
        
        except ValueError:
            print("Invalid input\n")
            continue

        if option == 1:
            number_to_binary()
        elif option == 2:
            binary_to_number()
        else:
            print("Invalid option")
if __name__ == "__main__":
    main()
