# Program to be uploaded on the Pico W
# This program combines two processes to be ran on the 2 cores of the Pico W via two threads
# Main thread: sends the requests to Google Sheets, hosts the frontend, controls the IoT of the alarm sound + email notification, and updates the PIR sensor values on the frontend
# Secondary thread: actively reads the fob/card placed in front of the MFRC522 module and checks against correctness of encoded 
import socket
import network
from machine import Pin
import time
import utime
from mfrc522 import SimpleMFRC522
import _thread
import urequests

# Sensor counter to count motion detections
counter = 0
# Input text to be read via radio frequency identification MFRC522 module
inputText = ""
# Boolean for incorrect Password attempts
incorrectPass = 0
# Set security password for the system
password = "SECURITY_PASSWORD"
# Initialize pins on Pico W
PIRSensor = Pin(14, Pin.IN)
buzzer = Pin(15, Pin.OUT)
reader = SimpleMFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=5,rst=0)
sdi = Pin(18, Pin.OUT)
rclk = Pin(19, Pin.OUT)
srclk = Pin(20, Pin.OUT)
# For the 8x8 matrix graphic display. 
# Pico needs a 16 bit binary number the first 8 bits are given to the 74HC595 which controls the rows,
# and the last 8 bits are given to the 75HC595 which controls the columns, so that the dot matrix can display a specific pattern.
checkmark = [0xFF,0xFF,0xF7,0xEB,0xDF,0xBF,0xFF,0xFF]
x = [0xFF,0xBB,0xD7,0xEF,0xD7,0xBB,0xFF,0xFF]
# IFTTT Applets are used to log information to Google Sheet and send email notifications
server = 'maker.ifttt.com'

# Increments Passenger count when PIR sensor sends an interrupt request
def motionDetected(pin):
    global counter
    counter = counter + 1
# Sends a POST request to the applet URL to log incorrect password attempt
def logToGoogleSheets():
    IFTTT_URL = '/trigger/IncorrectPasswordAttempts/with/key/jo28QVc_9-SuWNm3CVwjfhrxBIsa0aSuX6Nt6aQdbu_'
    print('Connecting to', server)
    # value1 is the timestamp, value2 is the incorrect password provided
    json_data = '{"value1":"' + str(time.time()) + '","value2":"' + inputText + '"}'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post('https://' + server + IFTTT_URL, data=json_data, headers=headers)
    print('Response:', response.content.decode())
    response.close()
    print('Closing Connection')
# Sends a POST request to the applet URL to send an email notification with the link to the google sheets after alarm has been sounded
def sendEmailAlert():
    IFTTT_URL = '/trigger/Send_Alert_Email/with/key/jo28QVc_9-SuWNm3CVwjfhrxBIsa0aSuX6Nt6aQdbu_'
    print('Connecting to', server)
    headers = {'Content-Type': 'application/json'}
    response = urequests.post('https://' + server + IFTTT_URL, headers=headers)
    print('Response:', response.content.decode())
    response.close()
    print('Closing Connection')
# Writes values to the 8 bit shift register 75HC595 input
# When MR (pin10) is high level and OE (pin13) is low level, data is input in the rising edge of SHcp (srclk) and goes to the memory register through the rising edge of SHcp.
def hc595In(dat):
    for bit in range(7,-1, -1):
        srclk.low()
        time.sleep_us(30)
        sdi.value(1 & (dat >> bit))
        time.sleep_us(30)
        srclk.high()
# Controls output of 75HC595
# When OE is enabled (low level), the data in memory register is output to the bus(Q0 ~ Q7).
def hc595Out():
    rclk.high()
    time.sleep_us(200)
    rclk.low()
# Updates HTML displayed PIR sensor value
def getHTML(html_name):
    # open html_name (index.html), 'r' = read-only as variable 'file'
    with open(html_name, 'r') as file:
        html = file.read()
    # update counter value
    content = html.replace(
        "<h2 id=\"passenger\"></h2>", f"<h2 id=\"passenger\"> {counter}</h2>")
    return content
# Uses MFRC522 module to read the card/fob
def read():
    global reader
    print("Reading...Please place the card...")
    global inputText
    id, inputText = reader.read()
    print("ID: %s\nText: %s" % (id,inputText))
# Set up the PIR sensor interrupt request handler to call motionDetected()
PIRSensor.irq(trigger=Pin.IRQ_RISING, handler=motionDetected)
# Setup connection with local Wi-Fi network for Pico W remote connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("NETWORK_NAME","NETWORK_PASSWORD")
sta_if = network.WLAN(network.STA_IF)
# Prints IP address Pico W is connected on
print(sta_if.ifconfig()[0])
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
# Sets up web socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
# Start of main processes

# Reads SimpleMFRC522 card/fob input and displays result on 8x8 matrix, keeps it on for 80 iterations
def secondTask():
    while True:
        seconds = 0
        print("Ready to read RFID")
        read()
        print(inputText)
        global incorrectPass
        # the LEDs in the dot matrix use common poles, so controlling multiple rows/multiple columns at the same time will interfere with each other
        # (e.g., if you light up (1,1) and (2,2) at the same time, (1,2) and (2,1) will be lit up together). 
        # Therefore, it is necessary to activate one column (or one row) at a time, cycle 8 times, and use the residual image principle to make the human eye merge 8 patterns, so as to get a pair of patterns containing 8x8 amount of information.
        while (password in inputText and iteration <=80):
            incorrectPass = 0
            # when i is 1, only the first line is activated (the chip in the control line gets the value 0x80 ) and the image of the first line is written. 
            # When i is 2, the second line is activated (the chip of the control line gets the value 0x40) and the image of the second line is written. 
            # And so on, completing 8 outputs.
            # hc595In is called twice since we have a 16 bit binary value, one registers controls columns and the other rows.
            for i in range(0,8):
                hc595In(checkmark[i])
                hc595In(0x80>>i)
                hc595Out()
            iteration+=1
        while (password not in inputText and iteration <=80):
            incorrectPass = 1
            for i in range(0,8):
                hc595In(x[i])
                hc595In(0x80>>i)
                hc595Out()
            iteration+=1
        incorrectPass = 0
# Start secondary thread
_thread.start_new_thread(secondTask, ())

# Main thread begins
# Listen for connections/requests to the web server
while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024)
        # Stringify request to search for URL parameters
        request = str(request)
        response = getHTML('index.html')
        # If request sent through Ajax contains /data, return the value of counter of the PIR sensor. 
        # If user clicked on alarm on button, loop alarm sound for 2 loops (modifiable) + send email alert of password logs
        if (request.find('/data') > -1):
            response = str(counter)
        elif (request.find('/alarm=on') > -1):
            for i in range(2):
                buzzer.value(1)
                utime.sleep(0.3)
                buzzer.value(0)
                utime.sleep(0.3)
            sendEmailAlert()
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
    except OSError as e:
        cl.close()
        print('Connection closed')
    # If there's been an incorrect password attempt from the second thread, log it to google sheets
    if (incorrectPass ==1):
        logToGoogleSheets()
        # More for debugging purposes to see last log sent
        last_message = time.time()
        print(last_message)
    


