# main.py
import sys

def main():
    # Access command-line arguments
    args = sys.argv[1:]  # Exclude the script name
    print("Command-line arguments:", args)

if __name__ == "__main__":
    main()