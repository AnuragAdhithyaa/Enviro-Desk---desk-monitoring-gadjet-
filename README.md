# Enviro-Desk---desk-monitoring-gadjet-
Portable environmental monitoring device using Raspberry Pi 4 and Seeed XIAO to measure temperature, humidity, air quality, and soil moisture in real time. Features OLED display, LiPo power, compact design, and supports indoor and outdoor monitoring.
// Calibration values for soil moisture sensor
const int DRY_VALUE = 1023;  // ADC value when sensor is dry (0% moisture)
const int WET_VALUE = 0;     // ADC value when sensor is wet (100% moisture)

void setup() {
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial connection
  }
  // Set analog pins A0 (MQ135) and A1 (Soil Moisture) as inputs
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  // Preheat MQ135 for 30 seconds
  Serial.println("Preheating MQ135 for 30 seconds...");
  delay(30000); // 30 seconds
  Serial.println("Preheating complete");
}

void loop() {
  // Read analog values (0-1023)
  int mq135Value = analogRead(A0);
  int soilMoistureValue = analogRead(A1);
  
  // Convert soil moisture to percentage (0-100%)
  // Constrain to avoid values outside the calibration range
  int soilMoisturePercent = constrain(soilMoistureValue, WET_VALUE, DRY_VALUE);
  // Map to percentage (reversed: 1023 = 0%, 0 = 100%)
  float soilMoisturePercentFloat = map(soilMoisturePercent, DRY_VALUE, WET_VALUE, 0, 10000) / 100.0;
  
  // Send data over serial in a parseable format
  Serial.print("MQ135:");
  Serial.print(mq135Value); // Raw ADC value (0-1023)
  Serial.print(",SoilPercent:");
  Serial.println(soilMoisturePercentFloat, 2); // Percentage with 2 decimal places
  
  // Debug: Print raw values for calibration
  Serial.print("// Raw MQ135: ");
  Serial.print(mq135Value);
  Serial.print(", Raw Soil: ");
  Serial.println(soilMoistureValue);
  
  // Wait 1 second before next reading
  delay(1000);
}
