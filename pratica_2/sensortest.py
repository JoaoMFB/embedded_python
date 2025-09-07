from gpiozero import DistanceSensor, PWMLED
from signal import pause



# def atualizar_brilho():
#     if sensor.distance >= 0.02 and sensor.distance < 0.25:
#         led.value = 0.25
#     elif sensor.distance >= 0.25 and sensor.distance < 0.5:
#         led.value = 0.5
#     elif sensor.distance >= 0.5 and sensor.distance < 1:
#         led.value = 0.75
#     elif sensor.distance >= 1 and sensor.distance < 4:
#         led.value = 1
#     else:
#         led.value = 0

sensor = DistanceSensor(echo = 24, trigger = 23)
led = PWMLED(18)

led.source = sensor.values

pause()