"""
F1: Ein Sensor zur Erfassung von Luftfeuchtigkeit
    soll konstant die Luft- feuchtigkeit messen.
    
F2: Ein Temperatursensor soll konstant die Innenraumtemperatur ermitteln.

F3: Wird der Temperaturschwellenwert von 30°C überschritten, soll ein ventilator
    eingeschaltet werden, bis die Temperatur wieder unter 23°C gesunken.
    
Störmeldungen:   
F4: Ist die Temperatur außer Norm, soll eine Warnung angezeigt werden.   
 
"""

import machine
import esp32
from machine import Pin, SoftI2C, ADC, PWM
from time import sleep
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import dht

""" Feuchtigkeitssensor einrichten"""
eingang = Pin(17, Pin.IN)
sensor = dht.DHT11(eingang)

""" LCD einrichten """
# LCD Speicheradresse und Größenangabe des Bildschirms
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
# I2C mit Pins und gegebener Taktung
i2c = SoftI2C(scl = Pin(22), sda = Pin(21), freq = 10000)
# LCD-Monitor
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

""" Pin-Belegungen für den DC-Motor """
# Geschwindigkeit des Motors
en = Pin(26, Pin.OUT)
leistung = PWM(en, freq=800, duty_u16=0)
#leistung.init(freq=5000, duty_ns=5000)
# Drehrichtung des Motors
in1 = Pin(33, Pin.OUT)
in2 = Pin(25, Pin.OUT)
# Zu Programmbeginn ist der Motor aus
in1.off()
in2.off()

""" Funktionen """
# Funktion Motorstart
def start(pwm, x, y):
    pwm.duty_u16(int(0.9 * 65535))
    x.on()
    y.off()
# Funktion Motorende
def stop(x, y):
    x.on()
    y.on()
# Funktion Anzeige
def anzeige(lcd, temp, feuchte):
    lcd.putstr("Temp: " + str(temp) + " °C\n")
    lcd.putstr("Hum: " + str(feuchte) + "%" )
    
""" Programmdurchlauf in Dauerschleife """
PAUSE = 0.5
while True:
    lcd.clear()
    # Sensor aktivieren
    sensor.measure()
    # Temperatur in °C
    temperatur = sensor.temperature()
    # Luftfeuchtigkeit in % RH
    feuchtigkeit = sensor.humidity()
    
    # Temperatur zu hoch (Warnhinweis). Ventilator aktiviert
    if temperatur > 30:
        start(leistung, in1, in2)
        lcd.putstr("Over 30! ")
    # Anzeige der Phase zwischen Sollwert und kritischem Wert    
    if temperatur > 23 and temperatur <= 30:
        lcd.putstr("Warning")
        
    # Temperatur im Sollbereich. Ventilator deaktiviert    
    if temperatur < 23:
        stop(in1, in2)
        anzeige(lcd, temperatur, feuchtigkeit)
        
    sleep(PAUSE)
    



