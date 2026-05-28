# Acceder a la informacion al abrir el documento

productos = []

def leer_archivo_productos():
    global productos 
    try: #Se intenta por si este esta vacio
        file = open("inventario_productos.txt", "r") #R es read
        for producto in file:
            datos = producto.strip().split(",")
            cantidad = int(datos[1]) 
            productos.append(cantidad)
        file.close() #Cerrar el archivo es buena practica
    except :
        pass #Significa que no hay un archivo

leer_archivo_productos()
print(productos)
