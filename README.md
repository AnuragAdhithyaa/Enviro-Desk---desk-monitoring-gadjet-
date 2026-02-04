In the present era, continuous monitoring of environmental conditions is essential for improving air quality, supporting agriculture, and enhancing human health. This project presents a portable environmental monitoring desk device that combines compact hardware, low power consumption, and real-time data visualization in a single, user-friendly system.

The device is built using a Raspberry Pi 4 and a Seeed Studio XIAO microcontroller, forming a hybrid embedded architecture that efficiently handles both digital processing and analog sensing. The XIAO board reads data from the MQ135 gas sensor and soil moisture sensor through its analog pins A0 and A1, while the DHT22 temperature and humidity sensor is directly interfaced with the Raspberry Pi via GPIO 4. This division of tasks ensures stable performance and accurate data acquisition.

All sensor values—temperature, humidity, air quality, and soil moisture—are displayed in real time on a 0.96-inch OLED screen, providing clear and immediate feedback to the user. The entire system is enclosed in a compact 12 × 9 × 4 cm housing and powered by a LiPo battery, making it lightweight, portable, and suitable for both indoor and outdoor environments.

Designed with simplicity, modularity, and cost efficiency in mind, this device demonstrates how small-scale embedded systems can deliver meaningful environmental insights without complex or expensive equipment. Its practical applications include indoor air-quality tracking, smart agriculture monitoring, and personal environmental awareness.

This project highlights the potential of compact IoT-based systems to transform raw sensor data into actionable information, encouraging smarter decisions through real-time monitoring and accessible technology.

Components Required:

1.	DHT22 Sensor 

2.	MQ135 Gas Sensor

3.	Soil Moisture Sensor

4.	OLED Display

5.	Raspberry pi 4

6.	Xiao Board SAMD21
