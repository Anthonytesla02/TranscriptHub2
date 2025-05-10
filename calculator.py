#!/usr/bin/env python3
"""
Simple Command-Line Calculator

This program provides a simple calculator interface that can perform
basic arithmetic operations such as addition, subtraction, multiplication,
and division.
"""


def add(x, y):
    """Add two numbers"""
    return x + y


def subtract(x, y):
    """Subtract y from x"""
    return x - y


def multiply(x, y):
    """Multiply two numbers"""
    return x * y


def divide(x, y):
    """Divide x by y"""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y


def get_float_input(prompt):
    """Get and validate float input from user"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_operation():
    """Get operation choice from user"""
    valid_operations = {
        '1': ('Addition', add),
        '2': ('Subtraction', subtract),
        '3': ('Multiplication', multiply),
        '4': ('Division', divide)
    }
    
    while True:
        print("\nAvailable operations:")
        for key, (name, _) in valid_operations.items():
            print(f"{key}. {name}")
        print("q. Quit")
        
        choice = input("Enter your choice (1/2/3/4/q): ").strip().lower()
        
        if choice == 'q':
            return None
        
        if choice in valid_operations:
            return valid_operations[choice][1]
        
        print("Invalid choice. Please try again.")


def calculator():
    """Main calculator function"""
    print("Welcome to Simple Calculator!")
    print("============================")
    
    result = None
    first_calculation = True
    
    while True:
        # For first calculation, get both numbers
        if first_calculation:
            num1 = get_float_input("Enter first number: ")
            operation = get_operation()
            if operation is None:
                break
            num2 = get_float_input("Enter second number: ")
            
            try:
                result = operation(num1, num2)
                print(f"\nResult: {result}")
                first_calculation = False
            except ValueError as e:
                print(f"Error: {e}")
        
        # For subsequent calculations, use the previous result as first number
        else:
            print("\nContinue with result or start new calculation?")
            print("1. Continue with result")
            print("2. Start new calculation")
            print("q. Quit")
            
            choice = input("Enter your choice (1/2/q): ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '2':
                first_calculation = True
                continue
            elif choice == '1':
                print(f"Using previous result: {result}")
                operation = get_operation()
                if operation is None:
                    break
                num2 = get_float_input("Enter number: ")
                
                try:
                    result = operation(result, num2)
                    print(f"\nResult: {result}")
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Invalid choice. Please try again.")
    
    print("\nThank you for using Simple Calculator!")


if __name__ == "__main__":
    calculator()
