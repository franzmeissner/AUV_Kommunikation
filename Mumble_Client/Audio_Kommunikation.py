#!/usr/bin/python3
import  pymumble_py3
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED as PCS
import pyaudio
import Adafruit_BBIO.GPIO as GPIO

# Connection details for mumble server. Hardcoded for now, will have to be
# command line arguments eventually
pwd = ""  # password
server = "192.168.43.150"  # server address
nick = "BeagleBone_Green"
port = 64738 # port number

# pyaudio set up
CHUNK = 1024
FORMAT = pyaudio.paInt16  # pymumble soundchunk.pcm is 16 bits
CHANNELS = 1
RATE = 48000  # pymumble soundchunk.pcm is 48000Hz



p = pyaudio.PyAudio()
print(p.get_default_host_api_info())
stream_in = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True, 
                input_device_index=1,
                frames_per_buffer=CHUNK)

stream_out = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                output_device_index=1,
                frames_per_buffer=CHUNK)

#GPIO-Setup Input
GPIO.setup("P8_30", GPIO.IN) #Push-to-talk externer Taster
GPIO.setup("P8_8",GPIO.IN) #Verbindung zu Server herstellen
GPIO.setup("P8_10", GPIO.IN) #nur Hören
GPIO.setup("P8_7", GPIO.IN) #Push-to-talk
GPIO.setup("P8_9", GPIO.IN) #dauerhaft Hören und Sprechen
GPIO.setup("P8_29", GPIO.IN) #manuelle Serververbindung

#GPIO-Setup Output
GPIO.setup("P9_23", GPIO.OUT) #LED nur Hören
GPIO.setup("P9_25", GPIO.OUT) #LED Push-to-talk
GPIO.setup("P9_29", GPIO.OUT) #LED dauerhaft Hören und Sprechen
GPIO.setup("P8_34", GPIO.OUT) #zu Server verbunden/EIN
GPIO.setup("P8_36", GPIO.OUT) #nicht zu Server verbunden/AUS

# mumble client set up
def sound_received_handler(user, soundchunk):
   # """ play sound received from mumble server upon its arrival """
    	stream_out.write(soundchunk.pcm)


server_connect = 0 #Hilfsvariable für Serverstatus

#Anfangsbedingung EIN/AUS (Serververbindung abfragen)
if not GPIO.input("P8_29"):
  GPIO.output("P8_34", GPIO.HIGH)
  GPIO.output("P8_36", GPIO.LOW)
  mumble = pymumble_py3.Mumble(server, nick, password=pwd, port=port)
  mumble.callbacks.set_callback(PCS, sound_received_handler)
  mumble.set_receive_sound(1)  # Enable receiving sound from mumble server
  mumble.start() #Verbindung wird zu Server wird gestartet
  mumble.is_ready()  #Verbindung hergestellt
  #Start-Nachricht 
  mumble.channels[0].send_text_message("Bellypack is Ready")
  server_connect = 1
else:
  GPIO.output("P8_34", GPIO.LOW)
  GPIO.output("P8_36", GPIO.HIGH)
  server_connect = 0


while True :
 if server_connect == 1:
    if GPIO.input("P8_10"):
      GPIO.output("P9_23", GPIO.HIGH)
      GPIO.output("P9_25", GPIO.LOW)
      GPIO.output("P9_29", GPIO.LOW)
      while True and not GPIO.input("P8_8") and not GPIO.input("P8_10") and not GPIO.input("P8_7") and not GPIO.input("P8_9")  and server_connect == 1:   
       if GPIO.input("P8_29"):
        GPIO.output("P9_23", GPIO.LOW)
        GPIO.output("P9_25", GPIO.LOW)
        GPIO.output("P9_29", GPIO.LOW)
        GPIO.output("P8_34", GPIO.LOW)
        GPIO.output("P8_36", GPIO.HIGH)
        server_connect = 0
        mumble.stop()
       
#Modus: Push-to-talk
    elif GPIO.input("P8_7"): 
     GPIO.output("P9_23", GPIO.LOW)
     GPIO.output("P9_25", GPIO.HIGH)
     GPIO.output("P9_29", GPIO.LOW)
     while True and not GPIO.input("P8_8") and  not GPIO.input("P8_9") and not GPIO.input("P8_10") and not GPIO.input("P8_8") and server_connect == 1:
      if not GPIO.input("P8_29"):
        if GPIO.input("P8_30"):
         data = stream_in.read(CHUNK, exception_on_overflow=False)
         mumble.sound_output.add_sound(data)
      else:
       GPIO.output("P9_23", GPIO.LOW)
       GPIO.output("P9_25", GPIO.LOW)
       GPIO.output("P9_29", GPIO.LOW)
       GPIO.output("P8_34", GPIO.LOW)
       GPIO.output("P8_36", GPIO.HIGH)
       server_connect = 0
       mumble.stop()
        
#Modus: Dauerhaft Sprechen
    elif GPIO.input("P8_9"):
     GPIO.output("P9_23", GPIO.LOW)
     GPIO.output("P9_25", GPIO.LOW)
     GPIO.output("P9_29", GPIO.HIGH)
     while True and not GPIO.input("P8_8")  and not GPIO.input("P8_7") and not GPIO.input("P8_10") and not GPIO.input("P8_8") and server_connect == 1: 
      if not GPIO.input("P8_29"):
       data = stream_in.read(CHUNK, exception_on_overflow=False)
       mumble.sound_output.add_sound(data)
      else:      
       GPIO.output("P9_23", GPIO.LOW)
       GPIO.output("P9_25", GPIO.LOW)
       GPIO.output("P9_29", GPIO.LOW)
       GPIO.output("P8_34", GPIO.LOW)
       GPIO.output("P8_36", GPIO.HIGH)
       server_connect = 0
       mumble.stop()

#Modus Platzhalter, kann beliebig belegt werden
    else:
     GPIO.output("P9_23", GPIO.HIGH)
     GPIO.output("P9_25", GPIO.HIGH)
     GPIO.output("P9_29", GPIO.HIGH)
     while True and not GPIO.input("P8_7") and not GPIO.input("P8_9") and not GPIO. input("P8_10") and server_connect == 1:
      if GPIO.input("P8_29"):
       GPIO.output("P9_23", GPIO.LOW)
       GPIO.output("P9_25", GPIO.LOW)
       GPIO.output("P9_29", GPIO.LOW)
       GPIO.output("P8_34", GPIO.LOW)
       GPIO.output("P8_36", GPIO.HIGH)
       server_connect = 0
       mumble.stop()
      
#Server neu verbinden
 elif server_connect== 0:
  while True and server_connect == 0:
   if not GPIO.input("P8_29"):
    mumble = pymumble_py3.Mumble(server, nick, password=pwd, port=port)
    mumble.callbacks.set_callback(PCS, sound_received_handler)
    mumble.set_receive_sound(1)  # Enable receiving sound from mumble server
    mumble.start() #Verbindung wird zu Server wird gestartet
    mumble.is_ready()  #Verbindung hergestellt
    mumble.channels[0].send_text_message("Bellypack is Ready")   
    GPIO.output("P8_34", GPIO.HIGH)
    GPIO.output("P8_36", GPIO.LOW)
    server_connect = 1




