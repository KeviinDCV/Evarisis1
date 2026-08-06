; =====================================================================
;  ONCONOVA — Instalador de Windows
;  Generado para Inno Setup 6. Lo invoca build_tools\construir_instalador.py,
;  que le pasa las rutas y la version por linea de comandos.
; =====================================================================
;
;  QUE RESUELVE
;  ------------
;  Hasta ahora "instalar" era copiar a mano la carpeta dist\ y editar el
;  config.ini en cada PC. Esto instala y deja el programa FUNCIONANDO: escribe
;  el config ya relleno con el servidor y las credenciales, crea accesos
;  directos y registra un desinstalador.
;
;  DONDE INSTALA, Y POR QUE NO EN "Program Files"
;  ----------------------------------------------
;  La aplicacion escribe su log junto al ejecutable, y el config.ini tiene que
;  poder editarse despues (cambiar la IP del servidor, por ejemplo). En
;  Program Files un usuario estandar no puede escribir, asi que el programa
;  fallaria de formas confusas. Se instala en C:\ONCONOVA y se le da permiso
;  de modificacion al grupo Usuarios sobre esa carpeta.
; =====================================================================

#ifndef MiVersion
  #define MiVersion "6.9.92"
#endif
#ifndef MiRaiz
  #define MiRaiz ".."
#endif
#ifndef MiSalida
  #define MiSalida "..\dist_instalador"
#endif
#ifndef MiRol
  #define MiRol "consulta"
#endif
#ifndef MiServidorIp
  #define MiServidorIp "192.168.2.172"
#endif
#ifndef MiPuertoBD
  #define MiPuertoBD "3306"
#endif

[Setup]
; AppId FIJO: es lo que permite que una version nueva ACTUALICE la anterior
; en vez de instalarse al lado. No cambiarlo nunca.
AppId={{8F3C1A64-2D7B-4E59-9C10-7A5E3B02D9F4}
AppName=ONCONOVA — Gestor Oncológico HUV
AppVersion={#MiVersion}
AppVerName=ONCONOVA {#MiVersion}
AppPublisher=Hospital Universitario del Valle — Área de Oncología Quirúrgica
DefaultDirName={sd}\ONCONOVA
DisableDirPage=no
DefaultGroupName=ONCONOVA
OutputDir={#MiSalida}
OutputBaseFilename=ONCONOVA_{#MiVersion}_{#MiRol}_setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Hace falta admin para escribir en C:\ y para fijar los permisos de la carpeta
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=ONCONOVA — Gestor Oncológico HUV
; Si el programa esta abierto, avisa en vez de dejar ficheros a medias
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "{#MiRaiz}\dist\GestorOncologia.exe"; DestDir: "{app}"; Flags: ignoreversion
; config.ini YA RELLENO — esto es lo que evita tener que editar nada
Source: "{#MiRaiz}\dist_instalador\config_generado.ini"; DestDir: "{app}\config"; DestName: "config.ini"; Flags: ignoreversion
Source: "{#MiRaiz}\docs\DESPLIEGUE_LAN.md"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Permiso de escritura para Usuarios: el programa escribe su log aqui y el
; config debe poder editarse sin ser administrador.
Name: "{app}"; Permissions: users-modify
Name: "{app}\config"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify

[Icons]
Name: "{group}\ONCONOVA"; Filename: "{app}\GestorOncologia.exe"
Name: "{group}\Guía de despliegue"; Filename: "{app}\DESPLIEGUE_LAN.md"
Name: "{group}\Desinstalar ONCONOVA"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ONCONOVA"; Filename: "{app}\GestorOncologia.exe"; Tasks: iconoescritorio

[Tasks]
Name: "iconoescritorio"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\GestorOncologia.exe"; Description: "Abrir ONCONOVA ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; El log lo crea la aplicacion, no el instalador: hay que borrarlo aparte o
; queda una carpeta huerfana tras desinstalar.
Type: files; Name: "{app}\debug_psa.log"
Type: dirifempty; Name: "{app}\config"
Type: dirifempty; Name: "{app}\data"
Type: dirifempty; Name: "{app}"

[Code]
// Comprueba que el servidor responde ANTES de terminar la instalacion. Sin
// esto, el usuario descubre que no hay conexion la primera vez que abre el
// programa y ve una tabla vacia sin saber por que.
function ServidorResponde(Ip: String; Puerto: String): Boolean;
var
  Codigo: Integer;
begin
  Result := False;
  // PowerShell devuelve 0 si el puerto acepta conexion
  if Exec('powershell.exe',
          '-NoProfile -Command "if ((Test-NetConnection -ComputerName ' + Ip +
          ' -Port ' + Puerto + ' -InformationLevel Quiet)) { exit 0 } else { exit 1 }"',
          '', SW_HIDE, ewWaitUntilTerminated, Codigo) then
    Result := (Codigo = 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Ip, Puerto: String;
  Aviso: String;
begin
  if CurStep = ssPostInstall then
  begin
    Ip := '{#MiServidorIp}';
    Puerto := '{#MiPuertoBD}';
    if not ServidorResponde(Ip, Puerto) then
    begin
      Aviso := 'ONCONOVA quedó instalado, pero NO se pudo contactar con el servidor ' +
               Ip + ' en el puerto ' + Puerto + '.' + #13#10 + #13#10 +
               'Comprueba en el servidor:' + #13#10 +
               '  · Que la PC esté encendida y MySQL en marcha' + #13#10 +
               '  · Que el firewall permita el puerto ' + Puerto + ' en perfil Privada' + #13#10 +
               '  · Que la IP siga siendo ' + Ip + #13#10 + #13#10 +
               'El programa se abrirá igual, pero mostrará la tabla vacía hasta que ' +
               'haya conexión.';
      MsgBox(Aviso, mbError, MB_OK);
    end;
  end;
end;
