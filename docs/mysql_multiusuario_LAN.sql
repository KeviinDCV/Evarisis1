-- =====================================================================
--  ONCONOVA — Preparar MySQL/MariaDB para varios usuarios en la LAN
--  V6.9.93
-- =====================================================================
--
--  POR QUÉ HACE FALTA ESTO
--  -----------------------
--  Hoy el servidor SOLO tiene estas cuentas, y las cuatro SIN contraseña:
--
--      pma  @ localhost      root @ localhost
--      root @ 127.0.0.1      root @ ::1
--
--  No existe ninguna cuenta con host de LAN, así que MySQL rechaza por
--  diseño cualquier conexión desde otra PC — aunque se abra el firewall.
--  Ese, y no el firewall, es el bloqueante real del multiusuario.
--
--  (El fichero dist/CLIENTE_SETUP.md documenta un usuario `huv_app` con
--   contraseña `huv2026` como si existiera. NUNCA se creó. Y esa
--   contraseña está en claro en un documento que viaja a cada PC cliente:
--   no la reutilices.)
--
--  CÓMO USAR ESTE FICHERO
--  ----------------------
--  1. Sustituye los dos marcadores  <<<PON_AQUI_UNA_CONTRASEÑA>>>  por
--     contraseñas reales, distintas entre sí. No las escribas en ningún
--     chat ni las subas al repositorio.
--  2. Ajusta la subred si la del hospital no es 192.168.2.x
--  3. Ejecútalo como root desde la PC servidor:
--         mysql -u root < docs\mysql_multiusuario_LAN.sql
--  4. Pon esas contraseñas en el config.ini de cada PC cliente.
--
--  DOS ROLES, A PROPÓSITO
--  ----------------------
--  Nadie debería conectarse como root desde otra máquina. Se crean dos
--  cuentas con el mínimo que la aplicación necesita de verdad:
--
--    huv_consulta  → SELECT. Para quien solo mira, filtra y exporta.
--    huv_captura   → SELECT, INSERT, UPDATE. Para quien además importa
--                    PDFs y corrige casos.
--
--  Ninguna lleva CREATE, ALTER, DROP ni DELETE. Eso es deliberado:
--    · Sin ALTER, un .exe viejo no puede reintroducir columnas retiradas
--      ni crearlas como VARCHAR(500) donde el esquema quiere TEXT.
--    · Sin DROP no puede ejecutarse el TRUNCATE del modelo relacional,
--      que es el que podría vaciar tablas mientras otro usuario lee.
--
--  Para que eso funcione hacen falta DOS COSAS en el cliente (ver abajo).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) Cuenta de SOLO CONSULTA
-- ---------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'huv_consulta'@'192.168.2.%'
    IDENTIFIED BY '<<<PON_AQUI_UNA_CONTRASEÑA>>>';

GRANT SELECT ON huv_oncologia.* TO 'huv_consulta'@'192.168.2.%';

-- ---------------------------------------------------------------------
-- 2) Cuenta de CAPTURA (importar PDFs y corregir casos)
-- ---------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'huv_captura'@'192.168.2.%'
    IDENTIFIED BY '<<<PON_AQUI_OTRA_CONTRASEÑA>>>';

GRANT SELECT, INSERT, UPDATE ON huv_oncologia.* TO 'huv_captura'@'192.168.2.%';

FLUSH PRIVILEGES;

-- ---------------------------------------------------------------------
-- 3) Comprobación
-- ---------------------------------------------------------------------
SELECT user, host,
       IF(LENGTH(authentication_string) > 0, 'con contraseña', '*** SIN CONTRASEÑA ***') AS clave
FROM mysql.user
ORDER BY user, host;

SHOW GRANTS FOR 'huv_consulta'@'192.168.2.%';
SHOW GRANTS FOR 'huv_captura'@'192.168.2.%';


-- =====================================================================
--  LO QUE HAY QUE PONER EN EL config.ini DE CADA PC CLIENTE
-- =====================================================================
--
--      [database]
--      tipo = mysql
--      host = 192.168.2.172          ; la PC servidor, no 127.0.0.1
--      puerto = 3306
--      usuario = huv_consulta        ; o huv_captura, según el rol
--      password = (la que hayas puesto arriba)
--      base_datos = huv_oncologia
--      charset = utf8mb4
--
--      ; IMPRESCINDIBLE en los clientes: el modelo relacional resincroniza
--      ; haciendo TRUNCATE de cuatro tablas, y con dos usuarios a la vez uno
--      ; puede quedarse leyendo tablas vacías sin ningún error. Que
--      ; resincronice SOLO el servidor.
--      usar_modelo_relacional = false
--
--  Ojo: en el .exe el config.ini que manda es el que está AL LADO del
--  ejecutable, no el que va empaquetado dentro.
--
--
--  LO QUE SIGUE PENDIENTE, Y CONVIENE NO OLVIDAR
--  --------------------------------------------
--  · root sigue SIN CONTRASEÑA en las cuatro cuentas locales. Este script
--    no la pone a propósito: cambiarla rompe la aplicación del servidor
--    hasta que se actualice su propio config.ini, y esa es una decisión
--    tuya, no algo que deba pasar de refilón.
--        ALTER USER 'root'@'localhost' IDENTIFIED BY '...';   -- y las otras tres
--
--  · have_ssl = DISABLED. Hoy la sesión NO puede cifrarse ni aunque el
--    cliente lo pida: usuario, contraseña y el contenido de los informes
--    (nombre, cédula, diagnóstico) viajan legibles por la red. Dentro de
--    la LAN del hospital es discutible frente a la Ley 1581; fuera del
--    perímetro es inaceptable sin túnel.
--
--  · No hay trazabilidad. La tabla no tiene columna de usuario ni de fecha
--    de modificación, así que con varias personas editando no se puede
--    saber quién cambió un dato clínico. Para un sistema que maneja
--    historias clínicas, eso acabará haciendo falta.
--
--  · La PC servidor tiene que estar encendida. Hoy es además el equipo de
--    desarrollo, el que guarda los 7 GB de PDFs y el que corre LM Studio.
--
--  · Los usuarios remotos podrán CONSULTAR pero no auditar: los
--    debug_maps (340 MB) y los PDF de origen (7 GB) solo existen en el
--    disco de quien importó.
-- =====================================================================
