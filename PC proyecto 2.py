# cliente_gui.py
import socket
import threading
import tkinter as tk

SERVER_IP = "10.165.83.130"  # Cambia esto con la IP de la Pico W
PORT = 1717

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        except:
            break

def salir():
    try:
        client_socket.close()
    except:
        pass
    root.destroy()

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

connect()
root.mainloop()