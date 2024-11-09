import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import ctypes
import winreg
import platform
import psutil
import locale  # Para obtener el rendimiento del sistema

# Función para obtener permisos de administrador
def es_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Re-ejecuta el script con permisos de administrador si no los tiene
def ejecutar_como_admin():
    if not es_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

# Función para listar reglas del cortafuegos
def listar_reglas_cortafuegos():
    try:
        comando = ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, resultado.stdout)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo listar las reglas del cortafuegos: {e}")

# Función para agregar una regla al cortafuegos
def agregar_regla_cortafuegos():
    nombre_regla = entry_nombre.get().strip()
    puerto = entry_puerto.get().strip()

    if not nombre_regla or not puerto.isdigit():
        messagebox.showwarning("Entrada inválida", "Por favor, ingrese un nombre válido para la regla y un puerto numérico.")
        return

    if not es_admin():
        ejecutar_como_admin()
        return

    try:
        comando = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={nombre_regla}",
            "dir=in",
            "action=allow",
            "protocol=TCP",
            f"localport={puerto}"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, resultado.stdout)

        if "Ok" in resultado.stdout:
            messagebox.showinfo("Éxito", f"Regla '{nombre_regla}' agregada con éxito.")
        else:
            messagebox.showwarning("Advertencia", f"No se pudo agregar la regla: {resultado.stdout}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo agregar la regla del cortafuegos: {e}")

# Función para eliminar una regla del cortafuegos
def eliminar_regla_cortafuegos():
    nombre_regla = entry_nombre.get().strip()

    if not nombre_regla:
        messagebox.showwarning("Entrada inválida", "Por favor, ingrese un nombre válido para la regla.")
        return

    if not es_admin():
        ejecutar_como_admin()
        return

    try:
        comando = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={nombre_regla}"]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, resultado.stdout)

        if "No rules match" in resultado.stdout:
            messagebox.showwarning("Advertencia", f"No se encontró ninguna regla con el nombre '{nombre_regla}' para eliminar.")
        else:
            messagebox.showinfo("Éxito", f"Regla '{nombre_regla}' eliminada con éxito.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar la regla del cortafuegos: {e}")

# Función para obtener la lista de programas instalados en el sistema
def obtener_programas():
    programas = []
    clave_registro = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    
    # Abrir la clave del registro
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave_registro) as key:
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    programa = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    programas.append(programa)
            except FileNotFoundError:
                pass
    return programas

# Función para mostrar la lista de programas instalados
def mostrar_programas():
    programas = obtener_programas()
    for programa in programas:
        lista_programas.insert("", "end", text=programa)

# Función para abrir la configuración del cortafuegos
def abrir_configuracion_cortafuegos():
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()

    label_titulo1 = ttk.Label(frame_visualizacion, text="JGS-Configuración del Cortafuegos", font=("Arial", 16, "bold"))
    label_titulo1.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    label_nombre = ttk.Label(frame_visualizacion, text="Nombre de la regla:")
    label_nombre.grid(row=1, column=0, padx=10, pady=5)
    global entry_nombre
    entry_nombre = ttk.Entry(frame_visualizacion)
    entry_nombre.grid(row=1, column=1, padx=10, pady=5)

    label_puerto = ttk.Label(frame_visualizacion, text="Puerto:")
    label_puerto.grid(row=2, column=0, padx=10, pady=5)
    global entry_puerto
    entry_puerto = ttk.Entry(frame_visualizacion)
    entry_puerto.grid(row=2, column=1, padx=10, pady=5)

    btn_listar = ttk.Button(frame_visualizacion, text="Listar Reglas", command=listar_reglas_cortafuegos)
    btn_listar.grid(row=3, column=0, padx=10, pady=5)

    btn_agregar = ttk.Button(frame_visualizacion, text="Agregar Regla", command=agregar_regla_cortafuegos)
    btn_agregar.grid(row=3, column=1, padx=10, pady=5)

    btn_eliminar = ttk.Button(frame_visualizacion, text="Eliminar Regla", command=eliminar_regla_cortafuegos)
    btn_eliminar.grid(row=3, column=2, padx=10, pady=5)

    global text_area
    text_area = tk.Text(frame_visualizacion, height=15, width=70)
    text_area.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Función para abrir la lista de programas instalados
def abrir_programas_instalados():
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()

    label_titulo = ttk.Label(frame_visualizacion, text="Programas Instalados", font=("Arial", 20, "bold"))
    label_titulo.grid(row=0, column=0, padx=10, pady=10)

    global lista_programas
    lista_programas = ttk.Treeview(frame_visualizacion, height=20)
    lista_programas.heading("#0", text="Programas Instalados")
    lista_programas.config(height=20)
    lista_programas.grid(row=1, column=0, padx=0, pady=5)

    frame_visualizacion.config(width=600, height=400)
    frame_visualizacion.grid_propagate(False)

    mostrar_programas()

# Función para obtener la versión de Windows
def obtener_version_windows():
    system = platform.system()
    version = platform.release()
    version_detalle = platform.version()
    return f"{system} {version} ({version_detalle})"

# Función para obtener la memoria RAM total y libre
def obtener_memoria():
    memoria = psutil.virtual_memory()
    total = memoria.total / (1024 ** 3)  # Convertir a GB
    libre = memoria.available / (1024 ** 3)  # Convertir a GB
    return f"Total RAM: {total:.2f} GB | Libre: {libre:.2f} GB"

# Función para obtener el uso del CPU
def obtener_cpu():
    uso_cpu = psutil.cpu_percent(interval=1)
    return f"Uso CPU: {uso_cpu}%" 

# Función para obtener el uso del disco duro
def obtener_disco():
    uso_disco = psutil.disk_usage('/').percent
    return f"Uso Disco: {uso_disco}%" 

# Función para actualizar la información
def actualizar_info():
    # Obtener la versión de Windows, la memoria, el CPU y el disco
    version_info = obtener_version_windows()
    memoria_info = obtener_memoria()
    cpu_info = obtener_cpu()
    disco_info = obtener_disco()

    # Actualizar las etiquetas con la nueva información
    version_label.config(text=f"Versión de Windows: {version_info}")
    memoria_label.config(text=f"{memoria_info}")
    cpu_label.config(text=f"{cpu_info}")
    disco_label.config(text=f"{disco_info}")

    # Actualizar cada 5 segundos
    root.after(5000, actualizar_info)

# Función para mostrar los procesos en ejecución
def mostrar_procesos():
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()

    label_titulo = ttk.Label(frame_visualizacion, text="Procesos en Ejecución", font=("Arial", 20, "bold"))
    label_titulo.grid(row=0, column=0, padx=10, pady=10)

    global lista_procesos
    lista_procesos = ttk.Treeview(frame_visualizacion, height=20)
    lista_procesos.heading("#0", text="Proceso")
    lista_procesos.config(height=20)
    lista_procesos.grid(row=1, column=0, padx=0, pady=5)

    frame_visualizacion.config(width=600, height=400)
    frame_visualizacion.grid_propagate(False)

    # Obtener los procesos del sistema y mostrarlos
    for proc in psutil.process_iter(['pid', 'name']):
        lista_procesos.insert("", "end", text=f"{proc.info['name']} (PID: {proc.info['pid']})")
# Función para obtener permisos de administrador
def es_adminin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def ejecutar_como_adminin():
    if not es_adminin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

# Función para obtener la información del sistema
def obtener_informacion_sistema():
    info = {}
    info["Sistema operativo"] = platform.system()
    info["Versión del sistema operativo"] = platform.version()
    info["Arquitectura"] = platform.architecture()[0]
    info["Nombre del equipo"] = platform.node()
    info["Procesador"] = platform.processor()
    info["Idioma del sistema"] = locale.getdefaultlocale()[0]

    mem = psutil.virtual_memory()
    info["Memoria RAM total"] = f"{round(mem.total / (1024**3), 2)} GB"

    disk = psutil.disk_usage('/')
    info["Espacio total en disco"] = f"{round(disk.total / (1024**3), 2)} GB"
    info["Espacio libre en disco"] = f"{round(disk.free / (1024**3), 2)} GB"

    if platform.system() == "Windows":
        try:
            fabricante = subprocess.check_output("wmic computersystem get manufacturer", shell=True).decode().split('\n')[1].strip()
            modelo = subprocess.check_output("wmic computersystem get model", shell=True).decode().split('\n')[1].strip()
            info["Fabricante"] = fabricante
            info["Modelo"] = modelo
        except Exception as e:
            info["Fabricante"] = "No disponible"
            info["Modelo"] = "No disponible"
    
    return info

# Función para mostrar la información del sistema en el marco de visualización
def mostrar_informacion_sistema():
    # Limpiar el frame de visualización
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()

    label_titulo = ttk.Label(frame_visualizacion, text="Especificaciones del Sistema", font=("Arial", 14, "bold"))
    label_titulo.pack(pady=10)

    info = obtener_informacion_sistema()
    for key, value in info.items():
        etiqueta = ttk.Label(frame_visualizacion, text=f"{key}: {value}")
        etiqueta.pack(anchor="w", padx=10, pady=2)

        # Función para obtener permisos de administrador
def es_adminin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def ejecutar_como_adminin():
    if not es_adminin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

# Función para obtener la información del sistema
def obtener_informacion_sistema():
    info = {}
    info["Sistema operativo"] = platform.system()
    info["Versión del sistema operativo"] = platform.version()
    info["Arquitectura"] = platform.architecture()[0]
    info["Nombre del equipo"] = platform.node()
    info["Procesador"] = platform.processor()
    info["Idioma del sistema"] = locale.getdefaultlocale()[0]

    mem = psutil.virtual_memory()
    info["Memoria RAM total"] = f"{round(mem.total / (1024**3), 2)} GB"

    disk = psutil.disk_usage('/')
    info["Espacio total en disco"] = f"{round(disk.total / (1024**3), 2)} GB"
    info["Espacio libre en disco"] = f"{round(disk.free / (1024**3), 2)} GB"

    if platform.system() == "Windows":
        try:
            fabricante = subprocess.check_output("wmic computersystem get manufacturer", shell=True).decode().split('\n')[1].strip()
            modelo = subprocess.check_output("wmic computersystem get model", shell=True).decode().split('\n')[1].strip()
            info["Fabricante"] = fabricante
            info["Modelo"] = modelo
        except Exception as e:
            info["Fabricante"] = "No disponible"
            info["Modelo"] = "No disponible"
    
    return info

# Función para mostrar la información del sistema en el marco de visualización
def mostrar_informacion_sistema():
    # Limpiar el frame de visualización
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()

    label_titulo = ttk.Label(frame_visualizacion, text="Especificaciones del Sistema", font=("Arial", 14, "bold"))
    label_titulo.pack(pady=10)

    info = obtener_informacion_sistema()
    for key, value in info.items():
        etiqueta = ttk.Label(frame_visualizacion, text=f"{key}: {value}")
        etiqueta.pack(anchor="w", padx=10, pady=2)


# Ventana principal
root = tk.Tk()
root.title("Aplicación Principal en Tkinter")
root.geometry("800x600")

# Frame izquierdo para el menú
frame_menu = ttk.Frame(root)
frame_menu.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

# Etiqueta de "Menú"
label_menu = ttk.Label(frame_menu, text="Menú", font=("Arial", 14))
label_menu.pack(pady=10)


# Botones de menú
btn_config_cortafuegos = ttk.Button(frame_menu, text="Abrir Configuración del Cortafuegos", command=abrir_configuracion_cortafuegos)
btn_config_cortafuegos.pack(pady=5)


#ver programas
btn_programas_instalados = ttk.Button(frame_menu, text="Ver Programas Instalados", command=abrir_programas_instalados)
btn_programas_instalados.pack(pady=5)

#boton de mostrar procesos

btn_procesos = ttk.Button(frame_menu, text="Ver Procesos", command=mostrar_procesos)
btn_procesos.pack(pady=5)


#boton de mostrar informacion
btn_procesos = ttk.Button(frame_menu, text="mostrar_informacion_sistema", command=mostrar_informacion_sistema)
btn_procesos.pack(pady=5)

# Etiqueta de título y la información del sistema
title_label = tk.Label(root, text="Detalles del Sistema", font=('Arial', 16))
title_label.grid(row=0, column=1, pady=10)

# Obtener la versión de Windows, la memoria RAM, CPU y Disco
version_info = obtener_version_windows()
memoria_info = obtener_memoria()
cpu_info = obtener_cpu()
disco_info = obtener_disco()

# Etiquetas para mostrar la versión de Windows, la RAM, el CPU y el Disco
version_label = tk.Label(root, text=f"Versión de Windows: {version_info}", font=('Arial', 12))
version_label.grid(row=1, column=1, pady=5)

memoria_label = tk.Label(root, text=f"{memoria_info}", font=('Arial', 12))
memoria_label.grid(row=2, column=1, pady=5)

cpu_label = tk.Label(root, text=f"Uso CPU: {cpu_info}", font=('Arial', 12))
cpu_label.grid(row=3, column=1, pady=5)

disco_label = tk.Label(root, text=f"Uso Disco: {disco_info}", font=('Arial', 12))
disco_label.grid(row=4, column=1, pady=5)

# Frame derecho para la visualización
frame_visualizacion = ttk.Frame(root)
frame_visualizacion.grid(row=0, column=1, sticky="nsew", padx=10, pady=0)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Llamar la función para actualizar la información cada 5 segundos
root.after(5000, actualizar_info)

# Ejecutar la aplicación
root.mainloop()
