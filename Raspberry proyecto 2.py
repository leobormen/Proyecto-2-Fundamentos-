import network
import socket
import select 
from machine import ADC, Pin, PWM
import time

#Configuracion inicial de la conexion WiFi
SSID = "RedSanti" #No debe tener caracteres especiales
PASSWORD = "ce1234ce"
PORT = 1717
cliente_sock = None #Definir el sock del cliente

#Lista_Productos
lista_productos = [0,0,0]
lista_stats = [0,0,0]

#Pines 
potenciometro = ADC(Pin(26))
led_rojo = Pin(16, Pin.OUT)
led_verde = Pin(17, Pin.OUT)
led_azul = Pin(1, Pin.OUT)
led_azul.value(1)
boton = Pin(10, Pin.IN, Pin.PULL_DOWN)


#7 Segmentos

# Pines 7 Segmentos	
segmento0 = Pin(15, Pin.OUT)
segmento1 = Pin(14, Pin.OUT)
segmento2 = Pin(13, Pin.OUT)
segmento3 = Pin(12, Pin.OUT)
segmento4 = Pin(18, Pin.OUT)
segmento5 = Pin(19, Pin.OUT)
segmento6 = Pin(20, Pin.OUT)

#Diccionario Pines del 7 segmentos
diccionario_segmentos = {"segmento0" : segmento0, "segmento1" : segmento1, "segmento2" : segmento2, "segmento3" : segmento3, "segmento4" : segmento4, "segmento5" : segmento5, "segmento6" : segmento6}

#Numeros del Segumento
numeros_segmento = {"0" : [0,1,1,1,1,1,1], "1" : [0,0,0,1,0,0,1], "2" : [1,0,1,1,1,1,0], "3" : [1,0,1,1,0,1,1], "4" : [1,1,0,1,0,0,1], "5" : [1,1,1,0,0,1,1], "6" : [1,1,1,0,1,1,1], "7" : [0,0,1,1,0,0,1], "8" : [1,1,1,1,1,1,1], "9" : [1,1,1,1,0,1,1] }


# Servo Motor 
servo = PWM(Pin(0))
frequency = 50
servo.freq(frequency)

# Set Duty Cycle for Different Angles
max_duty = 6800
min_duty = 2000
half_duty = 4700


# Modos de la maquina
modo_ventas = False
modo_mantenimiento = False 

# Funciones de la maquina

def mostrar_cantidad_productos(producto):
    global lista_productos 
    numero = numeros_segmento[str(lista_productos[producto])]
    for x in range(7):
        diccionario_segmentos["segmento" + str(x)].value(numero[x])
        
def apagar_7segmentos():
    for x in range(7):
        diccionario_segmentos["segmento" + str(x)].value(0) #Para cada segmento , el valor sera 0
#Funcion para detener ejecucion
        
def iniciar_mantenimiento():
     global modo_ventas, modo_mantenimiento, servo, led_azul, led_verde, led_rojo
     modo_ventas = False
     modo_mantenimiento = True
     servo.duty_u16(min_duty)
     led_azul.value(1)
     led_verde.value(0)
     led_rojo.value(0)
     apagar_7segmentos()

# Conexion WiFi 

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConectado:", wlan.ifconfig())
    return wlan.ifconfig()[0]

def iniciar_servidor_async(ip):
    #Esta funcion la tome del proyecto de StrangerTEC

    s = socket.socket() #Crea un socket, en este caso para la conexion asincrona

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Permite reusar el puerto si la rasperry se desconecta

    s.bind((ip, PORT)) #Le asocia la ip y el puerto al socket creado
    s.listen(1) #Significa que escuchará solo un mensaje a la vez
 
    poller = select.poll() #Crea un poller
    poller.register(s, select.POLLIN) #POLLIN revisa si hay un mensaje, pero lo hace una vez y no en un loop constante, dando la logica de la conexion asincrona
    print("Servidor Asincrono Listo")
    return s, poller #Devuelve ambos para su uso posterior

def recibir_mensaje(data):
    global lista_productos, modo_ventas, modo_mantenimiento, led_azul 
    mensaje = data.decode().strip().upper()
    
    if mensaje.startswith("STOCK:"):
        mensaje_lista_stock = mensaje.split(":")
        lista_productos = []
        for i in range(1, len(mensaje_lista_stock)):
            lista_productos.append(int(mensaje_lista_stock[i]))
        print("Lista de productos actualizada!!")
        print(lista_productos)
        if modo_mantenimiento == False:
            modo_ventas = True


    elif mensaje.startswith("MANTENIMIENTO:ACTIVAR"):
            iniciar_mantenimiento()
 
    elif mensaje.startswith("MANTENIMIENTO:DESACTIVAR"):
            led_azul.value(0)
            servo.duty_u16(half_duty)
            modo_mantenimiento = False
            modo_ventas = True 

#Definir una funcion para enviar mensajes
def enviar_mensaje(id, producto):
    global cliente_sock #Revisar si hay un cliente conectado
    mensaje = None #En caso de que no haya mensaje
    
    if id == "VENTA": #es decir que se vendio un producto
        mensaje = f"VENTA:{producto}:{lista_productos[0]}:{lista_productos[1]}:{lista_productos[2]}"

    if cliente_sock:
        try:
            cliente_sock.send(bytes(mensaje, "utf-8")) #hay que codificar siempre el mensaje, en este caso encode no me funciono entonces use bytes, utf 8 es un estandar de codificacion
        except Exception as e:
            print("ERROR", e) 
    else:
        print("No hay cliente conectado")



#definimos una funcion para iniciar el programa

def inicio():
   global ip_local, server_sock, poller #Necesito que sean variables globales para que estas mismas se usen en el main loop!!
   ip_local = connect_wifi() #Como conect wifi conecta la rasp y devuelve una ip, lo podemos iniciar asi
   server_sock, poller = iniciar_servidor_async(ip_local) #El server sock y poller los devuelve la funcion de iniciar servidor async
   print("Sistema listo.")

inicio()
print("inicio while loop")
#Loop principal
while True:
    
    # Eventos de red
    eventos = poller.poll(0) #Pregunta si hay actividad sin bloquear el sistema
    for sock, ev in eventos: #Itera sobre cada socket para recibir su informacion
        
        #Conexion al servidor
        
        if sock == server_sock: #Basicamente dice que si el sock que tuvo actividad es el mismo que el de la Rasp, es porque hay un cliente conectandose
            cliente_sock, addr = server_sock.accept() #Acepta la conexion
            print("PC Conectada:", addr)
            poller.register(cliente_sock, select.POLLIN) #Registra un poller, que sera la entrada de datos desde la PC
        
        elif sock == cliente_sock: #Si llega un mensaje desde el PC
            try: 
                data = cliente_sock.recv(1024) #Intenta recibir informacion
                if data:
                    #Si hay informacion, simplemente llamamos a la funcion de manejar_mensajes
                    recibir_mensaje(data)
                    
            except: #Si no hay sock del cliente, simplemente lo desconecta
                poller.unregister(cliente_sock) #quita el poller
                cliente_sock.close() #cerramos el socket del cliente
                cliente_sock = None #lo pasamos a None,
    
    # Modo de ventas
    if modo_ventas:
        # Potenciometro 
        adc_value = potenciometro.read_u16()

        if adc_value > 50000:
            producto = 0 #Este es el indice de la lista

        elif 20000 < adc_value < 50000:
            producto = 1
        else:
            producto = 2
       
       # Prender Leds
       
        if lista_productos[producto] == 0: #Si no hay producto, prender rojo y no prender verde
            led_rojo.value(1)
            led_verde.value(0)
       
        else: #Si hay productos, hacer la instruccion alreves
            led_rojo.value(0)
            led_verde.value(1)
        mostrar_cantidad_productos(producto) #Mostrar la cantidad de producto en el 7 segmentos
        
        # Procedimiento compra productos
        if boton.value() == 1 and lista_productos[producto] > 0:
            lista_productos[producto] = lista_productos[producto] - 1
            enviar_mensaje("VENTA", producto)
            if lista_productos[producto] == 0: #Si no hay producto, prender rojo y no prender verde
                led_rojo.value(1)
                led_verde.value(0)
           
            else: #Si hay productos, hacer la instruccion alreves
                led_rojo.value(0)
                led_verde.value(1)
            mostrar_cantidad_productos(producto) #Mostrar la cantidad de producto en el 7 segmentos
            servo.duty_u16(min_duty)
            time.sleep(3)
            servo.duty_u16(half_duty)
            time.sleep(1)
        
        
        
        time.sleep(0.1) #Evitar que la rasperry se sobre caliente
