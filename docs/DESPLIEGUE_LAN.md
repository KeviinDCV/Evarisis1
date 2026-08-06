# Despliegue en la LAN — una PC lo sirve todo

**V6.9.93.** Tu PC es el servidor de las dos cosas: **MySQL** (la base de datos)
y **LM Studio** (la IA). Los demás equipos instalan la aplicación y la usan
contra tu máquina. Lo que cambies aquí lo ven allí al instante, porque no hay
copia: hay una sola base de datos.

```
                        ┌──────────────────────────────┐
   PC clínico  ────────►│  TU PC — 192.168.2.172       │
   PC consulta ────────►│    MySQL      puerto 3306    │
   PC gestión  ────────►│    LM Studio  puerto 1234    │
                        └──────────────────────────────┘
```

---

## Estado verificado hoy

| | Situación |
|---|---|
| IP de tu PC | `192.168.2.172` — **asignada por DHCP** ⚠️ |
| MySQL (3306) | escucha en `::` → **ya acepta la LAN** |
| LM Studio (1234) | escucha en `127.0.0.1` → **solo tu máquina** ⚠️ |
| Cuentas MySQL | solo `root`/`pma` locales, **las cuatro sin contraseña** ⚠️ |

Nada de esto es un fallo del programa: son tres interruptores del entorno.

---

## En TU PC (el servidor) — se hace una vez

### 1. Fija la IP

Es lo primero porque todo lo demás cuelga de ella. Ahora mismo la da el router
por DHCP: **el día que cambie, todos los clientes dejan de funcionar a la vez**,
y el síntoma será «no conecta» sin más pista.

Reserva `192.168.2.172` para la MAC de tu equipo en el router, o pásala a
estática. Si tiene que cambiar, hay que reeditar el `config.ini` de cada PC.

### 2. Crea las cuentas de base de datos

Hoy no existe ninguna cuenta que pueda entrar desde otra máquina — por eso
ningún cliente conecta aunque abras el firewall. Y las cuatro que hay no tienen
contraseña.

```bash
mysql -u root < docs\mysql_multiusuario_LAN.sql
```

Antes de ejecutarlo, sustituye los dos marcadores `<<<PON_AQUI_UNA_CONTRASEÑA>>>`.
Crea dos roles de mínimo privilegio:

| Cuenta | Permisos | Para quién |
|---|---|---|
| `huv_consulta` | SELECT | mira, filtra y exporta |
| `huv_captura` | SELECT, INSERT, UPDATE | además importa PDFs y corrige casos |

Ninguna lleva CREATE, ALTER, DROP ni DELETE. Sin DROP no puede dispararse el
`TRUNCATE` de la resincronización, que es lo que podría vaciarle las tablas a
otro usuario mientras lee.

### 3. Pon a LM Studio a servir en la red

Ahora escucha solo en `127.0.0.1`, así que **los clientes no lo alcanzan**. En
LM Studio → pestaña *Developer* / *Local Server* → activa **«Serve on Local
Network»**. El puerto sigue siendo 1234.

Comprueba que cambió:

```bash
netstat -an | findstr :1234
```

Debe aparecer `0.0.0.0:1234` en vez de `127.0.0.1:1234`.

Y deja el modelo **cargado**: si LM Studio está abierto pero sin modelo, los
clientes esperan y fallan uno a uno.

### 4. Abre los dos puertos en el firewall

```powershell
New-NetFirewallRule -DisplayName "ONCONOVA MySQL"    -Direction Inbound -LocalPort 3306 -Protocol TCP -Action Allow -Profile Private
New-NetFirewallRule -DisplayName "ONCONOVA LM Studio" -Direction Inbound -LocalPort 1234 -Protocol TCP -Action Allow -Profile Private
```

**Perfil `Private`, no `Any`.** Si el equipo se lleva a una red pública, esos
puertos no deben quedar abiertos.

---

## En CADA PC cliente

1. Copia la carpeta `dist\` completa.
2. Renombra `config.ini.cliente` a `config\config.ini` y **pon la contraseña**.
   Elige el usuario según el rol: `huv_consulta` o `huv_captura`.
3. Instala Tesseract si vas a procesar PDF escaneados. Si no lo instalas la app
   arranca igual: solo falla el OCR de escaneados, porque el corpus se lee por
   la capa de texto nativa del PDF.
4. Doble clic en `GestorOncologia.exe`.

La plantilla ya viene apuntando a tu PC para las dos cosas:

```ini
[database]
host = 192.168.2.172
usar_modelo_relacional = false     ; que resincronice solo el servidor

[llm]
provider = lm_studio
base_url = http://192.168.2.172:1234/v1
usar_ia_polaridad = true
```

> El `config.ini` que manda es el que está **al lado del .exe**, no el que viaja
> empaquetado dentro. Hasta la V6.9.93 eso solo valía para la base de datos y
> los interruptores de IA quedaban congelados; ya no.

---

## Por qué la IA aceptaba solo `localhost`, y qué se cambió

Las capas de IA que ven texto de informes tenían una guarda anti-nube: si el
endpoint no era `localhost`, **se negaban a llamar**. Correcto mientras el
modelo corría en la misma máquina; pero en este esquema habría dejado la IA
apagada en todos los clientes, sin avisar.

La regla vive ahora en `core/red_local.py` y es una sola para todas las capas:
se aceptan las direcciones **privadas** (`10.x`, `172.16-31.x`, `192.168.x`,
loopback), que no son enrutables en internet, y se sigue rechazando cualquier
destino público — `openrouter.ai`, `api.openai.com`, `8.8.8.8`.

Para un host que no sea loopback hay que escribir **una IP, no un nombre de
máquina**: un nombre como `SERVIDOR` parece local, pero con un dominio de
búsqueda mal configurado puede resolver a cualquier sitio.

---

## Lo que hay que saber antes de repartirlo

**Tu PC tiene que estar encendida**, con LM Studio abierto y el modelo cargado.
Si la apagas, todos se quedan sin base de datos y sin IA a la vez.

**La IA se pone en cola.** Es una GPU sirviendo a varios. Con el consenso
activado son 2 llamadas por lote de 8 marcadores. Está medido en este proyecto
que 2.077 casos tardan unas 9 h a un hilo — y que **subir a 4 hilos fue peor**,
no mejor. Si dos personas importan a la vez, se suman sus tiempos. Para lotes
grandes, mejor por turnos.

**El tráfico va sin cifrar.** MySQL tiene `have_ssl = DISABLED`: usuario,
contraseña y el contenido de los informes viajan legibles por la LAN. Dentro de
la red del hospital es discutible frente a la Ley 1581; fuera del perímetro no
es aceptable sin túnel.

**No hay trazabilidad.** La tabla no tiene columna de usuario ni de fecha de
modificación. Con varias personas editando **no se puede saber quién cambió un
dato clínico**. Para un sistema que maneja historias clínicas, eso acabará
haciendo falta.

**Los clientes consultan, pero no pueden auditar.** Los `debug_maps` (340 MB) y
los PDF de origen (7 GB) están solo en el disco de quien importó. Lo que se
comparte es la base de datos, no los ficheros.

---

## Cuando toque el acceso desde fuera

Ya tienes **Tailscale** instalado en esta máquina (`100.72.222.24`). Es el
camino limpio para eso: red cifrada de extremo a extremo, sin abrir un solo
puerto a internet, y sin depender de que TI del hospital monte una VPN.

⚠️ **Un detalle que hay que tocar cuando llegue el momento:** Tailscale usa el
rango `100.64.0.0/10`, que Python **no** clasifica como privado. La guarda de
`core/red_local.py` lo rechaza hoy, así que la IA quedaría apagada sobre
Tailscale. Es una línea, pero hay que hacerla a conciencia: ese rango también lo
usan los operadores para CGNAT, así que aceptarlo a ciegas es más flojo que
aceptar `192.168.x`.

Y sigue en pie lo legal: los datos de salud son categoría sensible en la Ley
1581, y el acceso desde fuera del hospital necesita aval del responsable del
tratamiento, no solo que funcione.
