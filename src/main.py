import sys 
import platform

def main():
    print("--- Local Agent System Info ---")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")
    print("Code end")

if __name__ == "__main__":
    main()