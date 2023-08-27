# secure-pass-guard
A multi-disciplinary password anomaly detection, alarm, and logging system. 
Tools: MicroPython, multi-threaded/multi-core programming on Raspberry Pi Pico with ESP8266 for Wi-Fi connectivity, sensor data logging through Google Sheets and email notifications with IFTTT Applets
- Main thread: sends the requests to Google Sheets, hosts the frontend, controls the IoT of the alarm sound + email notification, and updates the PIR sensor values on the frontend
- Secondary thread: actively reads the fob/card placed in front of the MFRC522 module and checks against correctness of encoded password 

## Components 
- Raspberry Pi Pico
- ESP8266 module
- MFRC522 Radio Frequency Identification Module
- 8x8 matrix pixel display
- 2 75HC595 ICs (8 bit shift registers + memory register)
- S8050 NPN transistor
- Active buzzer 
### Schematics
#### 75HC595 IC
<img width="322" alt="image" src="https://github.com/rana-balabel/secure-pass-guard/assets/78990245/d5f0f51b-6702-48b2-ac7e-d21cecb18868"> <br>
#### 8x8 Matrix Pixel Display
<img width="588" alt="image" src="https://github.com/rana-balabel/secure-pass-guard/assets/78990245/1e92d7c9-f45e-4c23-8cc5-5f3957b1fefa"> <br>
- For the 8x8 matrix graphic display, the Pico needs a 16 bit binary number. The first 8 bits are given to the 74HC595 which controls the rows, and the last 8 bits are given to the 75HC595 which controls the columns, so that the dot matrix can display a specific pattern.
The code writes values to the 8 bit shift register 75HC595 input when MR (pin10) is HIGH and OE (pin13) is LOW. The data is input in the rising edge of SHcp (srclk variable name in code), and goes to the memory register through the rising edge of SHcp.
The output of the register happens when OE is enabled (LOW). The data in the memory register is output to the bus(Q0 ~ Q7). This happens in each of the 75HC595 on the circuit, producing a 16 bit output.
#### PIR Sensor
<img width="289" alt="image" src="https://github.com/rana-balabel/secure-pass-guard/assets/78990245/74600007-8a9b-4788-9a8d-c5a54c8b5f5b"> <br>
- When the PIR module detects someone passing by, GP14 will be HIGH, else it will be LOW.
The PIR module has two potentiometers: one adjusts sensitivity, the other adjusts detection distance. To make the PIR module work better, you need to turn both of them counterclockwise to the end.
#### MFRC522 Module + Active Buzzer 
<img width="328" alt="image" src="https://github.com/rana-balabel/secure-pass-guard/assets/78990245/c5bbd705-b2ab-45b2-8755-4a208bc12232"> <br>
- The MFRC5222 microchip manages communication with the reader via radio frequency (RF).
When the GP15 output is high, after the 1K current limiting resistor (used to protect the transistor), the S8050 (NPN transistor) will conduct, and the buzzer will sound.
The role of the transistor is to amplify the current and make the buzzer sound louder.

## Capabilities
### User View
<img width="1023" alt="image" src="https://github.com/rana-balabel/secure-pass-guard/assets/78990245/b5d9cc3e-6e28-4cfb-83bf-f168342a112d"> <br>
### Demo & Setup
- To setup the environment, install the Thonny IDE and upload the latest firmware of the Raspberry Pi Pico from the [Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- Select the MicroPython language in the interpretor and run the [main.py]() after setting up the circuit. Ensure the dependencies (SimpleMFRC522 module, for ex.) are installed on the Pico beforehand.
- Copy over the [index.html]() and required JavaScript [js/alarm.js]. The CSS and remaining files are optional and only used for styling.
- View the demo through this [Google Drive link](https://drive.google.com/file/d/1BywcW-gau7x6p4sAKkLqN3-PGKrpZqSf/view?usp=sharing) <br>
 
