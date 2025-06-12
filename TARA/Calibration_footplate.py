import serial
import time
import sys

# Configuration
PORT = 'COM4'  # Replace with your COM port
BAUD_RATE = 115200
TIMEOUT = 1  # Timeout in seconds
MAX_RECONNECT_ATTEMPTS = 20
RECONNECT_DELAY = 5  # Seconds between reconnection attempts
CALIBRATION_CYCLES = 20  # Number of cycles to run calibration

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

def zero_system():
    """Initial zeroing phase - wait for stable readings"""
    print("=" * 50)
    print("CALIBRATION: ZEROING PHASE")
    print("=" * 50)
    print("Please ensure the machine is at rest position.")
    print("Waiting for system to stabilize...")
    
    # Wait a bit for system to stabilize
    time.sleep(3)
    print("Zeroing complete. System ready for calibration.")
    print()

def calibration_phase(ser):
    """Run calibration for specified number of cycles"""
    print("=" * 50)
    print("CALIBRATION: MEASUREMENT PHASE")
    print("=" * 50)
    print(f"Starting calibration measurement for {CALIBRATION_CYCLES} cycles.")
    print("Please start the fatigue testing machine now.")
    print()
    
    force_readings = []
    cycle_count = 0
    
    try:
        while cycle_count < CALIBRATION_CYCLES:
            try:
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    # Parse the data: expecting format "cycle,time,force"
                    data = line.split(',')
                    if len(data) >= 3:
                        try:
                            cycle = int(data[0])
                            time_ms = float(data[1])
                            force = float(data[2])
                            
                            force_readings.append(force)
                            cycle_count += 1
                            
                            print(f"Cycle {cycle_count}/{CALIBRATION_CYCLES}: "
                                  f"Cycle={cycle}, Time={time_ms}ms, Force={force:.2f}N")
                            
                        except ValueError:
                            # Skip lines that can't be parsed as numbers
                            print(f"Skipping invalid data: {line}")
                            continue
                    else:
                        # Skip incomplete data lines
                        print(f"Skipping incomplete data: {line}")
                        continue
                
            except serial.SerialException:
                print("Lost connection. Attempting to reconnect...")
                ser.close()
                ser = connect_serial()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\nCalibration interrupted by user.")
        return None
    
    return force_readings

def calculate_and_display_results(force_readings):
    """Calculate and display calibration results"""
    if not force_readings:
        print("No valid force readings collected.")
        return
    
    print("\n" + "=" * 50)
    print("CALIBRATION RESULTS")
    print("=" * 50)
    
    # Calculate statistics
    avg_force = sum(force_readings) / len(force_readings)
    min_force = min(force_readings)
    max_force = max(force_readings)
    force_range = max_force - min_force
    
    # Calculate standard deviation
    variance = sum((f - avg_force) ** 2 for f in force_readings) / len(force_readings)
    std_dev = variance ** 0.5
    
    print(f"Total readings collected: {len(force_readings)}")
    print(f"Average force: {avg_force:.3f} N")
    print(f"Minimum force: {min_force:.3f} N")
    print(f"Maximum force: {max_force:.3f} N")
    print(f"Force range: {force_range:.3f} N")
    print(f"Standard deviation: {std_dev:.3f} N")
    print(f"Coefficient of variation: {(std_dev/avg_force)*100:.2f}%")
    
    print("\n" + "=" * 50)
    print("CALIBRATION COMPLETE")
    print("=" * 50)

def main():
    print("FATIGUE TESTING MACHINE - CALIBRATION MODE")
    print("=" * 50)
    
    # Connect to serial port
    ser = connect_serial()
    
    try:
        # Phase 1: Zeroing
        zero_system()
        
        # Phase 2: Calibration measurement
        force_readings = calibration_phase(ser)
        
        # Phase 3: Results
        if force_readings:
            calculate_and_display_results(force_readings)
        
    except Exception as e:
        print(f"Error during calibration: {e}")
    finally:
        ser.close()
        print("Serial connection closed.")

if __name__ == '__main__':
    main()