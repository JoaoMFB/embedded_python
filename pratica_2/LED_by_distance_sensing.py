import RPi.GPIO as GPIO
import threading
import time

# --- Configuração dos Pinos ---
# Use o modo BCM para referenciar os pinos pelo número GPIO.
PIN_TRIG = 23
PIN_ECHO = 24
PIN_LED = 18

GPIO.setmode(GPIO.BCM)

# --- Variáveis Globais e Sincronização ---
# Variavel global para armazenar a distância em centímetros.
distance_value = 0.0

# Mutex para proteger a variável global.
mutex_distance = threading.Lock()

# --- Configuração dos Componentes ---
GPIO.setup(PIN_TRIG, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.setup(PIN_LED, GPIO.OUT)

# Configura o PWM do LED. A frequência de 100 Hz é uma boa escolha.
pwm_led = GPIO.PWM(PIN_LED, 100)
pwm_led.start(0)  # Inicia o PWM com 0% de ciclo de trabalho (LED apagado)

# --- Thread 1: Leitura do Sensor ---
def read_sensor_thread():
    """
    Thread responsável por ler o sensor HC-SR04 continuamente.
    """
    print("Thread de leitura do sensor iniciada.")
    global distance_value
    
    # Garante que o pino TRIG está em LOW no início para estabilizar.
    GPIO.output(PIN_TRIG, False)
    time.sleep(2) 

    while True:
        # Envia um pulso de 10 microssegundos.
        GPIO.output(PIN_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIG, False)

        # Mede o tempo de viagem da onda.
        start_time = time.time()
        while GPIO.input(PIN_ECHO) == 0:
            start_time = time.time()
        
        end_time = time.time()
        while GPIO.input(PIN_ECHO) == 1:
            end_time = time.time()

        pulse_duration = end_time - start_time
        
        # Calcula a distância em centímetros.
        distance = (pulse_duration * 34300) / 2
        
        # Protege a variável compartilhada com o mutex.
        with mutex_distance:
            distance_value = distance
            
        # Pequena pausa para liberar o processador.
        time.sleep(0.1)


# --- Thread 2: Controle do LED ---
def control_led_thread():
    """
    Thread responsável por controlar o brilho do LED com base na distância.
    """
    print("Thread de controle do LED iniciada.")
    global distance_value
    
    while True:
        local_distance = 0.0
        
        # Lê a variável compartilhada com o mutex.
        with mutex_distance:
            local_distance = distance_value

        # Mapeia a distância (em cm) para o ciclo de trabalho do PWM (0 a 100).
        # Vamos usar um mapeamento simples:
        # 0 cm a 100 cm -> 100% a 0% de brilho (inversamente proporcional).
        if local_distance >= 100:
            duty_cycle = 0  # LED apagado para distâncias maiores que 1 metro.
        elif local_distance <= 0:
            duty_cycle = 100  # LED com brilho máximo para distâncias menores ou iguais a 0.
        else:
            # Mapeamento linear de 100cm para 0cm.
            duty_cycle = 100 - local_distance

        # Ajusta o brilho do LED.
        pwm_led.ChangeDutyCycle(duty_cycle)
        
        print(f"Distância: {local_distance:.2f} cm - Brilho do LED: {duty_cycle:.2f}%")

        # Pequena pausa para evitar sobrecarregar a CPU.
        time.sleep(0.05)


# --- Função Principal ---
def main():
    """
    Cria e inicia as threads.
    """
    try:
        # Cria as threads.
        thread_sensor = threading.Thread(target=read_sensor_thread)
        thread_led = threading.Thread(target=control_led_thread)

        # Inicia as threads.
        thread_sensor.start()
        thread_led.start()

        # Espera as threads terminarem.
        thread_sensor.join()
        thread_led.join()

    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário.")
    finally:
        # Limpa os pinos GPIO.
        pwm_led.stop()  # Para o PWM antes de limpar.
        GPIO.cleanup()
        print("GPIO limpo.")


if __name__ == '__main__':
    main()