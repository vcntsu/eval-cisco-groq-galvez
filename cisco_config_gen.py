import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from groq import APIConnectionError, AuthenticationError, RateLimitError

# Cargar variables de entorno
load_dotenv()

# ─── Validar API Key antes de continuar ───────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("Error: GROQ_API_KEY no encontrada. Configúrala en tu archivo .env")
    sys.exit(1)

client = Groq(api_key=api_key)

# ─── System prompt especializado ──────────────────────────────────────────────
SYSTEM_PROMPT = (
    "Eres un ingeniero de redes Cisco experto. "
    "Tu ÚNICA tarea es generar configuraciones Cisco IOS válidas. "
    "REGLAS ESTRICTAS:\n"
    "1. Devuelve SOLO comandos Cisco IOS en bloque, listos para copiar y pegar.\n"
    "2. Puedes usar comentarios IOS (líneas que empiezan con !) para separar secciones.\n"
    "3. PROHIBIDO incluir explicaciones, saludos, advertencias o cualquier texto fuera de comandos IOS.\n"
    "4. No uses bloques de código markdown (``` o similar).\n"
    "5. Comienza directamente con el primer comando."
)

# ─── Utilidades ───────────────────────────────────────────────────────────────

def validar_ip(ip: str) -> bool:
    """Valida formato básico de IPv4."""
    patron = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(patron, ip):
        return False
    return all(0 <= int(octeto) <= 255 for octeto in ip.split("."))


def guardar_configuracion(config_texto: str, tipo_escenario: str) -> None:
    """Guarda la configuración en /configs/ con timestamp."""
    os.makedirs("configs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"configs/escenario_{tipo_escenario}_{timestamp}.txt"
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(config_texto)
        print(f"\n Configuración guardada en: {nombre_archivo}")
    except OSError as e:
        print(f"\n  No se pudo guardar el archivo: {e}")


def generar_configuracion(prompt_usuario: str, tipo_escenario: str) -> None:
    """Llama a la API de Groq con streaming y guarda el resultado."""
    print("\n Generando configuración...\n")
    print("-" * 45)
    try:
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,   # Bajo para respuestas determinísticas (configs reproducibles)
            max_tokens=1200,   # Suficiente para configs con múltiples VLANs/redes
            stream=True,
        )

        config_completa = ""
        for chunk in stream:
            contenido = chunk.choices[0].delta.content
            if contenido:
                print(contenido, end="", flush=True)
                config_completa += contenido

        print("\n" + "-" * 45)
        print("Generación completada.")

        if config_completa.strip():
            guardar_configuracion(config_completa, tipo_escenario)

    except AuthenticationError:
        print("API Key inválida o sin permisos. Verifica tu GROQ_API_KEY.")
    except RateLimitError:
        print("Rate limit alcanzado (HTTP 429). Espera unos segundos e intenta de nuevo.")
    except APIConnectionError as e:
        print(f"Error de conexión con la API: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


# ─── Escenario A: VLANs y Trunking ───────────────────────────────────────────

def pedir_vlan() -> dict:
    """Solicita datos de una VLAN individual."""
    while True:
        try:
            id_vlan = int(input("  ID de VLAN (1-4094): "))
            if 1 <= id_vlan <= 4094:
                break
            print("El ID debe estar entre 1 y 4094.")
        except ValueError:
            print("Ingresa un número entero.")
    nombre = input("  Nombre de la VLAN: ").strip() or f"VLAN{id_vlan}"
    puerto_acceso = input("  Puerto de acceso (ej: FastEthernet0/1): ").strip()
    return {"id": id_vlan, "nombre": nombre, "puerto_acceso": puerto_acceso}


def escenario_a_vlans() -> None:
    print("\n--- Escenario A: VLANs y Trunking ---")

    while True:
        try:
            cantidad = int(input("¿Cuántas VLANs deseas configurar? (1-10): "))
            if 1 <= cantidad <= 10:
                break
            print("Ingresa un número entre 1 y 10.")
        except ValueError:
            print("Ingresa un número entero.")

    vlans = []
    for i in range(cantidad):
        print(f"\nVLAN {i + 1}:")
        vlans.append(pedir_vlan())

    puerto_trunk = input("\nPuerto Trunk (ej: GigabitEthernet0/1): ").strip()

    # Construir descripción para el prompt
    detalle_vlans = "; ".join(
        f"VLAN {v['id']} nombre '{v['nombre']}' en puerto {v['puerto_acceso']}"
        for v in vlans
    )
    ids_vlans = ",".join(str(v["id"]) for v in vlans)

    prompt = (
        f"Genera la configuración Cisco IOS para un switch capa 2 con las siguientes VLANs: {detalle_vlans}. "
        f"Configura el puerto {puerto_trunk} en modo trunk permitiendo las VLANs {ids_vlans}."
    )
    generar_configuracion(prompt, "A")


# ─── Escenario B: OSPF ────────────────────────────────────────────────────────

def escenario_b_ospf() -> None:
    print("\n--- Escenario B: Configuración OSPF ---")

    while True:
        try:
            id_proceso = int(input("ID del proceso OSPF (1-65535): "))
            if 1 <= id_proceso <= 65535:
                break
            print("El ID debe estar entre 1 y 65535.")
        except ValueError:
            print("Ingresa un número entero.")

    while True:
        try:
            cantidad_redes = int(input("¿Cuántas redes deseas anunciar? (1-10): "))
            if 1 <= cantidad_redes <= 10:
                break
            print("Ingresa un número entre 1 y 10.")
        except ValueError:
            print("Ingresa un número entero.")

    redes = []
    for i in range(cantidad_redes):
        print(f"\nRed {i + 1}:")
        while True:
            red = input("  Red con wildcard (ej: 192.168.1.0 0.0.0.255): ").strip()
            partes = red.split()
            if len(partes) == 2 and validar_ip(partes[0]) and validar_ip(partes[1]):
                break
            print("Formato inválido. Usa: <red> <wildcard>  (ej: 10.0.0.0 0.0.0.255)")
        while True:
            try:
                area = int(input("  Área OSPF (0 o mayor): "))
                if area >= 0:
                    break
                print("El área no puede ser negativa.")
            except ValueError:
                print("Ingresa un número entero.")
        redes.append({"red": partes[0], "wildcard": partes[1], "area": area})

    detalle_redes = "; ".join(
        f"red {r['red']} wildcard {r['wildcard']} área {r['area']}" for r in redes
    )
    prompt = (
        f"Genera la configuración Cisco IOS para el proceso OSPF {id_proceso} "
        f"anunciando las siguientes redes: {detalle_redes}."
    )
    generar_configuracion(prompt, "B")


# ─── Escenario C: Subnetting + Interfaces ────────────────────────────────────

def escenario_c_subnetting() -> None:
    print("\n--- Escenario C: Subnetting y Asignación de IP ---")

    while True:
        red_base = input("Red base (ej: 192.168.1.0): ").strip()
        if validar_ip(red_base):
            break
        print("⚠️  Dirección IP inválida.")

    while True:
        try:
            prefijo = int(input("Prefijo de la red (/8 a /30): "))
            if 8 <= prefijo <= 30:
                break
            print("⚠️  El prefijo debe estar entre /8 y /30.")
        except ValueError:
            print("⚠️  Ingresa un número entero.")

    while True:
        try:
            subredes = int(input("Cantidad de subredes requeridas: "))
            if subredes > 0:
                break
            print("⚠️  Debe ser mayor a 0.")
        except ValueError:
            print("⚠️  Ingresa un número entero.")

    interfaz = input("Interfaz a configurar (ej: GigabitEthernet0/0): ").strip()

    prompt = (
        f"Realiza el subnetting de la red {red_base}/{prefijo} para obtener {subredes} subredes. "
        f"Genera la configuración Cisco IOS para asignar la primera IP útil de cada subred "
        f"a interfaces secuenciales comenzando por {interfaz}, y activa cada interfaz."
    )
    generar_configuracion(prompt, "C")


# ─── Escenario D (Bonus): Servidor DHCP ──────────────────────────────────────

def escenario_d_dhcp() -> None:
    print("\n--- Escenario D (Bonus): Servidor DHCP ---")

    while True:
        nombre_pool = input("Nombre del pool DHCP (ej: LAN_VENTAS): ").strip()
        if nombre_pool:
            break
        print("⚠️  El nombre no puede estar vacío.")

    while True:
        red_base = input("Red a repartir (ej: 192.168.20.0): ").strip()
        if validar_ip(red_base):
            break
        print("⚠️  Dirección IP inválida.")

    while True:
        mascara = input("Máscara de subred (ej: 255.255.255.0): ").strip()
        if validar_ip(mascara):
            break
        print("⚠️  Máscara inválida.")

    while True:
        gateway = input("Default Gateway (ej: 192.168.20.1): ").strip()
        if validar_ip(gateway):
            break
        print("⚠️  IP de gateway inválida.")

    dns = input("Servidor DNS (ej: 8.8.8.8) [Enter para omitir]: ").strip()
    excluidas = input("Rango de IPs a excluir (ej: 192.168.20.1 192.168.20.10) [Enter para omitir]: ").strip()

    prompt = (
        f"Genera la configuración Cisco IOS para un servidor DHCP. "
        f"Pool: '{nombre_pool}', red: {red_base}, máscara: {mascara}, default-router: {gateway}."
    )
    if dns and validar_ip(dns):
        prompt += f" DNS: {dns}."
    if excluidas:
        prompt += f" Excluir IPs: {excluidas}."

    generar_configuracion(prompt, "D")


# ─── Menú principal ───────────────────────────────────────────────────────────

def main() -> None:
    opciones = {
        "1": ("Escenario A - VLANs y Trunking", escenario_a_vlans),
        "2": ("Escenario B - OSPF",              escenario_b_ospf),
        "3": ("Escenario C - Subnetting e Interfaces", escenario_c_subnetting),
        "4": ("Escenario D - Servidor DHCP ", escenario_d_dhcp),
        "5": ("Salir", None),
    }

    while True:
        print("\n" + "=" * 45)
        print("  GENERADOR DE CONFIGURACIONES CISCO IOS")
        print("=" * 45)
        for key, (desc, _) in opciones.items():
            print(f"  {key}. {desc}")

        opcion = input("\nElige una opción (1-5): ").strip()

        if opcion == "5":
            print("Saliendo... ¡Hasta luego!")
            break
        elif opcion in opciones:
            _, funcion = opciones[opcion]
            funcion()
        else:
            print("⚠️  Opción no válida. Elige entre 1 y 5.")


if __name__ == "__main__":
    main()