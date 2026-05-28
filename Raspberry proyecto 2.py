from machine import ADC, Pin, PWM
import time


numeros_segmento = {"0" : [0,1,1,1,1,1,1], "1" : [0,0,0,1,0,0,1], "2" : [1,0,1,1,1,1,0], "3" : [1,0,1,1,0,1,1], "4" : [1,1,0,1,0,0,1], "5" : [1,1,1,0,0,1,1], "6" : [1,1,1,0,1,1,1], "7" : [0,0,1,1,0,0,1]}

lista_productos = [0,2,5]

servo = Pin(21, Pin.OUT)
potenciometro = ADC(Pin(26))
led1 = Pin(16, Pin.OUT)
led2 = Pin(17, Pin.OUT)
boton = Pin(10, Pin.IN, Pin.PULL_DOWN)
segmento0 = Pin(15, Pin.OUT)
segmento1 = Pin(14, Pin.OUT)
segmento2 = Pin(13, Pin.OUT)
segmento3 = Pin(12, Pin.OUT)
segmento4 = Pin(18, Pin.OUT)
segmento5 = Pin(19, Pin.OUT)
segmento6 = Pin(20, Pin.OUT)

diccionario_segmentos = {"segmento0" : segmento0, "segmento1" : segmento1, "segmento2" : segmento2, "segmento3" : segmento3, "segmento4" : segmento4, "segmento5" : segmento5, "segmento6" : segmento6}


# Set up PWM Pin for servo control
servo_pin = machine.Pin(27)
servo = PWM(servo_pin)

# Set Duty Cycle for Different Angles
max_duty = 6800
min_duty = 2000
half_duty = 4700

#Set PWM frequency
frequency = 50
servo.freq (frequency)

def mostrar_cantidad_productos(producto):
    numero = numeros_segmento[str(lista_productos[producto])]
    for x in range(7):
        diccionario_segmentos["segmento" + str(x)].value(numero[x])
    

while True:
    adc_value = potenciometro.read_u16()
    if adc_value > 50000:
        print("0")
        producto = 0
    elif 20000 < adc_value < 50000:
        print("medio")
        producto = 1
    else:
        print("alto")
        producto = 2
    if lista_productos[producto] == 0:
        led1.value(1)
        led2.value(0)
    else:
        led1.value(0)
        led2.value(1)
    mostrar_cantidad_productos(producto)
    if boton.value() == 1 and lista_productos[producto] > 0:
        lista_productos[producto] = lista_productos[producto] - 1
        print("hola")
        servo.duty_u16(min_duty)
        time.sleep(2)
        servo.duty_u16(half_duty)
    time.sleep(0.1)
