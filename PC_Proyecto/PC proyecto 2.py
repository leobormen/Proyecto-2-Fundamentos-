# cliente_gui.py
import socket
import threading
import requests
import tkinter as tk
import time 

#Variables 
SERVER_IP = "10.136.232.130" # Cambia esto con la IP de la Pico W
PORT = 1717

lista_productos = []
lista_stats = []

#Definir el Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Definir variables importantes
tipo_cambio = "Obteniendo tipo de cambio..."
ventana_actual = "PRINCIPAL"

#API 
def obtener_tipo_cambio():
    global tipo_cambio 
   
    #Por si falla el API para volver a intentarlo (en sentido de ejecucion DESPUES de la ejecucion inicial al arrancar el programa)
    tipo_cambio = "Obteniendo tipo de cambio..."
    if ventana_actual == "STATS": #Si no esta en STATS, entonces no es necesario refrescar la pagina
        modo_estadisticas() #Refrescar para eliminar el boton

    #Procedimiento 
    try:
        # Realiza una solicitud HTTP a la API y espera 5 segundos  (HTTP --> mensaje que un cliente envia a un servidor para pedir un recurso o realizar una accion)
        response = requests.get("https://exchangecr.albertosaenz.com/api/tipodecambio",timeout=5) #Espera 5 segundos

        if response.status_code == 200: #Pregunta si el codigo de status del response es 200, si no significaria que no se acceso correctamente a la API
            datos = response.json() #Datos es un diccionario y le aplicamos .json() para decirle a Python como es el formato de los datos recibidos

            for divisa in datos: #Como recibimos una lista de diccionarios, simplemente lo iteramos
                if divisa["divisa"] == "USdollar": #El API usado entrega dolares, entonces esto de aqui es preguntarle al diccionario "Que informacion contiene "divisa"
                    tipo_cambio = float(divisa["venta"]) #Si es el USdollar, simplemente se saca un valor en float y listo.
                    if ventana_actual == "STATS": #Refrescar la pagina 
                        modo_estadisticas()
                    break 
        
        else : #Es decir que no se acceso correctamente la pagina 
            tipo_cambio = "ERROR" #es decir que fallo haciendo esto, sirve para poner el boton para reintentar
            if ventana_actual == "STATS":
                modo_estadisticas()
        
    except Exception as e: # En caso de que falle la ejecucion
        print("Error obteniendo tipo de cambio:", e)
        tipo_cambio = "ERROR" #es decir que fallo haciendo esto, sirve para poner el boton para reintentar
        if ventana_actual == "STATS":
            modo_estadisticas()
        return None 

#Conexion Wifi
def connect():

    try:
        client_socket.connect((SERVER_IP, PORT)) #Intenta connectar el socket a la rasperry PI 
        threading.Thread(target=receive_messages, daemon=True).start() #Si se conecta, genera un thread para no paralizar la ejecucion del programa
        print("Conectado al servidor") #Nos imprime que si esta conectado correctamente
    except Exception as e:
        print(f"Error: {e}") #Si no imprime un error

def receive_messages():
    while True: #Loop
        try:
            msg = client_socket.recv(1024).decode() #decodificar mensaje
            print(f"Mensaje Rasperry: {msg}\n") #Imprime el mensaje en vs code
            if msg.startswith("VENTA:"): #Cuestion de formato
                escritura_stock(msg, None) #Escribir el stock dando como argumento mensaje
                escritura_stats(msg) #Actualizar la variable de stats
                if ventana_actual == "PRINCIPAL" or ventana_actual == "MANTENIMIENTO":  
                    cambiar_labels_existencias() #Actualizar los labels de existencias, no se llama toda la pantalla ya que en este caso esta funcion esta compartida para ambas
                elif ventana_actual == "STATS":
                    modo_estadisticas() #Actualizar la pantalla de estadisticas, despues de escribir Y actualizar estso mismos
                    

        except:
            break

def salir():
    try:
        client_socket.close() #Cerrar el socket
    except:
        pass #NO hacer nada
    root.destroy() #Destruir root


# Acceder lectura productos
def leer_archivo_productos():
    global lista_productos 
    try: #Se intenta por si este esta vacio
        file = open("inventario_productos.txt", "r") #R es read
        for producto in file: #Por ccada linea
            datos = producto.strip().split(",") #El dato viene en formato Producto,Numero
            cantidad = int(datos[1]) 
            lista_productos.append(cantidad)
        file.close() #Cerrar el archivo es buena practica
    except :
        pass #Significa que no hay un archivo

# # Escritura 
def escritura_stock(msg_rasp, msg_mantenimiento): #Puede funcionar para dos cosas
    global lista_productos
    if msg_rasp != None : #Si la escritura del STOCK va a ser por UNA VENTA
        lista_productos = [] #Hay que limpiar la lista de productos para actualizar, ya que con msg_rasp significa que el mensaje fue de una venta
        file = open("inventario_productos.txt", "w") # No lo vaciamos, ya que "w" se encarga de eso por nosotros
        mensaje = msg_rasp.strip().upper().split(":") #Se vacia la lista ya que se actualiza en base a lo que viene en la rasp
        for i in range(2, len(mensaje)):
            file.write(f"Producto{i-1},{mensaje[i]}\n") #Hace una reescritura del mensaje en tiempo real
            lista_productos.append(int(mensaje[i])) #EEn este caso si hay que cambiar la lista
        file.close()
    
    elif msg_mantenimiento != None: #Si la escritura del STOCK va a ser por ACTUALIZAR MANUALMENTE
        file = open("inventario_productos.txt", "w") # No lo vaciamos, ya que "w" se encarga de eso por nosotros
        for i in range(len(lista_productos)):
            file.write(f"Producto{i+1},{lista_productos[i]}\n") #Hace una reescritura del mensaje en tiempo real
        file.close()

# Lectura de archivo stats
def leer_archivo_stats():
    global lista_stats
    try: #Se intenta por si este esta vacio
        file = open("stats_ventas.txt", "r") #R es read
        for producto in file: 
            datos = producto.strip().split(",") #Lo escrito en el doc se vuevle una lista
            cantidad = int(datos[1]) #Le sacamos un int
            lista_stats.append(cantidad) #Le hacemos append
        file.close() #Cerrar el archivo es buena practica
    except :
        pass #Significa que no hay un archivo

#Escritura de stats
def escritura_stats(msg):
    global lista_stats 
    mensaje = msg.strip().upper().split(":") 
    index = int(mensaje[1]) #El segundo item de la lista contiene el numero del producto ya que el mensaje viente "CODIGOACCION:PRODUCTO:EXISTENCIAS1:EXISTENCIAS2:EXISTENCIAS3"
    lista_stats[index] += 1 #Se le agrega una unidad por cosa vendida en el rasperry
        
    file = open("stats_ventas.txt", "w") # No lo vaciamos, ya que "w" se encarga de eso por nosotros
    for i in range(len(lista_stats)):
        file.write(f"Producto{i + 1},{lista_stats[i]}\n") #Hace una reescritura del mensaje en tiempo real
    file.close()


# Enviar productos  
def enviar_mensaje_rasp(id): #Funciona con id, es como decir "se presiono el boton 1, haga 1, ... se presiono boton n, haga n"
    # DEFINIR MENSAJE
    if id == 1:  
        mensaje = "STOCK" # Empezar con el mensaje
        for producto in lista_productos: #Para cada producto se usa algo 
            mensaje += f":{producto}"
    elif id == 2:
        mensaje = "MANTENIMIENTO:ACTIVAR" 
    elif id == 3:
        mensaje = "MANTENIMIENTO:DESACTIVAR"
    
    # INTENTAR MANDAR MENSAJE
    try:
        client_socket.send(mensaje.encode())
    except:
        print("Error enviando mensaje")


#Leer ambos documentos
def leer_archivos(): #Iniciar ejecucion
    leer_archivo_productos()
    leer_archivo_stats()


# GUI
root = tk.Tk()
root.title("Cliente GUI")
root.geometry("600x800")
root.resizable(False, False)

#Se crea un frame, que basicamente es como decir que root es la pared y frame es la pizarra, entonces esa pizarra se puede usar para dibujar y borrar lo que sea. esto se hace para obtener un movimiento de ventanas mas fluido
frame_gui = tk.Frame(root, width=600, height=800)
frame_gui.pack_propagate(False)  # evita que el frame se encoja
frame_gui.pack() #Se pone el frame

# Limpiar el frame
def clear_frame():
    for widget in frame_gui.winfo_children(): #winfo_children obtiene los widgets presentes en la ventana 
        widget.destroy() #Los limpiamos

# Menu Principal
def menu_principal():
    global ventana_actual, producto1_existencias, producto2_existencias, producto3_existencias
    ventana_actual = "PRINCIPAL" #Actualizar cual ventana se esta trabajando para las funciones de arriba
    clear_frame() #Siempre hay que limpiar esto 

    titulo = tk.Label(frame_gui, text="CELect Manager") #Definir en una label en que modo se esta
    titulo.pack()

    btn_salir = tk.Button(frame_gui, text="Salir", command=lambda:salir())
    btn_salir.pack()
    
    btn_mantenimiento = tk.Button(frame_gui, text="Mantenimiento", command=lambda:modo_mantenimiento())
    btn_mantenimiento.pack()

        
    btn_mantenimiento = tk.Button(frame_gui, text="Estadisticas de Ventas", command=lambda:modo_estadisticas())
    btn_mantenimiento.pack()

    producto1_existencias = tk.Label(frame_gui, text=f"Existencias P1: {lista_productos[0]}")
    producto1_existencias.place(relx=0.3, y=250, anchor="center")

    producto2_existencias = tk.Label(frame_gui, text=f"Existencias P2: {lista_productos[1]}")
    producto2_existencias.place(relx=0.5, y=250, anchor="center")

    producto3_existencias = tk.Label(frame_gui, text=f"Existencias P3: {lista_productos[2]}")
    producto3_existencias.place(relx=0.7, y=250, anchor="center")
    

# Menu Mantenimiento

def cambiar_stock():
    global lista_productos
    
    #Se recogen los datos de los scales con .get
    lista_productos[0] = scale_producto1.get()
    lista_productos[1] = scale_producto2.get()
    lista_productos[2] = scale_producto3.get()
    
    escritura_stock(None, lista_productos) #se escribe el stock en el documento.txt
    enviar_mensaje_rasp(1) #Se envia el mensaje a la rasperry
    cambiar_labels_existencias() #Se cambian las lables


def cambiar_labels_existencias(): #actualizar existencias 
    producto1_existencias.config(text=f"Existencias P1: {lista_productos[0]}")
    producto2_existencias.config(text=f"Existencias P2: {lista_productos[1]}")
    producto3_existencias.config(text=f"Existencias P3: {lista_productos[2]}")

def terminar_mantenimiento():
    enviar_mensaje_rasp(3) #Enviarle a la rasp "MANTENIMIENTO:DESACTIVAR"
    menu_principal() #Regresar al menu principal.

def modo_mantenimiento():
    global scale_producto1, scale_producto2, scale_producto3, producto1_existencias, producto2_existencias, producto3_existencias, ventana_actual
    ventana_actual = "MANTENIMIENTO"
    enviar_mensaje_rasp(2) #Enviarle a la rasp "MANTENIMIENTO:ACTIVAR"
    clear_frame() #Siemrpe se limpia el frame al principio

    titulo_label = tk.Label(frame_gui, text="Modo de Mantenimiento CElect")
    titulo_label.pack()

    btn_menu_principal = tk.Button(frame_gui, text="Salir del Modo Mantenimiento", command = lambda:terminar_mantenimiento())
    btn_menu_principal.pack()
    

    # Labels Existencias de productos // Se llaman igual que en modo mantenimiento para la funcion de actualizar 

    producto1_existencias = tk.Label(frame_gui, text=f"Existencias P1: {lista_productos[0]}")
    producto1_existencias.place(relx=0.3, y=250, anchor="center")

    producto2_existencias = tk.Label(frame_gui, text=f"Existencias P2: {lista_productos[1]}")
    producto2_existencias.place(relx=0.5, y=250, anchor="center")

    producto3_existencias = tk.Label(frame_gui, text=f"Existencias P3: {lista_productos[2]}")
    producto3_existencias.place(relx=0.7, y=250, anchor="center")
    
    #Sliders para dar la cantidad de productos // Funcionan como el volumen

    scale_producto1 = tk.Scale(frame_gui, from_=0, to=8, orient="horizontal", label="    Producto 1")
    scale_producto1.place(relx=0.3, y=300, anchor="center")

    scale_producto2 = tk.Scale(frame_gui, from_=0, to=8, orient="horizontal", label="    Producto 2")
    scale_producto2.place(relx=0.5, y=300, anchor="center")

    scale_producto3 = tk.Scale(frame_gui, from_=0, to=8, orient="horizontal", label="    Producto 3")
    scale_producto3.place(relx=0.7, y=300, anchor="center") 

    # Botones para confirmar entrada

    btn_p2 = tk.Button(frame_gui, text="Confirmar y Cambiar Stock \n Productos \n Nota: \n Salir sin presionar este boton \n NO genera cambios de existencias", command=lambda: cambiar_stock())
    btn_p2.place(relx=0.5, y=400, anchor="center")


# Menu Estadisticas
def modo_estadisticas():
    global ventana_actual
    ventana_actual = "STATS"
    clear_frame()
    
    
    #Titulo 
    titulo_label = tk.Label(frame_gui, text="Estadisticas de Ventas CELect")
    titulo_label.pack()

    #Regresar al menu
    btn_menu_principal = tk.Button(frame_gui, text="Salir del Modo Mantenimiento", command = lambda:menu_principal())
    btn_menu_principal.pack()
    

    # Se crean labels que dan estadisticas por producto
    producto1_ventas = tk.Label(frame_gui, text=f"Ventas P1: {lista_stats[0]}")
    producto1_ventas.place(relx=0.3, y=250, anchor="center")

    producto2_ventas = tk.Label(frame_gui, text=f"Ventas P2: {lista_stats[1]}")
    producto2_ventas.place(relx=0.5, y=250, anchor="center")

    producto3_ventas = tk.Label(frame_gui, text=f"Ventas P3: {lista_stats[2]}")
    producto3_ventas.place(relx=0.7, y=250, anchor="center")

    #Como esta ventana es la que trabaja el tipo de cambio, no se puede dividir entre un string para obtener los dolares, por eso se hacen 3 "estados" de la variable de "tipo_cambio"
    if tipo_cambio == "Obteniendo tipo de cambio...":
        label_tipo_cambio = tk.Label(frame_gui, text= f"{tipo_cambio}") 
        label_tipo_cambio.pack()
    
    #Si al usar la funcion "obtener_tipo_cambio()" nos "devuelve" error, se genera un boton para volver a intentar, y luego desaparece porque se cambia tipo de cambio
    elif tipo_cambio == "ERROR":
        tk.Label(frame_gui, text="Error obteniendo el tipo de cambio :(").pack()
        btn_reintentar = tk.Button(frame_gui, text="Reintentar", command=lambda: threading.Thread(target=obtener_tipo_cambio, daemon=True).start()) #Basicamente repite lo del inicio
        btn_reintentar.pack() 

    else: #Caso de que si este bien
        #Demostrar el tipo de cambio
        label_tipo_cambio = tk.Label(frame_gui, text=f"Tipo de cambio: ₡{tipo_cambio}")
        label_tipo_cambio.pack()

        #Definir ganancias totales para su uso despues
        ganancias_totales_colones = sum(lista_stats) * 250
        ganancias_totales_dolares = round(ganancias_totales_colones / tipo_cambio, 2)

        # Ganancias por producto
        label_ganancia_p1 = tk.Label(frame_gui, text=f"Ganancias P1: ₡{lista_stats[0] * 250} / ${round(lista_stats[0] * 250 / tipo_cambio, 2)}") 
        label_ganancia_p1.place(relx=0.2, y=300, anchor="center")                       #Round nos permite redondear numeros, entonces aqui el objetivo es obtener 2 decimales funciona asi (numero a redondear, cantidad digitos)

        label_ganancia_p2 = tk.Label(frame_gui, text=f"Ganancias P2: ₡{lista_stats[1] * 250} / ${round(lista_stats[1] * 250 / tipo_cambio, 2)}")
        label_ganancia_p2.place(relx=0.5, y=300, anchor="center")

        label_ganancia_p3 = tk.Label(frame_gui, text=f"Ganancias P3: ₡{lista_stats[2] * 250} / ${round(lista_stats[2] * 250 / tipo_cambio, 2)}")
        label_ganancia_p3.place(relx=0.8, y=300, anchor="center")

        # Ganancias totales
        label_ganancias_colones = tk.Label(frame_gui, text=f"Ganancias totales: ₡{ganancias_totales_colones}")
        label_ganancias_colones.place(relx=0.5, y=350, anchor="center")

        label_ganancias_dolares = tk.Label(frame_gui, text=f"Ganancias totales: ${ganancias_totales_dolares}")
        label_ganancias_dolares.place(relx=0.5, y=400, anchor="center")

        #Label ventas Totales 
        label_ventas_totales = tk.Label(frame_gui, text=f"Ventas totales: {sum(lista_stats)}") #Sumatoria de lista
        label_ventas_totales.place(relx=0.5, y=200, anchor="center")


#Funciones para ejecutar el programa
def inicio():
    threading.Thread(target=connect, daemon=True).start()
    threading.Thread(target=obtener_tipo_cambio, daemon=True).start()
    leer_archivos()
    enviar_mensaje_rasp(1)
    menu_principal()

inicio()
root.mainloop()
