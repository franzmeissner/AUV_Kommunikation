
import pymumble_py3
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED as PCS
import pyaudio

# Connection details for mumble server. Hardcoded for now, will have to be
# command line arguments eventually
pwd = ""  # password
server = "192.168.1.194"  # server address
nick = "Bellypack"
port = 64738  # port number -> Mumble-Server läuft Standardmäßig auf diesem Port (kann geändert werden)


# pyaudio set up
CHUNK = 4096
FORMAT = pyaudio.paInt16  # pymumble soundchunk.pcm is 16 bits
CHANNELS = 1
RATE = 48000  # pymumble soundchunk.pcm is 48000Hz

p = pyaudio.PyAudio()
stream_in = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index = 0, #-> Index jeweiliger Soundkarte auswählen
                frames_per_buffer=CHUNK)

stream_out =  p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                output_device_index=0, #-> Index jeweiliger Soundkarte auswählen
                frames_per_buffer=CHUNK)


# mumble client set up
def sound_received_handler(user, soundchunk):
    """ play sound received from mumble server upon its arrival """
    stream_out.write(soundchunk.pcm)


# Spin up a client and connect to mumble server
mumble = pymumble_py3.Mumble(server, nick, password=pwd, port=port)
# set up callback called when PCS event occurs
mumble.callbacks.set_callback(PCS, sound_received_handler)
mumble.set_receive_sound(1)  # Enable receiving sound from mumble server
mumble.start()
mumble.is_ready()  # Wait for client is ready


# constant capturing sound and sending it to mumble server
while True:
    data = stream_in.read(CHUNK, exception_on_overflow=False)
    mumble.sound_output.add_sound(data)


# close the stream and pyaudio instance
stream.stop_stream()
stream.close()
p.terminate()
