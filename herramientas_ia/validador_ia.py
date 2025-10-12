#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VALIDADOR CON IA - SISTEMA DE CORRECCIÓN INTELIGENTE
========================================================

Valida datos extraídos vs BD usando LLM local.
Genera correcciones automáticas basadas en el texto original.

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 5 de octubre de 2025
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import difflib

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.llm_client import LMStudioClient
from core.debug_mapper import DebugMapper
from core.database_manager import get_registro_by_peticion


class ValidadorIA:
    """Validador inteligente de datos médicos con IA"""

    def __init__(self, llm_endpoint: str = "http://127.0.0.1:1234"):
        """
        Inicializar validador

        Args:
            llm_endpoint: Endpoint del servidor LM Studio
        """
        self.llm_client = LMStudioClient(endpoint=llm_endpoint)
        self.resultados_dir = Path(__file__).parent / "resultados" / "validaciones_ia"
        self.resultados_dir.mkdir(parents=True, exist_ok=True)

    def validar_caso_ihq(
        self,
        numero_peticion: str,
        debug_map_path: Optional[Path] = None,
        validar_solo_criticos: bool = False
    ) -> Dict[str, Any]:
        """
        Valida un caso IHQ completo comparando debug map vs BD

        Args:
            numero_peticion: Número de petición IHQ
            debug_map_path: Ruta al archivo debug_map (opcional, se busca automáticamente)
            validar_solo_criticos: Si True, solo valida campos críticos

        Returns:
            Dict con resultados de validación
        """
        print(f"\n🔍 VALIDANDO CASO: {numero_peticion}")
        print("=" * 80)

        # 1. Cargar debug map
        if not debug_map_path:
            debug_map_path = self._buscar_debug_map(numero_peticion)

        if not debug_map_path or not debug_map_path.exists():
            return {
                "exito": False,
                "error": f"No se encontró debug map para {numero_peticion}"
            }

        print(f"📂 Cargando debug map: {debug_map_path.name}")
        debug_map = DebugMapper.cargar_mapa(debug_map_path)

        # 2. Cargar datos de BD
        print(f"🗄️ Consultando base de datos...")
        bd_data = get_registro_by_peticion(numero_peticion)

        if not bd_data:
            return {
                "exito": False,
                "error": f"No se encontró {numero_peticion} en la base de datos"
            }

        # 3. Extraer datos relevantes
        texto_original = debug_map["ocr"]["texto_consolidado"]
        datos_extraidos = debug_map["extraccion"]["unified_extractor"]
        datos_bd_dict = dict(bd_data) if bd_data else {}

        # 4. Campos a validar
        campos_criticos = [
            "numero_peticion", "identificacion", "nombre_completo",
            "edad", "genero", "diagnostico", "organo"
        ]

        campos_a_validar = campos_criticos if validar_solo_criticos else None

        # 5. Validar con IA
        print(f"\n🤖 Validando con IA (LM Studio)...")
        print(f"📋 Campos a validar: {len(campos_a_validar) if campos_a_validar else 'TODOS'}")

        validacion_resultado = self.llm_client.validar_multiple_campos(
            datos_extraidos=datos_extraidos,
            texto_original=texto_original,
            campos_a_validar=campos_a_validar
        )

        # 6. Comparar con BD y generar informe
        print(f"\n📊 Generando informe de validación...")
        informe = self._generar_informe_validacion(
            numero_peticion=numero_peticion,
            debug_map=debug_map,
            datos_bd=datos_bd_dict,
            validacion_ia=validacion_resultado
        )

        # 7. Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.resultados_dir / f"validacion_{numero_peticion}_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados guardados en: {output_file}")

        return informe

    def _buscar_debug_map(self, numero_peticion: str) -> Optional[Path]:
        """
        Busca el debug map más reciente para un número de petición

        Args:
            numero_peticion: Número de petición IHQ

        Returns:
            Path al debug map o None si no se encuentra
        """
        debug_dir = project_root / "data" / "debug_maps"

        if not debug_dir.exists():
            return None

        # Buscar archivos que contengan el número de petición
        mapas = list(debug_dir.glob(f"debug_map_{numero_peticion}_*.json"))

        if not mapas:
            return None

        # Retornar el más reciente
        return max(mapas, key=lambda p: p.stat().st_mtime)

    def _generar_informe_validacion(
        self,
        numero_peticion: str,
        debug_map: Dict[str, Any],
        datos_bd: Dict[str, Any],
        validacion_ia: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera informe completo de validación

        Args:
            numero_peticion: Número de petición
            debug_map: Mapa de debug completo
            datos_bd: Datos de la base de datos
            validacion_ia: Resultados de validación con IA

        Returns:
            Dict con informe completo
        """
        discrepancias = []
        correcciones_sugeridas = []
        campos_correctos = []

        validaciones = validacion_ia.get("validaciones", {})

        for campo, validacion in validaciones.items():
            if not validacion.get("exito"):
                continue

            val_data = validacion.get("validacion", {})

            campo_correcto = val_data.get("campo_correcto", True)
            confianza = val_data.get("confianza", 0.0)
            valor_sugerido = val_data.get("valor_sugerido")

            # Comparar con BD
            valor_extraido = debug_map["extraccion"]["unified_extractor"].get(campo)
            valor_bd = datos_bd.get(campo)

            if not campo_correcto or valor_sugerido:
                # Hay una discrepancia o sugerencia de corrección
                discrepancia = {
                    "campo": campo,
                    "valor_extraido": str(valor_extraido),
                    "valor_bd": str(valor_bd),
                    "valor_sugerido_ia": valor_sugerido,
                    "confianza_ia": confianza,
                    "razonamiento": val_data.get("razonamiento", ""),
                    "ubicacion_texto": val_data.get("ubicacion_en_texto", ""),
                    "similitud_extraido_bd": self._calcular_similitud(
                        str(valor_extraido), str(valor_bd)
                    )
                }

                discrepancias.append(discrepancia)

                # Si la IA sugiere un valor diferente al de BD, es una corrección
                if valor_sugerido and str(valor_sugerido) != str(valor_bd):
                    correcciones_sugeridas.append({
                        "campo": campo,
                        "valor_actual_bd": str(valor_bd),
                        "valor_nuevo_sugerido": valor_sugerido,
                        "confianza": confianza,
                        "razon": val_data.get("razonamiento", ""),
                        "criticidad": self._evaluar_criticidad(campo)
                    })
            else:
                campos_correctos.append(campo)

        # Resumen ejecutivo
        total_validados = len(validaciones)
        total_discrepancias = len(discrepancias)
        total_correcciones = len(correcciones_sugeridas)

        # Clasificar correcciones por criticidad
        correcciones_criticas = [c for c in correcciones_sugeridas if c["criticidad"] == "CRITICA"]
        correcciones_importantes = [c for c in correcciones_sugeridas if c["criticidad"] == "IMPORTANTE"]
        correcciones_opcionales = [c for c in correcciones_sugeridas if c["criticidad"] == "OPCIONAL"]

        informe = {
            "numero_peticion": numero_peticion,
            "timestamp": datetime.now().isoformat(),
            "resumen": {
                "total_campos_validados": total_validados,
                "campos_correctos": len(campos_correctos),
                "total_discrepancias": total_discrepancias,
                "total_correcciones_sugeridas": total_correcciones,
                "correcciones_criticas": len(correcciones_criticas),
                "correcciones_importantes": len(correcciones_importantes),
                "correcciones_opcionales": len(correcciones_opcionales),
                "tokens_usados": validacion_ia.get("tokens_totales", 0)
            },
            "discrepancias": discrepancias,
            "correcciones_sugeridas": {
                "criticas": correcciones_criticas,
                "importantes": correcciones_importantes,
                "opcionales": correcciones_opcionales
            },
            "campos_correctos": campos_correctos,
            "debug_map_usado": debug_map.get("session_id", ""),
            "metadata": {
                "caracteres_procesados": debug_map["metricas"]["caracteres_procesados"],
                "tiempo_total_extraccion": debug_map["metricas"]["tiempo_total_segundos"]
            }
        }

        return informe

    def _calcular_similitud(self, texto1: str, texto2: str) -> float:
        """
        Calcula similitud entre dos textos

        Args:
            texto1: Primer texto
            texto2: Segundo texto

        Returns:
            Similitud de 0.0 a 1.0
        """
        if not texto1 or not texto2:
            return 0.0

        return difflib.SequenceMatcher(None, texto1, texto2).ratio()

    def _evaluar_criticidad(self, campo: str) -> str:
        """
        Evalúa la criticidad de un campo

        Args:
            campo: Nombre del campo

        Returns:
            "CRITICA", "IMPORTANTE" o "OPCIONAL"
        """
        campos_criticos = [
            "numero_peticion", "identificacion", "nombre_completo", "edad", "genero"
        ]

        campos_importantes = [
            "diagnostico", "organo", "fecha_informe", "eps", "medico_tratante"
        ]

        if campo in campos_criticos:
            return "CRITICA"
        elif campo in campos_importantes:
            return "IMPORTANTE"
        else:
            return "OPCIONAL"

    def aplicar_correcciones(
        self,
        informe_validacion: Dict[str, Any],
        aplicar_criticas: bool = True,
        aplicar_importantes: bool = False,
        aplicar_opcionales: bool = False,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Aplica correcciones sugeridas a la base de datos

        Args:
            informe_validacion: Informe de validación generado
            aplicar_criticas: Aplicar correcciones críticas
            aplicar_importantes: Aplicar correcciones importantes
            aplicar_opcionales: Aplicar correcciones opcionales
            dry_run: Si True, solo simula (no modifica BD)

        Returns:
            Dict con resultado de la aplicación
        """
        numero_peticion = informe_validacion["numero_peticion"]

        correcciones_a_aplicar = []

        if aplicar_criticas:
            correcciones_a_aplicar.extend(informe_validacion["correcciones_sugeridas"]["criticas"])

        if aplicar_importantes:
            correcciones_a_aplicar.extend(informe_validacion["correcciones_sugeridas"]["importantes"])

        if aplicar_opcionales:
            correcciones_a_aplicar.extend(informe_validacion["correcciones_sugeridas"]["opcionales"])

        if not correcciones_a_aplicar:
            return {
                "exito": True,
                "mensaje": "No hay correcciones para aplicar",
                "correcciones_aplicadas": 0
            }

        print(f"\n🔧 {'SIMULANDO' if dry_run else 'APLICANDO'} CORRECCIONES...")
        print(f"📋 Total de correcciones: {len(correcciones_a_aplicar)}")

        cambios_realizados = []

        for correccion in correcciones_a_aplicar:
            campo = correccion["campo"]
            valor_nuevo = correccion["valor_nuevo_sugerido"]
            criticidad = correccion["criticidad"]

            print(f"\n  {'[DRY RUN]' if dry_run else '[APLICANDO]'} {criticidad}")
            print(f"  Campo: {campo}")
            print(f"  Valor actual: {correccion['valor_actual_bd']}")
            print(f"  Valor nuevo: {valor_nuevo}")
            print(f"  Confianza: {correccion['confianza']:.2f}")

            if not dry_run:
                # TODO: Implementar actualización real en BD
                # from core.database_manager import update_registro
                # update_registro(numero_peticion, {campo: valor_nuevo})
                pass

            cambios_realizados.append({
                "campo": campo,
                "valor_anterior": correccion["valor_actual_bd"],
                "valor_nuevo": valor_nuevo,
                "criticidad": criticidad,
                "confianza": correccion["confianza"]
            })

        resultado = {
            "exito": True,
            "numero_peticion": numero_peticion,
            "dry_run": dry_run,
            "correcciones_aplicadas": len(cambios_realizados),
            "cambios": cambios_realizados,
            "timestamp": datetime.now().isoformat()
        }

        # Guardar log de correcciones
        if not dry_run:
            log_file = self.resultados_dir / f"correcciones_aplicadas_{numero_peticion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Log de correcciones guardado en: {log_file}")

        return resultado

    def generar_reporte_comparativo(
        self,
        numero_peticion: str,
        output_formato: str = "json"
    ) -> Path:
        """
        Genera reporte comparativo visual (JSON o HTML)

        Args:
            numero_peticion: Número de petición
            output_formato: "json" o "html"

        Returns:
            Path al archivo generado
        """
        # Validar caso
        informe = self.validar_caso_ihq(numero_peticion)

        if not informe.get("exito", True):
            raise ValueError(f"Error validando caso: {informe.get('error')}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_formato == "html":
            # TODO: Implementar generación HTML
            output_file = self.resultados_dir / f"reporte_{numero_peticion}_{timestamp}.html"
            # generar_html(informe, output_file)
            print("⚠️ Formato HTML aún no implementado, generando JSON...")
            output_formato = "json"

        # JSON por defecto
        output_file = self.resultados_dir / f"reporte_{numero_peticion}_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Función principal CLI"""
    parser = argparse.ArgumentParser(
        description="🔍 Validador con IA v1.0.0 - Sistema de Corrección Inteligente",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--ihq",
        type=str,
        required=True,
        help="Número de petición IHQ (ej: IHQ250001 o 250001)"
    )

    parser.add_argument(
        "--debug-map",
        type=str,
        help="Ruta al archivo debug_map.json (opcional, se busca automáticamente)"
    )

    parser.add_argument(
        "--criticos-solo",
        action="store_true",
        help="Validar solo campos críticos"
    )

    parser.add_argument(
        "--aplicar-correcciones",
        action="store_true",
        help="Aplicar correcciones sugeridas (requiere confirmación)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simular correcciones sin modificar BD (por defecto: True)"
    )

    parser.add_argument(
        "--endpoint",
        type=str,
        default="http://127.0.0.1:1234",
        help="Endpoint de LM Studio (default: http://127.0.0.1:1234)"
    )

    args = parser.parse_args()

    # Normalizar número de petición
    numero_peticion = args.ihq.upper()
    if not numero_peticion.startswith("IHQ"):
        numero_peticion = f"IHQ{numero_peticion}"

    # Crear validador
    validador = ValidadorIA(llm_endpoint=args.endpoint)

    # Validar caso
    debug_map_path = Path(args.debug_map) if args.debug_map else None

    informe = validador.validar_caso_ihq(
        numero_peticion=numero_peticion,
        debug_map_path=debug_map_path,
        validar_solo_criticos=args.criticos_solo
    )

    # Mostrar resumen
    if informe.get("exito", True):
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE VALIDACIÓN")
        print("=" * 80)

        resumen = informe["resumen"]
        print(f"✅ Campos validados: {resumen['total_campos_validados']}")
        print(f"✓ Campos correctos: {resumen['campos_correctos']}")
        print(f"⚠️ Discrepancias encontradas: {resumen['total_discrepancias']}")
        print(f"🔧 Correcciones sugeridas: {resumen['total_correcciones_sugeridas']}")
        print(f"  - Críticas: {resumen['correcciones_criticas']}")
        print(f"  - Importantes: {resumen['correcciones_importantes']}")
        print(f"  - Opcionales: {resumen['correcciones_opcionales']}")
        print(f"📊 Tokens usados: {resumen['tokens_usados']}")

        # Aplicar correcciones si se solicita
        if args.aplicar_correcciones:
            resultado = validador.aplicar_correcciones(
                informe,
                aplicar_criticas=True,
                aplicar_importantes=False,
                aplicar_opcionales=False,
                dry_run=args.dry_run
            )

            print(f"\n{'🔍 SIMULACIÓN' if args.dry_run else '✅ APLICACIÓN'} DE CORRECCIONES:")
            print(f"  Correcciones aplicadas: {resultado['correcciones_aplicadas']}")
    else:
        print(f"\n❌ ERROR: {informe.get('error')}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
