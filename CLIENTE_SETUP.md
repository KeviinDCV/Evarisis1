# 🏥 EVARISIS Gestor Oncología — Setup Cliente HUV (V6.9.0)

## Para administradores: compilar el .exe

Desde la PC servidor (con todo el código fuente):

```cmd
cd C:\ruta\al\proyecto
COMPILADOR.bat
```

Esto genera en `dist\`:
- `GestorOncologia.exe` — el ejecutable
- `config\config.ini` — **archivo de configuración EDITABLE**
- `data\` — carpeta para BD SQLite local (si se usa modo offline)
- `pdfs_patologia\` — carpeta para que el usuario meta los PDFs

Distribuye toda la carpeta `dist\` a cada PC cliente (vía red, USB, o instalador).

---

## Para usuarios finales: instalación en cada PC del HUV

### Requisitos previos
- Windows 10 o superior
- Acceso a la red LAN del HUV
- Tesseract OCR instalado (`C:\Program Files\Tesseract-OCR\tesseract.exe`)

### Pasos

1. **Copiar la carpeta** `dist\` a la PC del usuario (recomendado: `C:\HUV_Oncologia\`)

2. **Editar `config\config.ini`** con un editor de texto (Notepad, VS Code):

   ```ini
   [database]
   tipo = mysql
   host = 192.168.2.172    ; <-- IP del servidor (XAMPP)
   puerto = 3306
   usuario = huv_app
   password = huv2026      ; <-- Cambiar por el password real
   base_datos = huv_oncologia
   charset = utf8mb4
   ```

   **Solo necesitan cambiar el `host`** si el servidor tiene otra IP.

3. **Doble click en `GestorOncologia.exe`**

4. La app se conecta automáticamente al servidor MySQL y muestra los datos compartidos.

---

## Configuración del servidor MySQL (XAMPP)

### En la PC servidor (esta máquina, IP 192.168.2.172)

1. **XAMPP debe estar instalado** con MySQL/MariaDB corriendo.

2. **BD y usuario ya creados** (V6.9.0):
   - BD: `huv_oncologia`
   - Usuario: `huv_app`
   - Password: `huv2026`
   - Acceso: `localhost` + `%` (cualquier IP de la LAN)

3. **Firewall**: permitir entrada TCP puerto **3306** para LAN:
   - Panel de control → Firewall de Windows Defender → Reglas de entrada
   - Nueva regla → Puerto → TCP 3306 → Permitir conexión
   - Aplicar a perfil **Privada** (LAN del hospital)
   - Nombre: `MySQL HUV Oncologia`

4. **Verificar conexión desde otra PC** de la red:
   ```cmd
   telnet 192.168.2.172 3306
   ```
   Si conecta → puerto abierto, los clientes pueden acceder.

---

## Modo offline (single-user con SQLite)

Si una PC necesita trabajar SIN red (campo, presentación, etc.), basta cambiar en `config.ini`:

```ini
[database]
tipo = sqlite
archivo = data/huv_oncologia_NUEVO.db
```

Los datos se guardan localmente en `data\huv_oncologia_NUEVO.db`. No se comparten con otros usuarios.

Para volver a modo compartido: cambiar `tipo = mysql` y reiniciar la app.

---

## Backup automático (recomendado en producción)

En la PC servidor, crear tarea programada nocturna con `mysqldump`:

```cmd
C:\xampp\mysql\bin\mysqldump.exe -u root --databases huv_oncologia > "D:\Backups\huv_%date:~6,4%%date:~3,2%%date:~0,2%.sql"
```

Programar en el **Programador de Tareas de Windows** para que corra todos los días a las 02:00 AM.

---

## Troubleshooting

### "Can't connect to MySQL server"
- Verificar que XAMPP esté corriendo en el servidor (panel MySQL = Running)
- Verificar firewall (puerto 3306 abierto)
- Verificar IP correcta en `config.ini`
- Probar `ping 192.168.2.172` desde la PC cliente

### "Access denied for user 'huv_app'"
- Verificar password en `config.ini`
- Si se cambió el password en MySQL, actualizar `config.ini` en TODAS las PCs

### "Table doesn't exist"
- La primera vez que se abre la app crea automáticamente las tablas
- Si falla, abrir phpMyAdmin (`http://192.168.2.172/phpmyadmin`) y verificar que BD `huv_oncologia` exista

### Datos no se ven en tiempo real entre PCs
- Refrescar el Visualizador (botón "Refrescar")
- Verificar que ambas PCs apunten al MISMO `host` en config.ini
- En phpMyAdmin verificar que los registros estén en `informes_ihq`

---

## Cambiar el password de `huv_app` (producción)

⚠️ El password `huv2026` es de prueba. Para producción:

1. En phpMyAdmin (`http://localhost/phpmyadmin`):
   - Cuentas de usuario → `huv_app` → Editar privilegios → Cambiar contraseña
   - Generar password fuerte (16+ caracteres con símbolos)

2. **Actualizar `config.ini`** en TODAS las PCs cliente con el nuevo password.

3. Reiniciar la app en cada PC.

---

## Cambiar IP del servidor

Si la PC servidor cambia de IP:

1. **En el servidor**: verificar nueva IP con `ipconfig`
2. **En cada PC cliente**: editar `config.ini` → cambiar `host = NUEVA_IP`
3. Reiniciar la app

Para evitar este lío, recomiendo configurar **IP fija** en el router del HUV para la PC servidor.

---

## Soporte

- Logs de la app: `dist\debug_psa.log`
- BD admin: phpMyAdmin en `http://192.168.2.172/phpmyadmin`
- Para reportar problemas: contactar al equipo de Innovación y Desarrollo del HUV.
