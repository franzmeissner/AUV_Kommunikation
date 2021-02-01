import alsaaudio as audio
import Adafruit_BBIO.ADC as ADC
import time

#Im Vorhinein empfiehlt es sich die jeweilig zu benutzen Soundkarte 
#als Default-Card anzulegen
# --> sudo nano /usr/share/alsa/alsa.conf
#nach unten scrollen
#defaults.ctl.card 1 <-- Index der zu verwenden Soundkarte eintragen
#defaults.pcm.card 1 <-- Index der zu verwenden Soundkarte eintragen

#Auflistung möglicher Soundkarten
scanCards = audio.cards()
print("Cards:", scanCards)

#Mixer für jeweilige Soundkarte
scanMixers = audio.mixers(cardindex=1)#Index anpassen, je nachdem welche Soundkarte angesprochen werden soll
print("Mixers:", scanMixers)

#Mixer Objekt
#Namen anpassen in Abhängigkeit von "scanMixers"
mixer_speaker = audio.Mixer('Speaker', cardindex=1)
mixer_mic = audio.Mixer('Mic', cardindex=1)
 

#ADC-Setup
ADC.setup()
analogPin1 = "P9_33"
analogPin2 = "P9_35"


while True:
 mic_level = round(ADC.read(analogPin1)*100)
 speaker_level = round(ADC.read(analogPin2)*100)
 #Mikrofon-Level in Alsa verändert, aber keine Änderung der Laustärke
 #-->Keine Ahnung wie dieses Problem behoben werden kann
 mixer_mic.setvolume(mic_level)
 #Änderung Lautstärke Kopfhörer funktioniert 
 mixer_speaker.setvolume(speaker_level)
 #Reaktionszeit Lautstärkeveränderungen Speaker/Mic --> je kleiner Sleep-time
 #desto schneller werden Laustärkeänderungen umgesetzt
 time.sleep(.2)
