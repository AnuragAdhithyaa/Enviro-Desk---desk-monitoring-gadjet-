import serial 
import time 
import board 
import busio 
import adafruit_dht 
import adafruit_ssd1306 
from PIL import Image, ImageDraw, ImageFont 
from flask import Flask, jsonify, render_template 
import threading 
import sys 
import RPi.GPIO as GPIO 
app = Flask(__name__) 
# Serial port configuration for XIAO 
serial_port = '/dev/ttyACM0' 
baud_rate = 9600 
# Buzzer configuration 
BUZZER_PIN = 18  # GPIO18 (Physical Pin 12) 
GAS_THRESHOLD = 300  # MQ135 raw value threshold for high gas 
BUZZER_COOLDOWN = 30  # Seconds between buzzer alerts 
# DHT22 configuration 
dht_sensor = adafruit_dht.DHT22(board.D4) 
# SSD1306 OLED configuration (128x64, I2C) 
i2c = busio.I2C(board.SCL, board.SDA) 
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C) 
# Create blank image for drawing 
width = oled.width 
height = oled.height 
image = Image.new("1", (width, height)) 
draw = ImageDraw.Draw(image) 
font = ImageFont.load_default() 
# Global sensor values (persist last valid) 
mq135_value = 0 
soil_percent = 0.0 
temp = 0.0 
hum = 0.0 
last_buzzer_time = 0.0  # Track last buzzer activation 
# Gas concentration and threshold functions 
def raw_to_ppm(raw, gas_type): 
"""Approximate raw ADC to ppm (simplified, not precise).""" 
if gas_type == "CO2": 
return (raw * 2.5) + 200 
elif gas_type == "NH3": 
        return raw * 0.5 
    elif gas_type in ["NOx", "Alcohol", "Benzene"]: 
        return raw * 0.4 
    return 0 
 
def get_threshold_level(ppm, gas_type): 
    """Classify ppm into Low, Medium, High.""" 
    if gas_type == "CO2": 
        if ppm < 800: 
            return "Low" 
        elif ppm <= 1200: 
            return "Medium" 
        return "High" 
    elif gas_type in ["NH3", "NOx", "Alcohol", "Benzene"]: 
        if ppm < 50: 
            return "Low" 
        elif ppm <= 100: 
            return "Medium" 
        return "High" 
    return "Unknown" 
 
def clear_display(): 
    draw.rectangle((0, 0, width, height), outline=0, fill=0) 
 
def display_data(mq135, soil, temp, hum, cycle_index): 
    clear_display() 
    gases = ["CO2", "NH3", "NOx", "Alcohol", "Benzene"] 
    # Cycle through gases, showing 2 at a time 
    start_idx = (cycle_index % len(gases)) // 2 * 2 
    lines = [] 
    for i in range(2): 
        if start_idx + i < len(gases): 
            gas = gases[start_idx + i] 
            ppm = raw_to_ppm(mq135, gas) 
            level = get_threshold_level(ppm, gas) 
            lines.append(f"{gas}: {level}") 
        else: 
            lines.append("") 
    # Add soil and DHT22 temp/hum 
    lines.append(f"Soil: {soil:.2f}%") 
    lines.append(f"T: {temp:.1f}C H: {hum:.1f}%") 
    for i, line in enumerate(lines): 
        draw.text((0, i * 12), line, font=font, fill=255) 
    oled.image(image) 
    oled.show() 
 
# Flask routes 
@app.route('/') 
def index(): 
    global mq135_value, soil_percent, temp, hum 
    data = { 
        "mq135": mq135_value, 
        "soil": soil_percent, 
        "temp": temp, 
        "hum": hum, 
        "co2_level": get_threshold_level(raw_to_ppm(mq135_value, "CO2"), 
"CO2"), 
        "nh3_level": get_threshold_level(raw_to_ppm(mq135_value, "NH3"), 
"NH3"), 
        "nox_level": get_threshold_level(raw_to_ppm(mq135_value, "NOx"), 
"NOx"), 
        "alcohol_level": get_threshold_level(raw_to_ppm(mq135_value, 
"Alcohol"), "Alcohol"), 
        "benzene_level": get_threshold_level(raw_to_ppm(mq135_value, 
"Benzene"), "Benzene") 
    } 
    return render_template('index.html', data=data) 
 
@app.route('/data') 
def data(): 
    global mq135_value, soil_percent, temp, hum 
    return jsonify({ 
        "mq135": mq135_value, 
        "soil": soil_percent, 
        "temp": temp, 
        "hum": hum, 
        "co2_level": get_threshold_level(raw_to_ppm(mq135_value, "CO2"), 
"CO2"), 
        "nh3_level": get_threshold_level(raw_to_ppm(mq135_value, "NH3"), 
"NH3"), 
        "nox_level": get_threshold_level(raw_to_ppm(mq135_value, "NOx"), 
"NOx"), 
        "alcohol_level": get_threshold_level(raw_to_ppm(mq135_value, 
"Alcohol"), "Alcohol"), 
        "benzene_level": get_threshold_level(raw_to_ppm(mq135_value, 
"Benzene"), "Benzene") 
    }) 
 
def run_flask(): 
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False) 
 
# Initialize serial connection with retries 
def init_serial(): 
    max_attempts = 5 
    for attempt in range(max_attempts): 
        try: 
            ser = serial.Serial(serial_port, baud_rate, timeout=2) 
            print(f"Connected to {serial_port} at {baud_rate} baud") 
            time.sleep(2) 
            return ser 
        except serial.SerialException as e: 
            print(f"Serial error (attempt {attempt + 1}/{max_attempts}): {e}") 
            time.sleep(2) 
    print(f"Failed to connect to {serial_port} after {max_attempts} attempts") 
    sys.exit(1) 
 
# Initialize GPIO for buzzer 
GPIO.setmode(GPIO.BCM) 
GPIO.setup(BUZZER_PIN, GPIO.OUT) 
GPIO.output(BUZZER_PIN, False)  # Buzzer off initially 
 
# Start Flask in a separate thread 
flask_thread = threading.Thread(target=run_flask) 
flask_thread.daemon = True 
flask_thread.start() 
 
# Main program 
ser = init_serial() 
 
try: 
    cycle_index = 0 
    cycle_time = time.time() 
    while True: 
        # Read XIAO serial data 
        if ser and ser.in_waiting > 0: 
            line = ser.readline().decode('utf-8').strip() 
            if line.startswith("MQ135:"): 
                try: 
                    data = line.split(',') 
                    mq135_value = int(data[0].split(':')[1]) 
                    soil_percent = float(data[1].split(':')[1]) 
                except (IndexError, ValueError) as e: 
                    print(f"Error parsing serial: {e}") 
 
        # Read DHT22 
        try: 
            temp = dht_sensor.temperature 
            hum = dht_sensor.humidity 
            if temp is None or hum is None: 
                temp = temp or 0.0 
                hum = hum or 0.0 
        except RuntimeError as e: 
            print(f"DHT22 error: {e}") 
 
        # Check for high gas and trigger buzzer 
        current_time = time.time() 
        if mq135_value > GAS_THRESHOLD and current_time - last_buzzer_time > 
BUZZER_COOLDOWN: 
            print("High gas detected! Activating buzzer") 
            GPIO.output(BUZZER_PIN, True) 
            time.sleep(1)  # Buzz for 1 second 
            GPIO.output(BUZZER_PIN, False) 
            last_buzzer_time = current_time 
 
        # Cycle display every 3 seconds 
        if current_time - cycle_time > 3: 
            cycle_index += 1 
            cycle_time = current_time 
 
        # Print to terminal 
        print(f"MQ135 Raw: {mq135_value}, Soil: {soil_percent:.2f}%, Temp: 
{temp:.1f}C, Hum: {hum:.1f}%") 
 
        # Update OLED display 
        display_data(mq135_value, soil_percent, temp, hum, cycle_index) 
 
        # Wait before next reading 
        time.sleep(1) 
 
except KeyboardInterrupt: 
    print("Stopped by user") 
finally: 
    if ser and hasattr(ser, 'is_open') and ser.is_open: 
        ser.close() 
        print("Serial port closed") 
    dht_sensor.exit() 
    oled.fill(0) 
    oled.show() 
    GPIO.cleanup() 
    print("Cleaned up")