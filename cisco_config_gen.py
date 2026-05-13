import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: Falta la API Key en el archivo .env")
    exit()

# Inicializar cliente
client = Groq(api_key=api_key)

# Ítem 6: System prompt especializado
SYSTEM_PROMPT = """Eres un experto ingeniero de redes Cisco. 
Tu única tarea es generar configuraciones de Cisco IOS válidas.
REGLA ESTRICTA: Devuelve SOLO los comandos en bloque listos para copiar y pegar en la terminal. 
NO incluyas explicaciones, saludos, ni texto fuera de los comentarios de IOS (líneas que empiezan con !)."""

def guardar_configuracion(config_texto, tipo_escenario):
    """Guarda la configuración generada en la carpeta /configs/"""
    if not os.path.exists("configs"):
        os.makedirs("configs")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"configs/escenario_{tipo_escenario}_{timestamp}.txt"
    
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(config_texto)
        print(f"\n💾 Configuración guardada en: {nombre_archivo}")
    except Exception as e:
        print(f"\n❌ Error al guardar el archivo: {e}")

def generar_configuracion(prompt_usuario, tipo_escenario):
    """Función para llamar a Groq y generar la configuración con streaming"""
    try:
        print("\n⏳ Generando configuración...\n")
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario}
            ],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=1000,
            stream=True
        )
        
        config_completa = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                contenido = chunk.choices[0].delta.content
                print(contenido, end="")
                config_completa += contenido
        
        print("\n\n✅ Generación completada.")
        
        if config_completa:
            guardar_configuracion(config_completa, tipo_escenario)

    except Exception as e:
        print(f"\n❌ Error de API/Red: {e}")

def escenario_a_vlans():
    print("\n--- Escenario A: VLANs y Trunking ---")
    while True:
        try:
            id_vlan = int(input("Ingresa el ID de la VLAN (1-4094): "))
            if 1 <= id_vlan <= 4094:
                break
            print("⚠️ Error: El ID de la VLAN debe estar entre 1 y 4094.")
        except ValueError:
            print("⚠️ Error: Debes ingresar un número entero.")
            
    nombre_vlan = input("Ingresa el nombre de la VLAN: ")
    puerto_acceso = input("Ingresa el puerto de acceso (ej: FastEthernet0/1): ")
    puerto_trunk = input("Ingresa el puerto Trunk (ej: GigabitEthernet0/1): ")
    
    prompt = f"Crea la configuración Cisco IOS para la VLAN {id_vlan} llamada {nombre_vlan}, asígnala en modo acceso al puerto {puerto_acceso}, y configura el puerto {puerto_trunk} en modo trunk."
    generar_configuracion(prompt, "A")

def escenario_b_ospf():
    print("\n--- Escenario B: Configuración OSPF ---")
    while True:
        try:
            id_proceso = int(input("Ingresa el ID del proceso OSPF (1-65535): "))
            if 1 <= id_proceso <= 65535:
                break
            print("⚠️ Error: El ID debe estar entre 1 y 65535.")
        except ValueError:
            print("⚠️ Error: Debes ingresar un número entero.")
            
    red = input("Ingresa la red a anunciar con su wildcard (ej: 192.168.1.0 0.0.0.255): ")
    
    while True:
        try:
            area = int(input("Ingresa el ID del área OSPF: "))
            if area >= 0:
                break
            print("⚠️ Error: El área no puede ser negativa.")
        except ValueError:
            print("⚠️ Error: Debes ingresar un número entero.")
            
    prompt = f"Genera la configuración Cisco IOS para el proceso OSPF {id_proceso}, anunciando la red {red} en el área {area}."
    generar_configuracion(prompt, "B")

def escenario_c_subnetting():
    print("\n--- Escenario C: Subnetting y Asignación de IP ---")
    red_base = input("Ingresa la red base (ej: 192.168.1.0): ")
    
    while True:
        try:
            prefijo = int(input("Ingresa el prefijo actual (8-30): "))
            if 8 <= prefijo <= 30:
                break
            print("⚠️ Error: El prefijo debe estar entre /8 y /30.")
        except ValueError:
            print("⚠️ Error: Debes ingresar un número entero.")
            
    while True:
        try:
            subredes = int(input("Ingresa la cantidad de subredes requeridas: "))
            if subredes > 0:
                break
            print("⚠️ Error: Debe ser mayor a 0.")
        except ValueError:
            print("⚠️ Error: Debes ingresar un número entero.")
            
    interfaz = input("Ingresa la interfaz a configurar (ej: GigabitEthernet0/0): ")
    
    prompt = f"Haz subnetting a la red {red_base}/{prefijo} para obtener {subredes} subredes. Muestra SOLO la configuración Cisco IOS para asignar la primera IP útil de la primera subred obtenida a la interfaz {interfaz} y encenderla."
    generar_configuracion(prompt, "C")

def main():
    while True:
        print("\n" + "="*45)
        print(" GENERADOR DE CONFIGURACIONES CISCO IOS")
        print("="*45)
        print("1. Escenario A - VLANs y Trunking")
        print("2. Escenario B - OSPF")
        print("3. Escenario C - Subnetting e Interfaces")
        print("4. Salir")
        
        opcion = input("\nElige una opción (1-4): ")
        
        if opcion == '1':
            escenario_a_vlans()
        elif opcion == '2':
            escenario_b_ospf()
        elif opcion == '3':
            escenario_c_subnetting()
        elif opcion == '4':
            print("Saliendo del programa... ¡Nos vemos!")
            break
        else:
            print("⚠️ Opción no válida.")

if __name__ == "__main__":
    main()