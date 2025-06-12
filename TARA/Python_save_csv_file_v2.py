import serial
import time
import os
import csv
import sys

# Configuration
PORT = 'COM4'  # Replace with your COM port
BAUD_RATE = 115200
TIMEOUT = 1  # Timeout in seconds
OUTPUT_FOLDER = r"C:\Users\Administrator\Abilitymade Dropbox\Abilitymade team folder\Product Development & Testing\20241126_TARA\CSV FILES"
MAX_ROWS = 1000000  # Maximum rows per file
MAX_RECONNECT_ATTEMPTS = 20
RECONNECT_DELAY = 5  # Seconds between reconnection attempts

def create_new_file(base_name, part):
    file_name = f"{base_name}_part{part}.csv"
    full_path = os.path.join(OUTPUT_FOLDER, file_name)
    return open(full_path, 'w', newline='')

def connect_serial():
    for attempt in range(MAX_RECONNECT_ATTEMPTS):
        try:
            ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
            print(f"Successfully connected to {PORT}")
            return ser
        except serial.SerialException as e:
            print(f"Attempt {attempt + 1}/{MAX_RECONNECT_ATTEMPTS}: Failed to connect. Error: {e}")
            if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                print(f"Retrying in {RECONNECT_DELAY} seconds...")
                time.sleep(RECONNECT_DELAY)
    print("Failed to establish connection after multiple attempts. Exiting.")
    sys.exit(1)

def main():
    base_file_name = input("Enter base file name to save the data (e.g., 'cc3d_A'): ")
    
    ser = connect_serial()
    
    part = 1
    row_count = 0
    current_file = create_new_file(base_file_name, part)
    csv_writer = csv.writer(current_file)
    csv_writer.writerow(['Cycle', 'Time (ms)', 'Force(N)'])  # Write header
    
    print("Starting data acquisition. Press Ctrl+C to stop.")

    try:
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    csv_writer.writerow(line.split(','))
                    row_count += 1
                    print(line)  # Print to console for real-time feedback
                    
                    if row_count >= MAX_ROWS:
                        current_file.close()
                        part += 1
                        current_file = create_new_file(base_file_name, part)
                        csv_writer = csv.writer(current_file)
                        csv_writer.writerow(['Cycle', 'Time (ms)', 'Force(N)'])  # Write header
                        row_count = 0
                
            except serial.SerialException:
                print("Lost connection. Attempting to reconnect...")
                ser.close()
                ser = connect_serial()
            
            # Add a small delay to prevent excessive CPU usage
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()
        current_file.close()
        print("Data acquisition complete.")

if __name__ == '__main__':
    main()
