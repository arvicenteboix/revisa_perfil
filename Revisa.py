import tkinter as tk
from tkinter import ttk
import json
from google import genai
import os, sys
import base64
import threading
from tkinter import messagebox


# Ventana principal
root = tk.Tk()
root.title("Valencià / Castellano")

def enviar_data_api(datos):
    
    # Leer la API key desde el archivo
    try:
        with open('./api.txt', 'r', encoding='utf-8') as f:
            raw = f.read().strip()
            try:
                api_key = base64.b64decode(raw).decode('utf-8')
            except Exception:
                api_key = raw
    except FileNotFoundError:
        tk.messagebox.showerror("Error", "No has definit la clau API")
        return

    # Importar y usar Google Generative AI

    client = genai.Client(api_key=api_key)

    # Convertir datos a JSON
    json_data = json.dumps(datos, indent=2, ensure_ascii=False)

    # Crear el prompt
    prompt = f"Revisa la ortografia de este texto tanto en valenciano como en castellano y devuelveme un json de la misma manera, sin cambiar ningun nombre de campos (objetivos, contenidos, etc...) con las correcciones hechas y un nuevo campo en el json que se llame 'Correcciones' y me enumeres todas las correcciones que has hecho. La respuesta debe ser en valenciano, cuando enumeres dime, 'en objectius en valencià...' per exemple. Basat també en els següents criteris per al valencià https://dogv.gva.es/datos/2024/05/02/pdf/2024_3799.pdf donde pones cosas como que se use 'Este/a' en lugar de 'Aquest/a', etc... Si hay enumeraciones pon un guión al principio: - y trata de convertir todos los anglicismos a su equivalente en castellano o valenciano, envuelve el anglicismo en cursiva html <i>...</i> y entre paréntesis pon la traducción\n\n{json_data}"

    
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error en la petició: {e}")
        return



    # Limpiar el texto de la respuesta (eliminar ```json y ```)
    texto_limpio = response.text.strip()
    primera_linea_end = texto_limpio.find('\n')
    if primera_linea_end != -1:
        texto_limpio = texto_limpio[primera_linea_end+1:].lstrip()
    if texto_limpio.startswith("```json"):
        texto_limpio = texto_limpio[7:]
    if texto_limpio.startswith("```"):
        texto_limpio = texto_limpio[3:]
    if texto_limpio.endswith("```"):
        texto_limpio = texto_limpio[:-3]
    texto_limpio = texto_limpio.strip()
        
    # Convertir a JSON
    print("resultado_json:", texto_limpio)
    resultado_json = json.loads(texto_limpio)

    

    # Mostrar el resultado en una nueva ventana
    resultado_ventana = tk.Toplevel(root)
    resultado_ventana.title("Resultado de la revisión")
    resultado_ventana.geometry("800x600")
    
    # Crear un Text widget con scrollbar en lugar de Label para mejor visualización
    text_frame = ttk.Frame(resultado_ventana)
    text_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    resultado_text = tk.Text(text_frame, wrap='word', width=80, height=30)
    scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=resultado_text.yview)
    resultado_text.configure(yscrollcommand=scrollbar.set)
    

    resultado_text.insert('1.0', json.dumps(resultado_json['Castellano']['Correcciones'], indent=2, ensure_ascii=False))
    resultado_text.insert('2.0', '\n\n')
    resultado_text.insert('end', json.dumps(resultado_json['Valencià']['Correcciones'], indent=2, ensure_ascii=False))
    resultado_text.config(state='disabled')  # Hacer el texto de solo lectura
    
    resultado_text.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # Actualizar los campos con los resultados corregidos
    if 'Valencià' in resultado_json:
        for field in fields:
            if field in resultado_json['Valencià']:
                val_texts[field].delete("1.0", "end")
                val_texts[field].insert("1.0", resultado_json['Valencià'][field])
    
    if 'Castellano' in resultado_json:
        for field in fields:
            if field in resultado_json['Castellano']:
                cas_texts[field].delete("1.0", "end")
                cas_texts[field].insert("1.0", resultado_json['Castellano'][field])




    # Botón para cerrar la ventana
    btn_cerrar = ttk.Button(resultado_ventana, text="Cerrar", command=resultado_ventana.destroy)
    btn_cerrar.pack(pady=10)


def revisa_ort():    # Aquí iría la lógica para revisar la ortografía
    print("Revisando ortografía...")
    
    # Recoger todos los campos en un diccionario
    data_json = {
        "Valencià": {field: val_texts[field].get("1.0", "end-1c") for field in fields},
        "Castellano": {field: cas_texts[field].get("1.0", "end-1c") for field in fields}
    }
    
    # Convertir a JSON
    enviar_data_api(data_json)

    # json_data = json.dumps(data_json, indent=2, ensure_ascii=False)
    # print(json_data)

# Frames para cada idioma
frame_val = ttk.LabelFrame(root, text='Valencià')
frame_cas = ttk.LabelFrame(root, text='Castellano')
frame_val.grid(row=1, column=0, padx=5, pady=5, sticky='n')
frame_cas.grid(row=1, column=1, padx=5, pady=5, sticky='n')

fields = [
    "Objetivos",
    "Contenidos",
    "Material didáctico",
    "Condiciones",
    "Observaciones",
    "Dirigido a"
]

val_texts = {}
cas_texts = {}

for idx, field in enumerate(fields):
    # Etiqueta
    ttk.Label(frame_val, text=field).grid(row=idx, column=0, sticky='w')
    ttk.Label(frame_cas, text=field).grid(row=idx, column=0, sticky='w')

    # Campo de texto multilínea
    val_texts[field] = tk.Text(frame_val, height=4, width=40)
    scrollbar_val = ttk.Scrollbar(frame_val, orient='vertical', command=val_texts[field].yview)
    val_texts[field].configure(yscrollcommand=scrollbar_val.set)
    val_texts[field].grid(row=idx, column=1, padx=5)
    scrollbar_val.grid(row=idx, column=1, sticky='nse', padx=(0, 2))

    cas_texts[field] = tk.Text(frame_cas, height=4, width=40, wrap='word')
    scrollbar_cas = ttk.Scrollbar(frame_cas, orient='vertical', command=cas_texts[field].yview)
    cas_texts[field].configure(yscrollcommand=scrollbar_cas.set)
    scrollbar_cas.grid(row=idx, column=1, sticky='nse', padx=(0, 2))
    cas_texts[field].grid(row=idx, column=1, padx=5)
    # Botón de copiar
    copy_btn = ttk.Button(frame_val, text="📋", width=3, 
                          command=lambda f=field: root.clipboard_clear() or root.clipboard_append(val_texts[f].get("1.0", "end-1c")))
    copy_btn.grid(row=idx, column=2, padx=2)

    copy_btn_cas = ttk.Button(frame_cas, text="📋", width=3,
                              command=lambda f=field: root.clipboard_clear() or root.clipboard_append(cas_texts[f].get("1.0", "end-1c")))
    copy_btn_cas.grid(row=idx, column=2, padx=2)

    

    def abrir_ventana_api():
        # Crear ventana secundaria
        ventana_api = tk.Toplevel(root)
        ventana_api.title("Configuración API")
        ventana_api.geometry("400x150")
        
        # Etiqueta
        ttk.Label(ventana_api, text="API de Google:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        # Campo de entrada
        api_entry = ttk.Entry(ventana_api, width=40)
        api_entry.grid(row=1, column=0, padx=10, pady=5, columnspan=2)
        
        # Intentar cargar API existente

        try:
            with open('api.txt', 'r', encoding='utf-8') as f:
                raw = f.read().strip()
                try:
                    decoded = base64.b64decode(raw).decode('utf-8')
                except Exception:
                    decoded = raw
            api_entry.insert(0, decoded)
        except FileNotFoundError:
            pass
        
        # Función guardar
        def guardar_api():
            api_value = api_entry.get()
            encrypted = base64.b64encode(api_value.encode('utf-8')).decode('utf-8')
            with open('api.txt', 'w', encoding='utf-8') as f:
                f.write(encrypted)
            ventana_api.destroy()
        '''
        def guardar_api():
            with open('api.txt', 'w', encoding='utf-8') as f:
                f.write(api_entry.get())
            ventana_api.destroy()
        '''
        
        # Botón guardar
        btn_guardar = ttk.Button(ventana_api, text="Guardar", command=guardar_api)
        btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)

    # Menú
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    menu_config = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Configuración", menu=menu_config)
    menu_config.add_command(label="API de Google", command=abrir_ventana_api)

ttk.Label(root, text="Perfil").grid(row=0, column=0, sticky='w')
# perfil_var = tk.StringVar(value="Perfil base")
# perfil_opciones = ["Perfil base", "Otro perfil"]
# perfil_menu = ttk.OptionMenu(root, perfil_var, perfil_opciones[0], *perfil_opciones)
# perfil_menu.grid(row=0, column=1, sticky='w')


# Botón revisar ortografía
btn_revisar = ttk.Button(root, text="Revisar ortografía", command=revisa_ort)
btn_revisar.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
