import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime
import threading
import os

# MACROS para o programa
PWM_PIN = 18 # Pino de saída (BCM mode)
PIN_TRIG = 23 # Pino para enviar o pulso de ativação
PIN_ECHO = 24 # Pino para ler o pulso de retorno



GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)


sens_value = 0.0                    # Variável para IO (coleta dos valores do sensor, leitura pelo LED, e leitura pelo escritoor de log)
mutex_sens = threading.Lock()       # Cria um mutex para a variavel mutex_sens

filename = datetime.now().strftime("log/log_%Y%m%d_%H%M%S.csv")
# Cria o CSV e escreve cabeçalho


# Função para medir a distância
def get_distance():
    """
    Mede a distância usando o sensor HC-SR04.
    Retorna a distância em centímetros.
    """
   
    # Envia um pulso de 10 microssegundos para ativar o sensor
    GPIO.output(PIN_TRIG, True)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIG, False)

    # Mede o tempo de viagem da onda
    # O pino ECHO irá para HIGH quando o pulso for enviado.
    # start_time registra o momento em que isso acontece.
    start_time = time.time()
    while GPIO.input(PIN_ECHO) == 0:
        start_time = time.time()
    
    # O pino ECHO voltará para LOW quando a onda retornar.
    # end_time registra o momento em que isso acontece.
    end_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        end_time = time.time()

    # Calcula a duração do pulso
    pulse_duration = end_time - start_time

    # Calcula a distância
    # A velocidade do som é 34300 cm/s.
    # A distância é a metade do tempo de viagem.
    distance = (pulse_duration * 34300) / 2
    
    return round(distance, 2)

def gpioPWM_ledControl():
    print(f"Thread para controle do LED iniciada com ID: {threading.get_ident()}")
    GPIO.setup(PWM_PIN, GPIO.OUT)   # Usando o pino PWM_PIN para o LED
    pwm = GPIO.PWM(PWM_PIN, 1000)   # Configura o PWM na frequência de 1kHz
    pwm.start(0)                    # Inicia o PWM com 0% de duty cycle (LED apagado)

    global sens_value
    local_var = 0.0
    while True:
        with mutex_sens:
            local_var = sens_value
        
        if(local_var<0):
            print("error in reading: reading less than 0")
        elif(local_var>100):
            print("distance read more than 100, get closer to the sensor")
            local_var = 100
        else:
            print(f"Distance: {local_var} cm - LED bright in: {local_var}%")
        pwm.ChangeDutyCycle(local_var)  # Ajusta o brilho do LED com base na distância
                
        time.sleep(0.1) # Para segurar o excesso de leituras                 RETIRAR
        agora = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        try:
            with open(filename, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([agora, f"{local_var:.2f}"])
        except Exception as e:
            print(f"[LED thread] Erro ao escrever no arquivo: {e}")

# Contagem aleatória
def readSonicSensor():
    print(f"Thread de leitura do sensor ultrassônico iniciada com ID: {threading.get_ident()}\n\tPorta Trigger: {PIN_TRIG}\n\tPorta Echo: {PIN_ECHO}")
    GPIO.setup(PIN_TRIG, GPIO.OUT) # Configura o pino do Trigger como saída
    GPIO.setup(PIN_ECHO, GPIO.IN)  # Configura o pino do Echo como entrada
     # Garante que o pino TRIG está em LOW (desligado) no início
    GPIO.output(PIN_TRIG, False)
    time.sleep(2) # Pausa de 2 segundos para o sensor se estabilizar

    global sens_value
    local_var = 0.0
    try:
        while True:
            try:
                local_var = get_distance()
                with mutex_sens:
                    sens_value = local_var # Em centimetros
            except Exception as e:
                print(f"[Sensor thread] Erro ao medir distância: {e}")
    except Exception as e:
        print(f"[Sensor thread] Exceção: {e}")


    
    time.sleep(0.5) # Aguarda meio segundo antes da próxima leitura
      

def main():

    try:
        os.makedirs("log", exist_ok=True)
        
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["time", "wrote"])

        print(f"Processo principal PID: {os.getpid()}") # Exibe o PID do processo principal
        # Cria threads para executar as funções simultaneamente
        thread1 = threading.Thread(target=gpioPWM_ledControl)
        thread2 = threading.Thread(target=readSonicSensor)
        # Inicia as threads
        thread1.start()
        thread2.start()
        # Aguarda a conclusão das threads
        thread1.join()
        thread2.join()
        
    except KeyboardInterrupt:
        print("Interrompido pelo usuário.")
    except Exception as e:
        print(f"[Main] Erro: {e}")
    finally:
        GPIO.cleanup()



# inicio do programa
if __name__ == '__main__':
    main()