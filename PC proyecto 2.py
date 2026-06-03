# cliente_gui.py
import socket
import threading
import tkinter as tk

SERVER_IP = "10.136.232.130" # Cambia esto con la IP de la Pico W
PORT = 1717

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#Conexion Wifi
def connect():
    try:
        client_socket.connect((SERVER_IP, PORT))
        threading.Thread(target=receive_messages, daemon=True).start()
        status_label.config(text="Conectado al servidor")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def receive_messages():
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            text_area.insert(tk.END, f"Raspberry: {msg}\n")
            if msg.startswith("STOCK:"):
                escritura_stock(msg)

        except:
            break


def salir():
    try:
        client_socket.close()
    except:
        pass
    root.destroy()


# Acceder lectura productos
lista_productos = []
def leer_archivo_productos():
    global lista_productos 
    try: #Se intenta por si este esta vacio
        file = open("inventario_productos.txt", "r") #R es read
        for producto in file:
            datos = producto.strip().split(",")
            cantidad = int(datos[1]) 
            lista_productos.append(cantidad)
        file.close() #Cerrar el archivo es buena practica
    except :
        pass #Significa que no hay un archivo

# # Escritura 
def escritura_stock(msg):
    global lista_productos
    lista_productos = [] #Hay que limpiar la lista de productos para actualizar
    file = open("inventario_productos.txt", "w") # No lo vaciamos, ya que "w" se encarga de eso por nosotros
    mensaje = msg.strip().upper().split(":")
    for i in range(1, len(mensaje)):
        file.write(f"Producto{i},{mensaje[i]}\n") #Hace una reescritura del mensaje en tiempo real
        lista_productos.append(int(mensaje[i]))
    file.close()



# Enviar productos  
def enviar_productos_rasp():
    mensaje = "STOCK" # Empezar con el mensaje
    for producto in lista_productos: #Para cada producto se usa algo 
        mensaje += f":{producto}"

    try:
        client_socket.send(mensaje.encode())
    except:
        print("Error")


# GUI
root = tk.Tk()
root.title("Cliente GUI")

entry = tk.Entry(root, width=50)
entry.pack()


text_area = tk.Text(root, height=10, width=60)
text_area.pack()

status_label = tk.Label(root, text="Desconectado")
status_label.pack()

salir_btn = tk.Button(root, text="Salir", command=salir)
salir_btn.pack()


#Funciones para ejecutar el programa

connect()
leer_archivo_productos()
enviar_productos_rasp() 
root.mainloop()