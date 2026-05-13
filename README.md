# Generador de Configuraciones Cisco IOS con IA

Herramienta de consola en Python que genera configuraciones Cisco IOS reales a partir de escenarios de red descritos por el usuario, usando la API de Groq con streaming en tiempo real.

 Integrantes

| Nombre | Rol |
|--------|-----|
| [Vicente Galvez] | Desarrollo escenarios A y B, validaciones |
| [Vicente Galvez] | Desarrollo escenarios C y D, persistencia |
| [Vicente Galvez] | System prompt, manejo de errores, README |

Instalación

1. Clona el repositorio:
   bash
   git clone https://github.com/vcntsu/eval-cisco-groq-galvez.git
   cd eval-cisco-groq-galvez
   

2. Crea y activa el entorno virtual:

   python -m venv venv
   # Windows
   venv\Scripts\activate
   

3. Instala las dependencias:
   
   pip install -r requirements.txt
   

4. Configura tu API Key:
   
   cp .env.example .env
   # Edita .env y agregar GROQ_API_KEY=
   

5. Ejecuta la aplicación:
   
   python cisco_config_gen.py
   
Escenarios soportados

Escenario A — VLANs y Trunking
Configura múltiples VLANs con nombre y puertos de acceso en un switch capa 2, más un puerto trunk.

Ejemplo de uso:

¿Cuántas VLANs deseas configurar? 2
VLAN 1:
  ID de VLAN: 10
  Nombre: VENTAS
  Puerto de acceso: FastEthernet0/1
VLAN 2:
  ID de VLAN: 20
  Nombre: RRHH
  Puerto de acceso: FastEthernet0/2
Puerto Trunk: GigabitEthernet0/1

Escenario B — OSPF
Configura el proceso OSPF con múltiples redes y áreas.

Ejemplo de uso:

ID del proceso OSPF: 1
¿Cuántas redes deseas anunciar? 2
Red 1:
  Red con wildcard: 192.168.1.0 0.0.0.255
  Área OSPF: 0
Red 2:
  Red con wildcard: 10.0.0.0 0.0.0.255
  Área OSPF: 1


Escenario C — Subnetting e Interfaces
Realiza subnetting sobre una red base y asigna la primera IP útil de cada subred a interfaces secuenciales.


Red base: 192.168.1.0
Prefijo: 24
Cantidad de subredes: 4
Interfaz: GigabitEthernet0/0

Escenario D — Servidor DHCP (Bonus)
Configura un pool DHCP con exclusiones y DNS opcionales.

Ejemplo de uso:

Nombre del pool: LAN_VENTAS
Red: 192.168.20.0
Máscara: 255.255.255.0
Gateway: 192.168.20.1
DNS: 8.8.8.8
Excluir: 192.168.20.1 192.168.20.10


Justificación de parámetros del modelo

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| `model` | `llama-3.3-70b-versatile` | Modelo activo y de alta calidad, genera configuraciones Cisco IOS más precisas y completas |
| `temperature` | `0.1` | Valor bajo para respuestas determinísticas y reproducibles. Las configuraciones de red no deben variar entre ejecuciones con los mismos datos |
| `max_tokens` | `1200` | Suficiente para configuraciones con múltiples VLANs, redes OSPF o subredes sin truncar la salida |
| `stream` | `True` | Muestra la configuración en tiempo real mientras se genera, mejorando la experiencia de usuario |



Limitaciones conocidas

- La validación de IP es básica (formato y rango de octetos). No verifica si la red es una dirección de host o broadcast.
- El modelo puede ocasionalmente incluir texto explicativo a pesar del system prompt restrictivo. Se recomienda revisar la salida antes de aplicarla en producción.
- El escenario C delega el cálculo de subredes al modelo; para subnetting crítico se recomienda verificar con una herramienta dedicada.
- No se valida que el wildcard ingresado en OSPF sea coherente con la red.
- Las configuraciones generadas son para fines educativos. Siempre valida en un entorno de laboratorio antes de aplicar en producción.
