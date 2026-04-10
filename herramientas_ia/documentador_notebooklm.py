#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERRAMIENTA: DOCUMENTADOR NOTEBOOKLM
======================================

Genera la estructura de carpetas y los archivos base (fuentes y prompts)
para una campaña de contenido en NotebookLM.

Uso:
  python herramientas_ia/documentador_notebooklm.py --proyecto "ruta/al/proyecto" --audiencia "gerente" --objetivo "impacto_economico"
"""

import argparse
import os
import sys
from pathlib import Path

# Forzar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Constantes de formatos de NotebookLM
FORMATOS_NOTEBOOKLM = {
    "video": "Video Overview (Diapositivas Narradas)",
    "audio": {
        "informacion_detallada": "Audio - Información Detallada (Conversación animada)",
        "breve": "Audio - Breve (Resumen breve y rápido)",
        "critica": "Audio - Crítica (Revisión experta con comentarios)",
        "debate": "Audio - Debate (Debate reflexivo entre presentadores)"
    },
    "cuestionario": "FAQ y Cuestionarios",
    "reporte": "Reporte Ejecutivo"
}

def analizar_proyecto(ruta_proyecto: Path) -> str:
    """
    Simula un análisis del proyecto para extraer puntos clave.
    En una versión real, esto usaría 'tree', 'cloc', o leería READMEs.
    Para esta simulación, reacciona al ejemplo del proyecto de oncología.
    """
    print(f"[INFO] Analizando estructura de: {ruta_proyecto}")
    # Simulación de análisis basada en el ejemplo del usuario
    if "oncologia" in str(ruta_proyecto).lower():
        print("[INFO] Proyecto de Oncología detectado.")
        return (
            "El proyecto es un sistema de registro de cáncer para el HUV (EVARISIS). "
            "Incluye un dashboard, múltiples agentes IA, y un sistema de extractores de datos (auditor_sistema.py) "
            "de PDFs de patología (IHQ). Un módulo clave analiza tendencias de biomarcadores "
            "para predecir la demanda futura de medicamentos de alto costo."
        )
    return "Análisis genérico del proyecto: El sistema automatiza procesos clave y utiliza una arquitectura de agentes."

def generar_archivos_fuente(ruta_archivo: Path, contexto_proyecto: str, audiencia: str, objetivo: str, formato: str):
    """
    Genera el archivo .md de conocimiento fuente, adaptado al formato.
    """
    titulo = f"Informe del Proyecto (Foco: {audiencia.capitalize()})"

    # --- Lógica de adaptación de contenido ---
    contenido_base = f"""
# {titulo}

## Contexto del Proyecto
{contexto_proyecto}

## Enfoque Principal: {objetivo.replace('_', ' ').capitalize()}
"""

    if objetivo == "impacto_economico_farmaceuticas":
        contenido_base += (
            "\nEl módulo de IA predictiva es la joya de la corona para la gestión. Al analizar tendencias de "
            "diagnósticos IHQ (ej. HER2+, Ki-67), podemos prever la demanda de medicamentos de alto costo "
            "con 3 a 6 meses de antelación. \n\n"
            "Esto transforma a la institución de ser reactiva a ser proactiva, dándonos un poder de negociación "
            "sin precedentes con farmacéuticas. Podemos negociar compras al por mayor de medicamentos "
            "como Trastuzumab o Pembrolizumab, generando ahorros estimados de 20-30% en el presupuesto de alto costo."
        )
    else:
        contenido_base += "\nEl proyecto ofrece beneficios significativos alineados con los objetivos de la organización."

    # Adaptación específica al formato
    if formato == "video":
        # Para video, agregar más bullets e ideas visuales
        contenido_base += """

## Puntos Clave para Presentación Visual
- **Gráfico 1:** Demanda Actual (Reactiva, picos y valles) vs. Demanda Predictiva (Proactiva, curva suavizada).
- **Diagrama:** Flujo: PDF de Patología -> Agente Extractor IA -> Base de Datos Estructurada -> Modelo Predictivo -> Reporte de Demanda.
- **Cita Clave (para Gerencia):** "Anticipar la necesidad de 100 dosis de Trastuzumab nos permite negociar un 30% por debajo del precio de mercado spot."
- **Visual:** Un 'antes' (un médico buscando un PDF) y un 'después' (un dashboard con un gráfico de predicción).
"""
    elif "audio" in formato:
        # Para audio, adaptar contenido según el tipo
        if "informacion_detallada" in formato:
            contenido_base += """

## Puntos Clave para Conversación Animada (Información Detallada)
- **Tema 1:** Evolución del proyecto desde su versión inicial hasta la actual
- **Tema 2:** Arquitectura técnica y decisiones de diseño
- **Tema 3:** Casos de éxito y métricas de impacto
- **Tema 4:** Beneficios tangibles y ROI
- **Tema 5:** Roadmap futuro y próximos pasos

**Estilo:** Conversación entre dos presentadores entusiastas que analizan y conectan conceptos.
**Duración:** 15-20 minutos aproximadamente.
"""
        elif "breve" in formato:
            contenido_base += """

## Puntos Esenciales para Resumen Breve
- **Mensaje 1:** ¿Qué es el proyecto? (30 segundos)
- **Mensaje 2:** ¿Cuál es el beneficio principal? (30 segundos)
- **Mensaje 3:** ¿Qué lo hace único? (30 segundos)
- **Mensaje 4:** ¿Cuál es el próximo paso? (30 segundos)

**Estilo:** Conciso, directo, enfocado en ideas principales.
**Duración:** 2-3 minutos máximo.
"""
        elif "critica" in formato:
            contenido_base += """

## Aspectos para Revisión Crítica Experta
- **Fortalezas:** Qué está bien implementado y por qué
- **Áreas de mejora:** Qué podría optimizarse o extenderse
- **Comparación:** Cómo se compara con alternativas o estándares de la industria
- **Recomendaciones:** Sugerencias constructivas para el siguiente nivel
- **Conclusión balanceada:** Evaluación general justa

**Estilo:** Análisis profesional, constructivo pero honesto, con comentarios expertos.
**Duración:** 10-15 minutos aproximadamente.
"""
        elif "debate" in formato:
            contenido_base += """

## Puntos de Debate (para formato Debate)
- **Pregunta 1:** ¿Cómo se diferencia esto de un simple 'conteo' de inventario? (Respuesta: Es predicción de demanda futura, no conteo de stock actual).
- **Pregunta 2:** ¿Qué tan confiable es la predicción de la IA? (Respuesta: El modelo se re-entrena semanalmente con los nuevos casos de IHQ, aumentando su precisión. Es más preciso que la estimación humana actual).
- **Pregunta 3 (Clave):** ¿Cuál es el beneficio tangible para el Gerente? (Respuesta: Poder de negociación. Comprar por volumen reduce costos y garantiza suministro, evitando escasez).

**Estilo:** Debate reflexivo entre dos presentadores con perspectivas diferentes pero complementarias.
**Duración:** 12-18 minutos aproximadamente.
"""

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido_base)
    print(f"   [OK] Creado archivo fuente: {ruta_archivo.name}")

def generar_archivos_prompt(ruta_archivo: Path, audiencia: str, objetivo: str, formato: str):
    """
    Genera el archivo .txt de prompts, adaptado al formato.
    """
    prompts = f"### Prompts para formato: {formato} (Audiencia: {audiencia.capitalize()})\n\n"

    # --- Lógica de adaptación de prompts ---
    prompt_enfoque_base = (
        f"Enfócate exclusivamente en el **impacto económico y estratégico** del proyecto. "
        f"Dirígete a un **Gerente** que valora el ROI, la eficiencia financiera y la ventaja competitiva. "
        f"Usa los datos sobre la predicción de tendencias para justificar la **negociación estratégica con farmacéuticas**. "
        f"Sé directo, profesional y basado en datos. Omite detalles técnicos de bajo nivel (código, librerías)."
    )

    if formato == "video":
        prompts += f"--- PROMPT DE ENFOQUE (Steering Prompt para Video Overview) ---\n"
        prompts += f"{prompt_enfoque_base}\n\n"
        prompts += f"--- PROMPT DE ESTILO VISUAL (Visual Style para Video Overview) ---\n"
        prompts += "Custom: Un estilo 'Whiteboard' profesional, corporativo y limpio. Similar a una presentación de consultoría de alto nivel (tipo McKinsey o BCG). Usar gráficos de barras y diagramas de flujo claros. Tono de narración firme y confiado."

    elif "audio" in formato:
        # Determinar el tipo de audio
        if "informacion_detallada" in formato:
            prompts += f"--- FORMATO DE AUDIO (Format para Audio Overview) ---\n"
            prompts += "Información detallada\n\n"
            prompts += f"--- CONFIGURACIÓN ---\n"
            prompts += "Idioma: español\n"
            prompts += "Duración: Predeterminada (15-20 minutos)\n\n"
            prompts += f"--- PROMPT DE ENFOQUE (Steering Prompt) ---\n"
            prompts += (
                f"Crea una conversación animada entre dos presentadores entusiastas que analizan y conectan los conceptos del proyecto. "
                f"Deben explorar la evolución del sistema, arquitectura técnica, casos de éxito, beneficios tangibles y roadmap futuro. "
                f"{prompt_enfoque_base}"
            )

        elif "breve" in formato:
            prompts += f"--- FORMATO DE AUDIO (Format para Audio Overview) ---\n"
            prompts += "Breve\n\n"
            prompts += f"--- CONFIGURACIÓN ---\n"
            prompts += "Idioma: español\n"
            prompts += "Duración: Corto (2-3 minutos)\n\n"
            prompts += f"--- PROMPT DE ENFOQUE (Steering Prompt) ---\n"
            prompts += (
                f"Genera un resumen ejecutivo breve y directo. En 2-3 minutos debe explicar: qué es el proyecto, "
                f"cuál es su beneficio principal, qué lo hace único y cuál es el próximo paso recomendado. "
                f"Debe ser conciso, claro y enfocado en las ideas principales. {prompt_enfoque_base}"
            )

        elif "critica" in formato:
            prompts += f"--- FORMATO DE AUDIO (Format para Audio Overview) ---\n"
            prompts += "Crítica\n\n"
            prompts += f"--- CONFIGURACIÓN ---\n"
            prompts += "Idioma: español\n"
            prompts += "Duración: Predeterminada (10-15 minutos)\n\n"
            prompts += f"--- PROMPT DE ENFOQUE (Steering Prompt) ---\n"
            prompts += (
                f"Genera una revisión experta del proyecto con comentarios constructivos. "
                f"Analiza fortalezas, áreas de mejora, comparación con alternativas, y recomendaciones específicas. "
                f"El tono debe ser profesional, balanceado, constructivo pero honesto. {prompt_enfoque_base}"
            )

        elif "debate" in formato:
            prompts += f"--- FORMATO DE AUDIO (Format para Audio Overview) ---\n"
            prompts += "Debate\n\n"
            prompts += f"--- CONFIGURACIÓN ---\n"
            prompts += "Idioma: español\n"
            prompts += "Duración: Predeterminada (12-18 minutos)\n\n"
            prompts += f"--- PROMPT DE ENFOQUE (Steering Prompt) ---\n"
            prompts += (
                f"Crear un debate reflexivo entre un presentador IA 'Optimista' (enfocado en la oportunidad económica de negociar con farmacéuticas) "
                f"y un presentador IA 'Pragmático' (enfocado en los riesgos y la precisión del modelo). "
                f"Ambos deben concluir que el beneficio económico supera con creces el riesgo. {prompt_enfoque_base}"
            )

    elif formato == "cuestionario":
        prompts += f"--- PROMPT DE CHAT (Chat Prompt para FAQs) ---\n"
        prompts += (
            "Basado en las fuentes, genera 10 preguntas y respuestas clave que un Gerente "
            f"haría sobre el {objetivo.replace('_', ' ')}. Enfócate en el ROI, "
            "el tiempo de implementación y los riesgos financieros."
        )

    else: # Reporte
        prompts += f"--- PROMPT DE REPORTE (Chat Prompt para Reporte Ejecutivo) ---\n"
        prompts += (
            f"Genera un reporte ejecutivo de una página (formato 'Briefing Doc') "
            f"enfocado en el {objetivo} para la {audiencia}. Incluye 3 puntos clave, "
            "un análisis de riesgo/beneficio y una recomendación de 'Siguiente Paso' accionable."
        )

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(prompts)
    print(f"   [OK] Creado archivo de prompts: {ruta_archivo.name}")

def main():
    parser = argparse.ArgumentParser(description="Generador de Insumos para NotebookLM")
    parser.add_argument("-p", "--proyecto", type=str, required=True, help="Ruta a la carpeta del proyecto a analizar.")
    parser.add_argument("-a", "--audiencia", type=str, required=True, help="Audiencia objetivo (ej: gerente, tecnico, inversor).")
    parser.add_argument("-o", "--objetivo", type=str, required=True, help="Objetivo/Mensaje clave (ej: impacto_economico_farmaceuticas).")

    args = parser.parse_args()

    print(f"Iniciando Documentador NotebookLM...")
    print(f"  Proyecto: {args.proyecto}")
    print(f"  Audiencia: {args.audiencia}")
    print(f"  Objetivo: {args.objetivo}")

    try:
        ruta_proyecto = Path(args.proyecto)
        # Verificación simple de que la ruta existe
        if not ruta_proyecto.exists():
            print(f"[ADVERTENCIA] La ruta del proyecto '{args.proyecto}' no existe. Se continuará con el análisis genérico.")
            contexto_proyecto = analizar_proyecto(Path(".")) # Simulación genérica
        else:
             contexto_proyecto = analizar_proyecto(ruta_proyecto)

        # Crear estructura de carpetas
        base_output_dir = Path("informes_notebookLM") / args.audiencia.lower().replace(" ", "_")

        for formato_key, formato_desc in FORMATOS_NOTEBOOKLM.items():
            # Caso especial para audio (tiene subtipos)
            if formato_key == "audio" and isinstance(formato_desc, dict):
                formato_dir = base_output_dir / formato_key
                os.makedirs(formato_dir, exist_ok=True)
                print(f"\n[INFO] Preparando formato: Audio (4 tipos)")

                # Generar cada tipo de audio
                for subtipo_key, subtipo_desc in formato_desc.items():
                    subtipo_dir = formato_dir / subtipo_key
                    os.makedirs(subtipo_dir, exist_ok=True)
                    print(f"   [SUBTIPO] {subtipo_desc}")

                    # 1. Generar archivo fuente
                    ruta_fuente = subtipo_dir / f"fuente_audio_{subtipo_key}.md"
                    generar_archivos_fuente(ruta_fuente, contexto_proyecto, args.audiencia, args.objetivo, f"audio_{subtipo_key}")

                    # 2. Generar archivo de prompts
                    ruta_prompts = subtipo_dir / f"prompts_audio_{subtipo_key}.txt"
                    generar_archivos_prompt(ruta_prompts, args.audiencia, args.objetivo, f"audio_{subtipo_key}")
            else:
                # Formatos normales (video, cuestionario, reporte)
                formato_dir = base_output_dir / formato_key
                os.makedirs(formato_dir, exist_ok=True)
                print(f"\n[INFO] Preparando formato: {formato_desc}")

                # 1. Generar archivo fuente
                ruta_fuente = formato_dir / f"fuente_{formato_key}.md"
                generar_archivos_fuente(ruta_fuente, contexto_proyecto, args.audiencia, args.objetivo, formato_key)

                # 2. Generar archivo de prompts
                ruta_prompts = formato_dir / f"prompts_{formato_key}.txt"
                generar_archivos_prompt(ruta_prompts, args.audiencia, args.objetivo, formato_key)

        print("\n" + "="*50)
        print("[COMPLETADO] Proceso exitoso")
        print(f"Estructura de carpetas creada en: {base_output_dir.resolve()}")
        print("="*50)

    except Exception as e:
        print(f"\n[ERROR] ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
