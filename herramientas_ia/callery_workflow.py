# -*- coding: utf-8 -*-
"""
CALLERY WORKFLOW - Asistente Personal de Auditoria
===================================================

Agente especializado en gestion de workflows de auditoria para multiples casos.

CAPACIDADES v2.0:
1. Iniciar lote de auditorias
2. Ejecutar auditorias secuenciales con actualizacion automatica
3. Consolidar reportes multiples con analisis inteligente
4. Reanudar workflows interrumpidos
5. Mostrar estado de progreso en tiempo real
6. 🆕 Actualizar auditoria_realizada.md automaticamente
7. 🆕 Detectar errores comunes y sugerir soluciones

Version: 2.0.0
Autor: Sistema EVARISIS
Fecha: 2025-12-02

CHANGELOG v2.0.0 (FASE 1):
- ✅ NUEVA: Actualizacion automatica de auditoria_realizada.md
- ✅ NUEVA: Deteccion inteligente de errores comunes
- ✅ NUEVA: Analisis de patrones y sugerencias de correccion
- ✅ MEJORA: Emojis visuales en output (✅ ⚠️)
- ✅ MEJORA: Extraccion metricas mejorada (metricas.score_final)

IMPORTANTE:
- NO modifica extractores (solo detecta problemas)
- NO consulta BD directamente (usa debug_maps via data-auditor)
- NO aplica correcciones automaticas (solo reporta)
- SI gestiona estado persistente de workflows
- SI actualiza auditoria_realizada.md automaticamente (v2.0)
"""

import json
import sys
import os
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics


# ===========================
# CONFIGURACION
# ===========================

VERSION = "2.0.0"
RESULTADOS_DIR = Path("herramientas_ia/resultados")
AUDITOR_PATH = Path("herramientas_ia/auditor_sistema.py")
AUDITORIA_REALIZADA_PATH = Path("auditoria_realizada.md")


# ===========================
# UTILIDADES
# ===========================

def generar_lote_id(num_casos: int) -> str:
    """Genera ID unico para el lote."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"lote_{num_casos}_casos_{timestamp}"


def parsear_casos(casos_str: str) -> List[str]:
    """Parsea string de casos separados por coma."""
    casos = [c.strip().upper() for c in casos_str.split(",")]
    # Validar formato IHQ
    casos_validos = []
    for caso in casos:
        if caso.startswith("IHQ"):
            casos_validos.append(caso)
        else:
            print(f"ADVERTENCIA: '{caso}' no tiene formato IHQ valido, ignorando...")
    return casos_validos


def formatear_duracion(segundos: float) -> str:
    """Formatea duracion en segundos a formato legible."""
    if segundos < 60:
        return f"{int(segundos)}s"
    elif segundos < 3600:
        mins = int(segundos / 60)
        secs = int(segundos % 60)
        return f"{mins}m {secs}s"
    else:
        horas = int(segundos / 3600)
        mins = int((segundos % 3600) / 60)
        return f"{horas}h {mins}m"


def mostrar_barra_progreso(completados: int, total: int, ancho: int = 40) -> str:
    """Genera barra de progreso visual con caracteres ASCII."""
    porcentaje = completados / total if total > 0 else 0
    bloques_llenos = int(ancho * porcentaje)
    bloques_vacios = ancho - bloques_llenos
    barra = "#" * bloques_llenos + "-" * bloques_vacios
    return f"[{barra}] {porcentaje*100:.0f}% ({completados}/{total})"


# ===========================
# FUNCION 1: INICIAR LOTE
# ===========================

def iniciar_lote(casos_str: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Crea archivo de estado inicial para un nuevo lote de auditorias.

    Args:
        casos_str: String con casos separados por coma (ej: "IHQ251014,IHQ251015")

    Returns:
        Tupla (exito, mensaje, datos_lote)
    """
    try:
        # Parsear casos
        casos = parsear_casos(casos_str)
        if not casos:
            return False, "Error: No se proporcionaron casos validos", None

        # Generar ID de lote
        lote_id = generar_lote_id(len(casos))

        # Crear estructura de estado
        estado = {
            "lote_id": lote_id,
            "timestamp_inicio": datetime.now().isoformat(),
            "timestamp_fin": None,
            "usuario": os.environ.get("USERNAME", "USUARIO"),
            "descripcion": f"Auditoria de {len(casos)} casos",
            "casos": [],
            "resumen": {
                "total": len(casos),
                "completados": 0,
                "en_proceso": 0,
                "pendientes": len(casos),
                "fallidos": 0,
                "progreso_porcentaje": 0.0,
                "tiempo_promedio_caso": None,
                "tiempo_estimado_restante": None,
                "promedio_score": None,
                "casos_criticos": []
            },
            "interrupciones": [],
            "version_herramienta": VERSION
        }

        # Agregar cada caso como PENDIENTE
        for caso in casos:
            estado["casos"].append({
                "numero": caso,
                "estado": "PENDIENTE",
                "score": None,
                "timestamp_inicio": None,
                "timestamp_fin": None,
                "duracion_segundos": None,
                "reporte_path": None,
                "errores_criticos": None,
                "warnings": None
            })

        # Crear directorio de resultados si no existe
        RESULTADOS_DIR.mkdir(exist_ok=True)

        # Guardar archivo de estado
        estado_path = RESULTADOS_DIR / f"callery_workflow_{lote_id}.json"
        with open(estado_path, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

        return True, estado_path, estado

    except Exception as e:
        return False, f"Error al iniciar lote: {str(e)}", None


# ===========================
# FUNCION 2: EJECUTAR LOTE
# ===========================

def ejecutar_lote(lote_id: str, modo_reanudar: bool = False) -> Tuple[bool, str]:
    """
    Ejecuta auditorias secuenciales para todos los casos PENDIENTES.

    Args:
        lote_id: ID del lote a procesar
        modo_reanudar: Si es True, reanuda desde casos pendientes

    Returns:
        Tupla (exito, mensaje)
    """
    try:
        # Cargar archivo de estado
        estado_path = RESULTADOS_DIR / f"callery_workflow_{lote_id}.json"
        if not estado_path.exists():
            return False, f"Error: No se encontro el lote '{lote_id}'"

        with open(estado_path, 'r', encoding='utf-8') as f:
            estado = json.load(f)

        # Filtrar casos pendientes
        casos_pendientes = [c for c in estado["casos"] if c["estado"] == "PENDIENTE"]

        if not casos_pendientes:
            return True, "Todos los casos ya fueron procesados"

        print(f"\n{'Reanudando' if modo_reanudar else 'Ejecutando'} workflow de auditoria...")
        print("=" * 60)
        print(f"Lote ID: {lote_id}")
        print(f"Casos pendientes: {len(casos_pendientes)}/{estado['resumen']['total']}")
        print("=" * 60)
        print()

        # Procesar cada caso pendiente
        for idx, caso_info in enumerate(casos_pendientes, 1):
            numero_caso = caso_info["numero"]
            total = len(casos_pendientes)

            # Mostrar progreso
            print(f"[{idx}/{total}] {numero_caso}...", end=" ", flush=True)

            # Timestamp inicio
            inicio = datetime.now()
            caso_info["timestamp_inicio"] = inicio.isoformat()
            caso_info["estado"] = "EN_PROCESO"

            # Actualizar resumen
            estado["resumen"]["en_proceso"] += 1
            estado["resumen"]["pendientes"] -= 1

            # Guardar estado (por si se interrumpe)
            with open(estado_path, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)

            # Invocar auditor_sistema.py
            try:
                resultado = subprocess.run(
                    [sys.executable, str(AUDITOR_PATH), numero_caso, "--inteligente"],
                    capture_output=True,
                    text=True,
                    timeout=180,  # 3 minutos max por caso
                    encoding='utf-8',
                    errors='ignore'  # V2.0: Ignorar errores de encoding
                )

                # Timestamp fin
                fin = datetime.now()
                duracion = (fin - inicio).total_seconds()

                # Buscar reporte generado
                reporte_path = RESULTADOS_DIR / f"auditoria_inteligente_{numero_caso}.json"

                if reporte_path.exists():
                    # Leer reporte para extraer metricas
                    with open(reporte_path, 'r', encoding='utf-8') as f:
                        reporte = json.load(f)

                    # V2.0: Extraer metricas del reporte
                    metricas = reporte.get("metricas", {})
                    score = metricas.get("score_final", 0.0)
                    estado_final = reporte.get("estado_final", "DESCONOCIDO")
                    warnings_count = metricas.get("warnings", 0)
                    errores_count = metricas.get("errores", 0)

                    # V2.0: Analizar errores comunes
                    errores_detectados = analizar_errores_caso(reporte)

                    # Actualizar caso
                    caso_info["estado"] = "COMPLETADO"
                    caso_info["score"] = score
                    caso_info["timestamp_fin"] = fin.isoformat()
                    caso_info["duracion_segundos"] = duracion
                    caso_info["reporte_path"] = str(reporte_path)
                    caso_info["errores_criticos"] = errores_count
                    caso_info["warnings"] = warnings_count
                    caso_info["errores_detectados"] = errores_detectados  # V2.0

                    # Mostrar resultado
                    if score >= 90.0:
                        try:
                            print(f"✅ Score: {score:.1f}% ({duracion:.0f}s)")
                        except:
                            print(f"OK Score: {score:.1f}% ({duracion:.0f}s)")
                    else:
                        try:
                            print(f"⚠️  Score: {score:.1f}% ({duracion:.0f}s)")
                        except:
                            print(f"WARNING Score: {score:.1f}% ({duracion:.0f}s)")

                    # V2.0: Actualizar auditoria_realizada.md automaticamente
                    exito_actualizacion, msg_actualizacion = actualizar_auditoria_realizada(
                        numero_caso, score, estado_final
                    )
                    if not exito_actualizacion:
                        print(f"    (Advertencia: {msg_actualizacion})")

                    # Actualizar resumen
                    estado["resumen"]["completados"] += 1
                    estado["resumen"]["en_proceso"] -= 1

                    if score < 90.0:
                        estado["resumen"]["casos_criticos"].append(numero_caso)

                else:
                    # Error: reporte no generado
                    caso_info["estado"] = "FALLIDO"
                    caso_info["timestamp_fin"] = fin.isoformat()
                    caso_info["duracion_segundos"] = duracion

                    print(f"ERROR (reporte no generado)")

                    estado["resumen"]["fallidos"] += 1
                    estado["resumen"]["en_proceso"] -= 1

            except subprocess.TimeoutExpired:
                print(f"TIMEOUT (>3min)")
                caso_info["estado"] = "FALLIDO"
                caso_info["timestamp_fin"] = datetime.now().isoformat()
                estado["resumen"]["fallidos"] += 1
                estado["resumen"]["en_proceso"] -= 1

            except Exception as e:
                print(f"ERROR ({str(e)})")
                caso_info["estado"] = "FALLIDO"
                caso_info["timestamp_fin"] = datetime.now().isoformat()
                estado["resumen"]["fallidos"] += 1
                estado["resumen"]["en_proceso"] -= 1

            # Calcular metricas de resumen
            casos_completados = [c for c in estado["casos"] if c["estado"] == "COMPLETADO"]
            if casos_completados:
                scores = [c["score"] for c in casos_completados if c["score"] is not None]
                if scores:
                    estado["resumen"]["promedio_score"] = statistics.mean(scores)

                duraciones = [c["duracion_segundos"] for c in casos_completados if c["duracion_segundos"] is not None]
                if duraciones:
                    tiempo_promedio = statistics.mean(duraciones)
                    estado["resumen"]["tiempo_promedio_caso"] = tiempo_promedio
                    casos_restantes = estado["resumen"]["pendientes"]
                    estado["resumen"]["tiempo_estimado_restante"] = tiempo_promedio * casos_restantes

            estado["resumen"]["progreso_porcentaje"] = (estado["resumen"]["completados"] / estado["resumen"]["total"]) * 100

            # Guardar estado actualizado
            with open(estado_path, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)

        # Marcar workflow como completado
        estado["timestamp_fin"] = datetime.now().isoformat()
        with open(estado_path, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

        print()
        print("=" * 60)
        print(f"Workflow completado")
        print(f"Completados: {estado['resumen']['completados']}/{estado['resumen']['total']}")
        print(f"Fallidos: {estado['resumen']['fallidos']}")
        if estado['resumen']['promedio_score'] is not None:
            print(f"Score promedio: {estado['resumen']['promedio_score']:.1f}%")
        print("=" * 60)

        return True, "Workflow ejecutado exitosamente"

    except KeyboardInterrupt:
        print("\n\nWORKFLOW INTERRUMPIDO POR USUARIO")
        print(f"Progreso guardado en: {estado_path}")
        print(f"Para reanudar: python {__file__} --reanudar --lote-id {lote_id}")
        return True, "Workflow interrumpido (progreso guardado)"

    except Exception as e:
        return False, f"Error al ejecutar lote: {str(e)}"


# ===========================
# FUNCION 3: CONSOLIDAR REPORTES
# ===========================

def consolidar_reportes(lote_id: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Genera reporte consolidado de todos los casos completados.

    Args:
        lote_id: ID del lote

    Returns:
        Tupla (exito, mensaje, reporte_consolidado)
    """
    try:
        # Cargar estado
        estado_path = RESULTADOS_DIR / f"callery_workflow_{lote_id}.json"
        if not estado_path.exists():
            return False, f"Error: No se encontro el lote '{lote_id}'", None

        with open(estado_path, 'r', encoding='utf-8') as f:
            estado = json.load(f)

        # Filtrar casos completados
        casos_completados = [c for c in estado["casos"] if c["estado"] == "COMPLETADO"]

        if not casos_completados:
            return False, "Error: No hay casos completados para consolidar", None

        # Recolectar datos de reportes individuales
        scores = []
        errores_por_tipo = {}
        biomarcadores_faltantes = {}
        casos_problematicos = []

        for caso_info in casos_completados:
            reporte_path = Path(caso_info["reporte_path"])

            if not reporte_path.exists():
                continue

            with open(reporte_path, 'r', encoding='utf-8') as f:
                reporte = json.load(f)

            score = caso_info["score"]
            scores.append(score)

            # Casos problematicos
            if score < 90.0:
                casos_problematicos.append({
                    "numero": caso_info["numero"],
                    "score": score,
                    "errores": caso_info["errores_criticos"],
                    "warnings": caso_info["warnings"]
                })

            # Analizar errores
            validacion = reporte.get("validacion", {})
            for error in validacion.get("errores_criticos", []):
                tipo = error.get("tipo", "DESCONOCIDO")
                errores_por_tipo[tipo] = errores_por_tipo.get(tipo, 0) + 1

            # Biomarcadores faltantes
            for warning in validacion.get("advertencias", []):
                if "biomarcador" in warning.get("mensaje", "").lower():
                    # Intentar extraer nombre del biomarcador
                    mensaje = warning.get("mensaje", "")
                    if "'" in mensaje:
                        biomarcador = mensaje.split("'")[1]
                        if biomarcador not in biomarcadores_faltantes:
                            biomarcadores_faltantes[biomarcador] = {
                                "frecuencia": 0,
                                "casos": []
                            }
                        biomarcadores_faltantes[biomarcador]["frecuencia"] += 1
                        biomarcadores_faltantes[biomarcador]["casos"].append(caso_info["numero"])

        # Calcular estadisticas
        resumen_scores = {
            "promedio": statistics.mean(scores) if scores else 0.0,
            "mediana": statistics.median(scores) if scores else 0.0,
            "minimo": min(scores) if scores else 0.0,
            "maximo": max(scores) if scores else 0.0
        }

        # Generar recomendaciones
        recomendaciones = []

        # Recomendaciones por biomarcadores faltantes
        for bio, info in sorted(biomarcadores_faltantes.items(), key=lambda x: x[1]["frecuencia"], reverse=True):
            if info["frecuencia"] >= 2:
                recomendaciones.append(f"Revisar extractor de {bio} ({info['frecuencia']} casos afectados)")

        # Recomendaciones por casos criticos
        if len(casos_problematicos) > 0:
            recomendaciones.append(f"Validar {len(casos_problematicos)} casos criticos con IA")

        # Crear reporte consolidado
        consolidado = {
            "lote_id": lote_id,
            "timestamp": datetime.now().isoformat(),
            "casos_procesados": len(casos_completados),
            "resumen_scores": resumen_scores,
            "casos_problematicos": casos_problematicos,
            "biomarcadores_faltantes_comunes": [
                {"nombre": bio, "frecuencia": info["frecuencia"], "casos": info["casos"][:5]}  # Max 5 casos
                for bio, info in sorted(biomarcadores_faltantes.items(), key=lambda x: x[1]["frecuencia"], reverse=True)
            ],
            "errores_por_tipo": errores_por_tipo,
            "recomendaciones": recomendaciones,
            "version_herramienta": VERSION
        }

        # Guardar reporte consolidado
        consolidado_path = RESULTADOS_DIR / f"callery_consolidado_{lote_id}.json"
        with open(consolidado_path, 'w', encoding='utf-8') as f:
            json.dump(consolidado, f, indent=2, ensure_ascii=False)

        return True, consolidado_path, consolidado

    except Exception as e:
        return False, f"Error al consolidar reportes: {str(e)}", None


# ===========================
# FUNCION 4: REANUDAR LOTE
# ===========================

def reanudar_lote(lote_id: str) -> Tuple[bool, str]:
    """
    Reanuda un workflow interrumpido.

    Args:
        lote_id: ID del lote

    Returns:
        Tupla (exito, mensaje)
    """
    try:
        # Verificar que existe el lote
        estado_path = RESULTADOS_DIR / f"callery_workflow_{lote_id}.json"
        if not estado_path.exists():
            return False, f"Error: No se encontro el lote '{lote_id}'"

        with open(estado_path, 'r', encoding='utf-8') as f:
            estado = json.load(f)

        # Contar pendientes
        pendientes = sum(1 for c in estado["casos"] if c["estado"] == "PENDIENTE")

        if pendientes == 0:
            return False, "No hay casos pendientes para reanudar"

        # Registrar reanudacion
        estado["interrupciones"].append({
            "timestamp": datetime.now().isoformat(),
            "casos_pendientes": pendientes
        })

        with open(estado_path, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

        # Ejecutar lote en modo reanudar
        return ejecutar_lote(lote_id, modo_reanudar=True)

    except Exception as e:
        return False, f"Error al reanudar lote: {str(e)}"


# ===========================
# FUNCION 5: MOSTRAR ESTADO
# ===========================

def mostrar_estado(lote_id: str) -> Tuple[bool, str]:
    """
    Muestra estado actual del workflow.

    Args:
        lote_id: ID del lote

    Returns:
        Tupla (exito, mensaje)
    """
    try:
        # Cargar estado
        estado_path = RESULTADOS_DIR / f"callery_workflow_{lote_id}.json"
        if not estado_path.exists():
            return False, f"Error: No se encontro el lote '{lote_id}'"

        with open(estado_path, 'r', encoding='utf-8') as f:
            estado = json.load(f)

        resumen = estado["resumen"]

        print()
        print("=" * 60)
        print("ESTADO DEL WORKFLOW")
        print("=" * 60)
        print(f"Lote ID: {lote_id}")
        print(f"Descripcion: {estado['descripcion']}")
        print(f"Inicio: {estado['timestamp_inicio']}")
        if estado['timestamp_fin']:
            print(f"Fin: {estado['timestamp_fin']}")
        print()

        # Barra de progreso
        print("Progreso:", mostrar_barra_progreso(resumen["completados"], resumen["total"]))
        print()

        # Resumen
        print(f"Completados: {resumen['completados']} casos")
        print(f"Pendientes: {resumen['pendientes']} casos")
        print(f"Fallidos: {resumen['fallidos']} casos")

        if resumen["promedio_score"] is not None:
            print(f"\nScore promedio: {resumen['promedio_score']:.1f}%")

        if resumen["tiempo_estimado_restante"] is not None:
            print(f"Tiempo estimado restante: {formatear_duracion(resumen['tiempo_estimado_restante'])}")

        # Casos criticos
        if resumen["casos_criticos"]:
            print(f"\nCasos criticos (score < 90%): {len(resumen['casos_criticos'])}")
            for caso_num in resumen["casos_criticos"][:5]:  # Max 5
                caso_info = next(c for c in estado["casos"] if c["numero"] == caso_num)
                print(f"  - {caso_num}: {caso_info['score']:.1f}%")

        # Casos completados (ultimos 10)
        print("\nUltimos casos procesados:")
        casos_completados = [c for c in estado["casos"] if c["estado"] == "COMPLETADO"]
        for caso_info in casos_completados[-10:]:
            emoji = "OK" if caso_info["score"] >= 90.0 else "ADVERTENCIA"
            print(f"  {emoji} {caso_info['numero']} -> {caso_info['score']:.1f}%")

        print("=" * 60)

        return True, "Estado mostrado exitosamente"

    except Exception as e:
        return False, f"Error al mostrar estado: {str(e)}"


# ===========================
# V2.0: ACTUALIZACION AUDITORIA_REALIZADA.MD
# ===========================

def actualizar_auditoria_realizada(caso: str, score: float, estado_final: str, observaciones: str = "") -> Tuple[bool, str]:
    """
    Actualiza auditoria_realizada.md despues de auditar un caso.

    V2.0 FUNCIONALIDAD NUEVA - FASE 1

    Args:
        caso: Numero de caso (ej: IHQ250013)
        score: Score de validacion (0-100)
        estado_final: Estado final (OK, WARNING, ERROR)
        observaciones: Observaciones adicionales (opcional)

    Returns:
        Tupla (exito, mensaje)
    """
    try:
        if not AUDITORIA_REALIZADA_PATH.exists():
            return False, f"Error: No se encontro {AUDITORIA_REALIZADA_PATH}"

        # Leer archivo actual
        with open(AUDITORIA_REALIZADA_PATH, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Extraer numero del caso (ej: IHQ250013 -> 13)
        numero_caso = int(caso.replace("IHQ", "").replace("250", ""))
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        # Construir observacion automatica
        if not observaciones:
            if score == 100.0:
                observaciones = f"Score: {score:.1f}%"
            elif score >= 90.0:
                observaciones = f"Score: {score:.1f}%"
            elif score >= 80.0:
                observaciones = f"Score: {score:.1f}% - Correcciones aplicadas"
            else:
                observaciones = f"Score: {score:.1f}% - Requiere revision"

        # 1. Actualizar contador de casos auditados en resumen general
        import re

        # Buscar linea de resumen general
        patron_resumen = r'\|\s*✅\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|'
        match_resumen = re.search(patron_resumen, contenido)

        if match_resumen:
            casos_procesados = int(match_resumen.group(1))
            casos_auditados = int(match_resumen.group(2))
            casos_pendientes = int(match_resumen.group(3))

            # Incrementar auditados, decrementar pendientes
            nuevos_auditados = casos_auditados + 1
            nuevos_pendientes = max(0, casos_pendientes - 1)

            nueva_linea_resumen = f"| ✅ | {casos_procesados} | {nuevos_auditados} | {nuevos_pendientes} |"
            contenido = re.sub(patron_resumen, lambda m: nueva_linea_resumen, contenido, count=1)

        # 2. Actualizar contador de casos auditados en seccion del archivo
        # Buscar patron "### ✅ Casos Auditados (X/50)"
        patron_contador = r'###\s*✅\s*Casos Auditados\s*\((\d+)/50\)'
        match_contador = re.search(patron_contador, contenido)

        if match_contador:
            contador_actual = int(match_contador.group(1))
            nuevo_contador = contador_actual + 1
            contenido = re.sub(patron_contador, f'### ✅ Casos Auditados ({nuevo_contador}/50)', contenido, count=1)

        # 3. Actualizar contador de pendientes
        patron_pendientes = r'###\s*⏳\s*Pendientes de Auditoría\s*\((\d+)/50\)'
        match_pendientes = re.search(patron_pendientes, contenido)

        if match_pendientes:
            pendientes_actual = int(match_pendientes.group(1))
            nuevos_pendientes_seccion = max(0, pendientes_actual - 1)
            contenido = re.sub(patron_pendientes, f'### ⏳ Pendientes de Auditoría ({nuevos_pendientes_seccion}/50)', contenido, count=1)

        # 4. Agregar caso a tabla de auditados
        # Buscar la ultima linea de la tabla de auditados
        patron_tabla_auditados = r'(\|\s*\d+\s*\|\s*IHQ\d+\s*\|\s*✅\s*Auditado\s*\|[^\n]+\n)'
        matches_tabla = list(re.finditer(patron_tabla_auditados, contenido))

        if matches_tabla:
            ultima_linea = matches_tabla[-1]
            # Extraer numero de la ultima linea
            ultimo_numero_match = re.search(r'\|\s*(\d+)\s*\|', ultima_linea.group(0))
            if ultimo_numero_match:
                ultimo_numero = int(ultimo_numero_match.group(1))
                nuevo_numero = ultimo_numero + 1

                # Construir nueva linea
                nueva_linea = f"| {nuevo_numero} | {caso} | ✅ Auditado | {fecha_actual} | {observaciones} |\n"

                # Insertar despues de la ultima linea de la tabla
                pos_insercion = ultima_linea.end()
                contenido = contenido[:pos_insercion] + nueva_linea + contenido[pos_insercion:]

        # 5. Remover caso de tabla de pendientes (si existe)
        # Buscar patron "| XX | IHQXXXXXX | ⏳ Pendiente |"
        patron_caso_pendiente = rf'\|\s*\d+\s*\|\s*{caso}\s*\|\s*⏳\s*Pendiente\s*\|\n'
        contenido = re.sub(patron_caso_pendiente, '', contenido)

        # 6. Actualizar seccion "Completado" en proximos pasos
        patron_completado = r'(✅ Auditoría de casos 001-\d+)'
        if re.search(patron_completado, contenido):
            contenido = re.sub(patron_completado, f'✅ Auditoría de casos 001-{numero_caso:03d}', contenido)

        # 7. Actualizar contador en "En Progreso"
        patron_en_progreso = r'(⏳ Completar auditoría de casos \d+-050 del primer archivo \()(\d+)( casos pendientes\))'
        match_en_progreso = re.search(patron_en_progreso, contenido)
        if match_en_progreso:
            pendientes_prog = int(match_en_progreso.group(2))
            nuevos_pend = max(0, pendientes_prog - 1)
            contenido = re.sub(patron_en_progreso, rf'\g<1>{nuevos_pend}\g<3>', contenido)

        # Guardar archivo actualizado
        with open(AUDITORIA_REALIZADA_PATH, 'w', encoding='utf-8') as f:
            f.write(contenido)

        return True, f"Auditoria_realizada.md actualizado: {caso} agregado"

    except Exception as e:
        return False, f"Error al actualizar auditoria_realizada.md: {str(e)}"


# ===========================
# V2.0: DETECCION INTELIGENTE DE ERRORES
# ===========================

def analizar_errores_caso(reporte_auditoria: Dict) -> List[Dict]:
    """
    Analiza reporte de auditoria y detecta patrones de errores comunes.

    V2.0 FUNCIONALIDAD NUEVA - FASE 1

    Args:
        reporte_auditoria: Diccionario con reporte de auditoria (FUNC-01)

    Returns:
        Lista de errores detectados con sugerencias
    """
    errores_detectados = []

    try:
        auditoria_bd = reporte_auditoria.get("auditoria_bd", {})

        # 1. Detectar DIAGNOSTICO_COLORACION faltante
        diag_coloracion = auditoria_bd.get("diagnostico_coloracion", {})
        if diag_coloracion.get("estado") == "ERROR":
            errores_detectados.append({
                "tipo": "DIAGNOSTICO_COLORACION",
                "severidad": "CRITICO",
                "campo": "Diagnostico Coloracion",
                "problema": "Campo NO APLICA pero existe diagnostico en OCR",
                "sugerencia": "Verificar patron de extraccion en medical_extractor.py (linea ~665)",
                "archivos_afectados": ["core/extractors/medical_extractor.py"],
                "funcion": "extract_diagnostico_coloracion()"
            })

        # 2. Detectar biomarcadores NO MAPEADOS
        biomarcadores = auditoria_bd.get("biomarcadores", {})
        no_mapeados = biomarcadores.get("no_mapeados", [])

        if no_mapeados:
            for bio in no_mapeados:
                errores_detectados.append({
                    "tipo": "BIOMARCADOR_NO_MAPEADO",
                    "severidad": "WARNING",
                    "campo": f"Biomarcador {bio}",
                    "problema": f"Biomarcador '{bio}' no esta en el sistema",
                    "sugerencia": f"Ejecutar FUNC-03: auditor.agregar_biomarcador('{bio}')",
                    "archivos_afectados": ["core/validation_checker.py"],
                    "funcion": "FUNC-03"
                })

        # 3. Detectar valores incorrectos en biomarcadores
        valores_incorrectos = biomarcadores.get("valores_incorrectos", [])

        if valores_incorrectos:
            for bio_info in valores_incorrectos:
                bio_nombre = bio_info.get("biomarcador", "DESCONOCIDO")
                errores_detectados.append({
                    "tipo": "VALOR_BIOMARCADOR_INCORRECTO",
                    "severidad": "CRITICO",
                    "campo": f"Biomarcador {bio_nombre}",
                    "problema": f"Valor en BD no coincide con OCR",
                    "sugerencia": f"Verificar extractor de {bio_nombre} o ejecutar FUNC-06",
                    "archivos_afectados": ["core/extractors/biomarker_extractor.py"],
                    "funcion": "extract_biomarkers()"
                })

        # 4. Detectar malignidad con WARNING
        malignidad = auditoria_bd.get("malignidad", {})
        if malignidad.get("estado") == "WARNING":
            errores_detectados.append({
                "tipo": "MALIGNIDAD_WARNING",
                "severidad": "WARNING",
                "campo": "Malignidad",
                "problema": malignidad.get("mensaje", "Clasificacion requiere revision"),
                "sugerencia": "Revisar clasificacion manualmente o ajustar keywords en medical_extractor.py",
                "archivos_afectados": ["core/extractors/medical_extractor.py"],
                "funcion": "determine_malignancy()"
            })

        # 5. Detectar campos criticos vacios
        campos_obligatorios = auditoria_bd.get("campos_obligatorios", {})
        errores_campos = campos_obligatorios.get("errores", [])

        if errores_campos:
            for error_campo in errores_campos:
                errores_detectados.append({
                    "tipo": "CAMPO_CRITICO_VACIO",
                    "severidad": "CRITICO",
                    "campo": error_campo.get("campo", "DESCONOCIDO"),
                    "problema": "Campo critico vacio o NULL",
                    "sugerencia": "Verificar extractor correspondiente y ejecutar FUNC-06",
                    "archivos_afectados": ["core/extractors/"],
                    "funcion": "Verificar extractor especifico"
                })

        # 6. Detectar warnings generales
        warnings = auditoria_bd.get("warnings", [])
        if warnings and len(warnings) > 0:
            for warning in warnings:
                if isinstance(warning, str):
                    errores_detectados.append({
                        "tipo": "WARNING_GENERAL",
                        "severidad": "INFO",
                        "campo": "General",
                        "problema": warning,
                        "sugerencia": "Revisar caso manualmente",
                        "archivos_afectados": [],
                        "funcion": ""
                    })

    except Exception as e:
        errores_detectados.append({
            "tipo": "ERROR_ANALISIS",
            "severidad": "ERROR",
            "campo": "Sistema",
            "problema": f"Error al analizar reporte: {str(e)}",
            "sugerencia": "Verificar estructura del reporte JSON",
            "archivos_afectados": [],
            "funcion": ""
        })

    return errores_detectados


# ===========================
# CLI PRINCIPAL
# ===========================

def main():
    parser = argparse.ArgumentParser(
        description="Callery Workflow - Gestion de auditorias por lote",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS:

1. Iniciar nuevo lote:
   python callery_workflow.py --iniciar --casos "IHQ251014,IHQ251015,IHQ251016"

2. Ejecutar lote:
   python callery_workflow.py --ejecutar --lote-id lote_3_casos_20251118_100000

3. Consolidar reportes:
   python callery_workflow.py --consolidar --lote-id lote_3_casos_20251118_100000

4. Reanudar lote interrumpido:
   python callery_workflow.py --reanudar --lote-id lote_3_casos_20251118_100000

5. Ver estado:
   python callery_workflow.py --estado --lote-id lote_3_casos_20251118_100000
        """
    )

    parser.add_argument("--iniciar", action="store_true",
                        help="Iniciar nuevo lote de auditorias")
    parser.add_argument("--ejecutar", action="store_true",
                        help="Ejecutar auditorias del lote")
    parser.add_argument("--consolidar", action="store_true",
                        help="Consolidar reportes del lote")
    parser.add_argument("--reanudar", action="store_true",
                        help="Reanudar lote interrumpido")
    parser.add_argument("--estado", action="store_true",
                        help="Mostrar estado del lote")

    parser.add_argument("--casos", type=str,
                        help="Lista de casos separados por coma (ej: IHQ251014,IHQ251015)")
    parser.add_argument("--lote-id", type=str,
                        help="ID del lote existente")

    parser.add_argument("--version", action="version",
                        version=f"Callery Workflow v{VERSION}")

    args = parser.parse_args()

    # Validar argumentos
    if args.iniciar:
        if not args.casos:
            print("ERROR: --iniciar requiere --casos")
            sys.exit(1)

        exito, resultado, estado = iniciar_lote(args.casos)
        if exito:
            print()
            print("=" * 60)
            print("LOTE CREADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Lote ID: {estado['lote_id']}")
            print(f"Total casos: {estado['resumen']['total']}")
            print(f"Estado guardado en: {resultado}")
            print()
            print("SIGUIENTE PASO:")
            print(f"  python {__file__} --ejecutar --lote-id {estado['lote_id']}")
            print("=" * 60)
        else:
            print(f"ERROR: {resultado}")
            sys.exit(1)

    elif args.ejecutar:
        if not args.lote_id:
            print("ERROR: --ejecutar requiere --lote-id")
            sys.exit(1)

        exito, mensaje = ejecutar_lote(args.lote_id)
        if not exito:
            print(f"ERROR: {mensaje}")
            sys.exit(1)

    elif args.consolidar:
        if not args.lote_id:
            print("ERROR: --consolidar requiere --lote-id")
            sys.exit(1)

        exito, resultado, consolidado = consolidar_reportes(args.lote_id)
        if exito:
            print()
            print("=" * 60)
            print("REPORTE CONSOLIDADO")
            print("=" * 60)
            print(f"Casos procesados: {consolidado['casos_procesados']}")
            print(f"Score promedio: {consolidado['resumen_scores']['promedio']:.1f}%")
            print(f"Score minimo: {consolidado['resumen_scores']['minimo']:.1f}%")
            print(f"Score maximo: {consolidado['resumen_scores']['maximo']:.1f}%")
            print()

            if consolidado['casos_problematicos']:
                print(f"CASOS PROBLEMATICOS ({len(consolidado['casos_problematicos'])}):")
                for caso in consolidado['casos_problematicos']:
                    print(f"  - {caso['numero']}: {caso['score']:.1f}% ({caso['errores']} errores, {caso['warnings']} warnings)")
                print()

            if consolidado['recomendaciones']:
                print("RECOMENDACIONES:")
                for i, rec in enumerate(consolidado['recomendaciones'], 1):
                    print(f"  {i}. {rec}")
                print()

            print(f"Reporte guardado en: {resultado}")
            print("=" * 60)
        else:
            print(f"ERROR: {resultado}")
            sys.exit(1)

    elif args.reanudar:
        if not args.lote_id:
            print("ERROR: --reanudar requiere --lote-id")
            sys.exit(1)

        exito, mensaje = reanudar_lote(args.lote_id)
        if not exito:
            print(f"ERROR: {mensaje}")
            sys.exit(1)

    elif args.estado:
        if not args.lote_id:
            print("ERROR: --estado requiere --lote-id")
            sys.exit(1)

        exito, mensaje = mostrar_estado(args.lote_id)
        if not exito:
            print(f"ERROR: {mensaje}")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
