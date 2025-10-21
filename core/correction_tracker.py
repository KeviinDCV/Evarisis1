#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CORRECTION TRACKER - EVARISIS CIRUGÍA ONCOLÓGICA
===================================================

Sistema centralizado para tracking de correcciones automáticas aplicadas
durante el proceso de extracción y validación de datos médicos.

Tipos de correcciones soportadas:
- Ortográficas (errores OCR)
- Médico-Servicio (validación especialidad)
- Normalización de biomarcadores

Autor: Sistema EVARISIS CIRUGÍA ONCOLÓGICA
Versión: 5.3.9
Fecha: 19 de octubre de 2025
"""

import sys
import logging
import io
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

# Configurar salida UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class CorrectionTracker:
    """
    Sistema de tracking de correcciones automáticas

    Acumula todas las correcciones aplicadas durante el procesamiento
    y proporciona métodos para consultar y serializar las correcciones.
    """

    def __init__(self):
        """Inicializar tracker de correcciones"""
        self.correcciones: List[Dict] = []

    def add_correction(
        self,
        tipo: str,
        campo: str,
        valor_original: str,
        valor_corregido: str,
        razon: str,
        numero_caso: str = "",
        metadata: Optional[Dict] = None
    ):
        """
        Registrar una corrección aplicada

        Args:
            tipo: Tipo de corrección ('ortografica', 'medico_servicio', 'normalizacion_biomarcador')
            campo: Nombre del campo corregido
            valor_original: Valor antes de la corrección
            valor_corregido: Valor después de la corrección
            razon: Explicación de por qué se corrigió
            numero_caso: Número de caso IHQ (opcional)
            metadata: Información adicional (opcional)
        """
        # Validar que realmente hubo un cambio
        if str(valor_original) == str(valor_corregido):
            return  # No hay corrección real

        correccion = {
            "tipo": tipo,
            "campo": campo,
            "valor_original": str(valor_original),
            "valor_corregido": str(valor_corregido),
            "razon": razon,
            "numero_caso": numero_caso,
            "timestamp": datetime.now().isoformat()
        }

        # Agregar metadata si existe
        if metadata:
            correccion.update(metadata)

        self.correcciones.append(correccion)

    def get_all_corrections(self) -> List[Dict]:
        """
        Obtener todas las correcciones registradas

        Returns:
            Lista de diccionarios con todas las correcciones
        """
        return self.correcciones.copy()

    def get_corrections_by_type(self, tipo: str) -> List[Dict]:
        """
        Obtener correcciones de un tipo específico

        Args:
            tipo: Tipo de corrección a filtrar

        Returns:
            Lista de correcciones del tipo especificado
        """
        return [c for c in self.correcciones if c.get("tipo") == tipo]

    def get_corrections_by_case(self, numero_caso: str) -> List[Dict]:
        """
        Obtener correcciones de un caso específico

        Args:
            numero_caso: Número de caso IHQ

        Returns:
            Lista de correcciones del caso especificado
        """
        return [c for c in self.correcciones if c.get("numero_caso") == numero_caso]

    def get_corrections_by_field(self, campo: str) -> List[Dict]:
        """
        Obtener correcciones de un campo específico

        Args:
            campo: Nombre del campo

        Returns:
            Lista de correcciones del campo especificado
        """
        return [c for c in self.correcciones if c.get("campo") == campo]

    def get_statistics(self) -> Dict:
        """
        Obtener estadísticas de correcciones

        Returns:
            Diccionario con estadísticas:
            - total: Total de correcciones
            - por_tipo: Conteo por tipo
            - por_campo: Conteo por campo
            - por_caso: Conteo por caso
        """
        stats = {
            "total": len(self.correcciones),
            "por_tipo": defaultdict(int),
            "por_campo": defaultdict(int),
            "por_caso": defaultdict(int)
        }

        for corr in self.correcciones:
            stats["por_tipo"][corr.get("tipo", "unknown")] += 1
            stats["por_campo"][corr.get("campo", "unknown")] += 1
            stats["por_caso"][corr.get("numero_caso", "unknown")] += 1

        # Convertir defaultdict a dict normal para serialización
        stats["por_tipo"] = dict(stats["por_tipo"])
        stats["por_campo"] = dict(stats["por_campo"])
        stats["por_caso"] = dict(stats["por_caso"])

        return stats

    def has_corrections(self) -> bool:
        """
        Verificar si hay correcciones registradas

        Returns:
            True si hay al menos una corrección
        """
        return len(self.correcciones) > 0

    def count_corrections(self) -> int:
        """
        Contar total de correcciones

        Returns:
            Número total de correcciones
        """
        return len(self.correcciones)

    def count_by_type(self, tipo: str) -> int:
        """
        Contar correcciones de un tipo específico

        Args:
            tipo: Tipo de corrección

        Returns:
            Número de correcciones de ese tipo
        """
        return len(self.get_corrections_by_type(tipo))

    def clear(self):
        """Limpiar todas las correcciones registradas"""
        self.correcciones = []

    def to_dict(self) -> Dict:
        """
        Convertir tracker a diccionario serializable

        Returns:
            Diccionario con correcciones y estadísticas
        """
        return {
            "correcciones": self.get_all_corrections(),
            "estadisticas": self.get_statistics()
        }

    def __len__(self) -> int:
        """Permite usar len(tracker) para contar correcciones"""
        return len(self.correcciones)

    def __bool__(self) -> bool:
        """Permite usar if tracker: para verificar si hay correcciones"""
        return self.has_corrections()

    def __repr__(self) -> str:
        """Representación string del tracker"""
        stats = self.get_statistics()
        return f"CorrectionTracker(total={stats['total']}, por_tipo={stats['por_tipo']})"


# ─────────────────────── FUNCIONES HELPER ───────────────────────

def merge_corrections(trackers: List[CorrectionTracker]) -> CorrectionTracker:
    """
    Combinar múltiples trackers en uno solo

    Args:
        trackers: Lista de CorrectionTracker

    Returns:
        Nuevo tracker con todas las correcciones combinadas
    """
    merged = CorrectionTracker()

    for tracker in trackers:
        merged.correcciones.extend(tracker.get_all_corrections())

    return merged


def format_correction_summary(tracker: CorrectionTracker) -> str:
    """
    Generar resumen formateado de correcciones

    Args:
        tracker: CorrectionTracker con correcciones

    Returns:
        String con resumen legible
    """
    if not tracker:
        return "✅ No se aplicaron correcciones automáticas"

    stats = tracker.get_statistics()

    summary = f"🔧 CORRECCIONES AUTOMÁTICAS APLICADAS: {stats['total']}\n"
    summary += "=" * 60 + "\n\n"

    # Resumen por tipo
    for tipo, count in stats["por_tipo"].items():
        tipo_label = {
            "ortografica": "📝 Correcciones Ortográficas",
            "medico_servicio": "🩺 Validación Médico-Servicio",
            "normalizacion_biomarcador": "🧬 Normalización Biomarcadores"
        }.get(tipo, f"📌 {tipo}")

        summary += f"{tipo_label}: {count}\n"

    summary += "\n" + "=" * 60

    return summary


def print_corrections_detail(tracker: CorrectionTracker, max_items: int = 10):
    """
    Imprimir detalle de correcciones en consola

    Args:
        tracker: CorrectionTracker con correcciones
        max_items: Máximo de items a mostrar por tipo
    """
    if not tracker:
        logging.info("✅ No se aplicaron correcciones automáticas")
        return

    logging.info(format_correction_summary(tracker))
    logging.info("\n" + "📋 DETALLE DE CORRECCIONES".center(60))
    logging.info("=" * 60)

    # Agrupar por tipo
    por_tipo = {
        "ortografica": tracker.get_corrections_by_type("ortografica"),
        "medico_servicio": tracker.get_corrections_by_type("medico_servicio"),
        "normalizacion_biomarcador": tracker.get_corrections_by_type("normalizacion_biomarcador")
    }

    for tipo, correcciones in por_tipo.items():
        if not correcciones:
            continue

        tipo_label = {
            "ortografica": "📝 CORRECCIONES ORTOGRÁFICAS",
            "medico_servicio": "🩺 VALIDACIÓN MÉDICO-SERVICIO",
            "normalizacion_biomarcador": "🧬 NORMALIZACIÓN BIOMARCADORES"
        }.get(tipo, tipo.upper())

        logging.info(f"\n{tipo_label} ({len(correcciones)}):")
        logging.info("-" * 60)

        for i, corr in enumerate(correcciones[:max_items], 1):
            caso = corr.get("numero_caso", "N/A")
            campo = corr.get("campo", "N/A")
            antes = corr.get("valor_original", "")[:30]  # Truncar si es muy largo
            despues = corr.get("valor_corregido", "")[:30]
            razon = corr.get("razon", "")

            logging.info(f"{i}. {caso} | {campo}")
            logging.info(f"   Antes:   {antes}")
            logging.info(f"   Después: {despues}")
            logging.info(f"   Razón:   {razon}")
            logging.info()

        if len(correcciones) > max_items:
            logging.info(f"   ... y {len(correcciones) - max_items} más\n")


# ─────────────────────── TESTING ───────────────────────

if __name__ == "__main__":
    logging.info("🧪 Testing CorrectionTracker\n")
    logging.info("=" * 60)

    # Crear tracker
    tracker = CorrectionTracker()

    # Agregar correcciones de prueba
    tracker.add_correction(
        tipo="ortografica",
        campo="Diagnostico Principal",
        valor_original="CARCIN0MA INVASIVO",
        valor_corregido="CARCINOMA INVASIVO",
        razon="Corrección OCR: 0 → O",
        numero_caso="IHQ250980"
    )

    tracker.add_correction(
        tipo="medico_servicio",
        campo="Servicio",
        valor_original="NEUROCIRUGIA",
        valor_corregido="UNIDAD DE ONCOLOGIA COEX",
        razon="Dr. LUIS ALFONSO GONZALEZ es Cirujano Oncólogo",
        numero_caso="IHQ250980",
        metadata={"medico": "LUIS ALFONSO GONZALEZ"}
    )

    tracker.add_correction(
        tipo="normalizacion_biomarcador",
        campo="Ki-67",
        valor_original="KI 67",
        valor_corregido="KI-67",
        razon="Normalización de formato de biomarcador",
        numero_caso="IHQ250980"
    )

    # Mostrar resultados
    logging.info(f"\n{tracker}\n")
    print_corrections_detail(tracker)

    # Estadísticas
    logging.info("\n📊 ESTADÍSTICAS:")
    logging.info("=" * 60)
    stats = tracker.get_statistics()
    logging.info(f"Total correcciones: {stats['total']}")
    logging.info(f"Por tipo: {stats['por_tipo']}")
    logging.info(f"Por campo: {stats['por_campo']}")
    logging.info(f"Por caso: {stats['por_caso']}")

    logging.info("\n✅ Test completado exitosamente!")
