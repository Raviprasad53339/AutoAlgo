import subprocess
import threading
import time
import os

def run_long_strategy():
    subprocess.run(['python', 'long_entry_strategy.py'])

def run_short_strategy():
    subprocess.run(['python', 'short_entry_strategy.py'])

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change current working directory to the script's directory
    os.chdir(script_dir)
    
    # Create threads for each strategy
    long_thread = threading.Thread(target=run_long_strategy)
    short_thread = threading.Thread(target=run_short_strategy)
    
    # Start the threads
    long_thread.start()
    short_thread.start()
    
    # Wait for both threads to complete
    long_thread.join()
    short_thread.join()

if __name__ == "__main__":
    print("Starting both trading strategies...")
    main()