import requests #Se usa requests para que el codigo pueda hacer la busqueda del API usado

def obtener_tipo_cambio():
    try:
        # Realiza una solicitud HTTP a la API y espera 5 segundos  (HTTP --> mensaje que un cliente envia a un servidor para pedir un recurso o realizar una accion)
        response = requests.get(
            "https://exchangecr.albertosaenz.com/api/tipodecambio",
            timeout=5
        )

        if response.status_code == 200: #Pregunta si el codigo de status del response es 200, si no significaria que no se acceso correctamente a la API
            datos = response.json() #Datos es un diccionario y le aplicamos .json() para decirle a Python como es el formato de los datos recibidos

            for divisa in datos: #Como recibimos una lista de diccionarios, simplemente lo iteramos
                if divisa["divisa"] == "USdollar": #El API usado entrega dolares, entonces esto de aqui es preguntarle al diccionario "Que informacion contiene "divisa"
                    return float(divisa["venta"]) #Si es el USdollar, simplemente se saca un valor intero y listo.

        return None #En caso de fallar

    except Exception as e: # En caso de fallar
        print("Error obteniendo tipo de cambio:", e)
        return None

#Prueba 
tipo_cambio = obtener_tipo_cambio()
print(round((600 / tipo_cambio), 3))