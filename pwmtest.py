from gpiozero import PWMLED
from gpiozero.pins.mock import MockFactory, MockPWMPin
from time import sleep

# pin_ mock p/ teste em casa
#Device.pin_factory = MockFactory(pin_class=MockPWMPin)

led = PWMLED(18)

try:
    while True:

        for i in range (0, 101, 25):
            led.value = i/100
            print(f"{led.value:.2f}", end = '\r')
            sleep(1)
        

except KeyboardInterrupt:
    print("\nPrograma finalizado.")
    led.value = 0 