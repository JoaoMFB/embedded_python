from gpiozero import DistanceSensor, PWMLED
from signal import pause
import time
 
sensor = DistanceSensor(echo = 24, trigger = 23)

led = PWMLED(18)

while(True):
    print(sensor.values)
    led.source = sensor.values
    time.sleep(0.5)

# led.source = sensor.values

# pause()