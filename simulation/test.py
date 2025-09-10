from gpiozero import PWMLED, Device
from gpiozero.pins.mock import MockFactory, MockPWMPin
from time import sleep

# pin_ mock p/ teste sem o rasp
Device.pin_factory = MockFactory(pin_class=MockPWMPin)

#led pwm atribuído ao pino gpio 18
led = PWMLED(18)


try:
    #loop que repete o loop interno até o keyboardinterrupt
    while True:
        #loop que aumenta a intensidade do led em 25% a cada iteração
        for i in range (0, 101, 25):
            led.value = i/100
            print(f"{led.value:.2f}", end = '\r')
            sleep(1)
        
except KeyboardInterrupt:
    print("\nPrograma finalizado.")
    led.value = 0
