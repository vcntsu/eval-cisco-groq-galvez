import os
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

def generar_configuracion(prompt_usuario):
    """Función para llamar a Groq y generar la configuración con streaming"""
    try:
        print("\n⏳ Generando configuración...\n")
        # Parámetros exigidos por la pauta: temperature <= 0.2, max_tokens >= 800, stream=True
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
        # Consumo iterativo de chunks para mostrar en tiempo real
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                contenido = chunk.choices[0].delta.content
                print(contenido, end="")
                config_completa += contenido
        
        print("\n\n✅ Generación completada.")
        return config_completa

    except Exception as e:
        print(f"\n❌ Error de API/Red: {e}")
        return None

def main():
    """Función principal y lectura de entrada"""
    print("=== Generador de Configuraciones Cisco IOS ===")
    print("1. Escenario de prueba libre")
    
    opcion = input("\nElige una opción (1) o escribe 'salir': ")
    
    if opcion == '1':
        entrada_usuario = input("Describe qué necesitas configurar (ej: Crea 3 VLANs): ")
        generar_configuracion(entrada_usuario)
    else:
        print("Saliendo del programa...")

if __name__ == "__main__":
    main()