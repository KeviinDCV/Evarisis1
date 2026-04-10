#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuditWorker - Worker asíncrono para auditoría IA
Worker QThread para ejecutar auditorías inteligentes sin bloquear la UI

Características:
- Auditoría asíncrona con validación semántica
- Integración con herramientas_ia/auditor_sistema.py
- Progreso en tiempo real
- Manejo de múltiples casos
"""

from PySide6.QtCore import QThread, Signal
from typing import List, Dict, Any, Optional
import traceback
from pathlib import Path


class AuditWorker(QThread):
    """
    Worker para auditoría IA asíncrona

    Signals:
        progress(int, str): Emite (porcentaje, mensaje) durante auditoría
        case_completed(str, dict): Emite (caso_id, resultado) por cada caso auditado
        finished(dict): Emite resultados finales cuando completa
        error(str): Emite mensaje de error si falla
    """

    # Signals
    progress = Signal(int, str)
    case_completed = Signal(str, dict)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, case_id: str, audit_type: str = 'inteligente', parent=None):
        """
        Inicializa el worker de auditoría

        Args:
            case_id: ID del caso a auditar (ej: 'IHQ251001')
            audit_type: Tipo de auditoría ('inteligente', 'basica', 'completa')
            parent: Widget padre
        """
        super().__init__(parent)
        self.case_id = case_id
        self.audit_type = audit_type
        self._is_cancelled = False

    def cancel(self):
        """Cancela la auditoría"""
        self._is_cancelled = True

    def run(self):
        """Ejecuta la auditoría en thread separado"""
        try:
            self.progress.emit(0, f"Iniciando auditoría {self.audit_type} para {self.case_id}...")

            # Importar módulo de auditoría
            from herramientas_ia.auditor_sistema import AuditorSistema

            # Crear instancia del auditor
            auditor = AuditorSistema()

            self.progress.emit(20, "Auditor inicializado. Cargando caso...")

            # Verificar si existe debug_map
            debug_map_path = Path(f"debug_maps/{self.case_id}/debug_map.json")
            if not debug_map_path.exists():
                self.error.emit(
                    f"No se encontró debug_map para {self.case_id}\n\n"
                    f"Ruta esperada: {debug_map_path}\n\n"
                    "El caso debe haber sido procesado previamente."
                )
                return

            self.progress.emit(40, "Debug map encontrado. Ejecutando validación...")

            # Ejecutar auditoría (solo modo inteligente disponible)
            # auditar_caso_inteligente(numero_caso, json_export=False, nivel='completo')
            if self.audit_type == 'inteligente':
                nivel = 'completo'
            elif self.audit_type == 'basica':
                nivel = 'basico'
            elif self.audit_type == 'completa':
                nivel = 'completo'
            else:
                nivel = 'completo'

            resultado = auditor.auditar_caso_inteligente(
                self.case_id,
                json_export=False,
                nivel=nivel
            )

            if self._is_cancelled:
                self.progress.emit(0, "Auditoría cancelada")
                return

            self.progress.emit(80, "Validación completada. Generando reporte...")

            # Procesar resultado
            if resultado:
                # Estructura del resultado de auditar_caso_inteligente():
                # {
                #   'metricas': {'score': float, 'validaciones_ok': int, ...},
                #   'auditoria_bd': {'errores': [...], 'warnings': [...]},
                #   ...
                # }
                metricas = resultado.get('metricas', {})
                auditoria_bd = resultado.get('auditoria_bd', {})

                score = metricas.get('score', 0.0)
                estado = metricas.get('estado', 'DESCONOCIDO')
                errores = auditoria_bd.get('errores', [])
                warnings = auditoria_bd.get('warnings', [])
                errores_count = len(errores) + len(warnings)

                # Mensaje de estado
                if score >= 95:
                    status_msg = f"✓ EXCELENTE ({score:.1f}%)"
                elif score >= 80:
                    status_msg = f"⚠ ACEPTABLE ({score:.1f}%)"
                else:
                    status_msg = f"✗ REQUIERE ATENCIÓN ({score:.1f}%)"

                self.progress.emit(
                    90,
                    f"Auditoría completada: {status_msg}"
                )

                # Emitir caso completado
                self.case_completed.emit(self.case_id, resultado)

                # Resultado final
                final_result = {
                    'case_id': self.case_id,
                    'audit_type': self.audit_type,
                    'score': score,
                    'estado': estado,
                    'errores_count': errores_count,
                    'errores': errores,
                    'warnings': warnings,
                    'resultado_completo': resultado
                }

                self.progress.emit(100, "Auditoría finalizada exitosamente")
                self.finished.emit(final_result)

            else:
                self.error.emit(
                    f"La auditoría de {self.case_id} no retornó resultados.\n"
                    "Verifica que el caso esté correctamente procesado."
                )

        except ImportError as e:
            error_msg = (
                f"Error de importación: {str(e)}\n\n"
                "Asegúrate de que el módulo de auditoría esté disponible:\n"
                "- herramientas_ia/auditor_sistema.py"
            )
            self.error.emit(error_msg)

        except Exception as e:
            error_msg = (
                f"Error durante auditoría de {self.case_id}:\n\n"
                f"{str(e)}\n\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            self.error.emit(error_msg)


class BatchAuditWorker(QThread):
    """
    Worker para auditoría de múltiples casos

    Ejecuta auditorías secuenciales con reporte consolidado
    """

    progress = Signal(int, str)
    case_completed = Signal(str, dict)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(
        self,
        case_ids: List[str],
        audit_type: str = 'inteligente',
        parent=None
    ):
        """
        Inicializa worker de auditoría por lotes

        Args:
            case_ids: Lista de IDs de casos
            audit_type: Tipo de auditoría
            parent: Widget padre
        """
        super().__init__(parent)
        self.case_ids = case_ids
        self.audit_type = audit_type
        self._is_cancelled = False

        self.results = {
            'cases_processed': [],
            'cases_failed': [],
            'total': len(case_ids),
            'average_score': 0.0,
            'high_quality': 0,   # score >= 95
            'medium_quality': 0,  # 80 <= score < 95
            'low_quality': 0      # score < 80
        }

    def cancel(self):
        """Cancela auditoría por lotes"""
        self._is_cancelled = True

    def run(self):
        """Ejecuta auditorías secuenciales"""
        try:
            from herramientas_ia.auditor_sistema import AuditorSistema

            self.progress.emit(
                0,
                f"Iniciando auditoría de {len(self.case_ids)} casos..."
            )

            auditor = AuditorSistema()
            total_score = 0.0

            for idx, case_id in enumerate(self.case_ids):
                if self._is_cancelled:
                    self.progress.emit(0, "Auditoría por lotes cancelada")
                    return

                # Progreso
                progress_pct = int((idx / len(self.case_ids)) * 100)
                self.progress.emit(
                    progress_pct,
                    f"[{idx+1}/{len(self.case_ids)}] Auditando {case_id}..."
                )

                try:
                    # Ejecutar auditoría inteligente
                    resultado = auditor.auditar_caso_inteligente(
                        case_id,
                        json_export=False,
                        nivel='completo'
                    )

                    if resultado:
                        metricas = resultado.get('metricas', {})
                        score = metricas.get('score', 0.0)
                        estado = metricas.get('estado', 'DESCONOCIDO')

                        # Acumular para promedio
                        total_score += score

                        # Clasificar por calidad
                        if score >= 95:
                            self.results['high_quality'] += 1
                        elif score >= 80:
                            self.results['medium_quality'] += 1
                        else:
                            self.results['low_quality'] += 1

                        # Guardar resultado
                        self.results['cases_processed'].append({
                            'case_id': case_id,
                            'score': score,
                            'estado': estado,
                            'resultado': resultado
                        })

                        # Emitir caso completado
                        self.case_completed.emit(case_id, resultado)

                        self.progress.emit(
                            progress_pct,
                            f"  ✓ {case_id}: {score:.1f}% ({estado})"
                        )

                    else:
                        # Caso falló
                        self.results['cases_failed'].append({
                            'case_id': case_id,
                            'error': 'No se obtuvieron resultados'
                        })

                        self.progress.emit(
                            progress_pct,
                            f"  ✗ {case_id}: ERROR"
                        )

                except Exception as e:
                    # Error en caso individual
                    self.results['cases_failed'].append({
                        'case_id': case_id,
                        'error': str(e)
                    })

                    self.progress.emit(
                        progress_pct,
                        f"  ✗ {case_id}: ERROR - {str(e)[:50]}"
                    )

            # Calcular estadísticas
            if self.results['cases_processed']:
                self.results['average_score'] = total_score / len(self.results['cases_processed'])

            # Mensaje final
            summary = (
                f"\n=== RESUMEN DE AUDITORÍA ===\n"
                f"Total: {self.results['total']}\n"
                f"Procesados: {len(self.results['cases_processed'])}\n"
                f"Fallidos: {len(self.results['cases_failed'])}\n"
                f"Score Promedio: {self.results['average_score']:.1f}%\n"
                f"Alta Calidad (≥95%): {self.results['high_quality']}\n"
                f"Media Calidad (80-94%): {self.results['medium_quality']}\n"
                f"Baja Calidad (<80%): {self.results['low_quality']}"
            )

            self.progress.emit(100, summary)
            self.finished.emit(self.results)

        except ImportError as e:
            self.error.emit(f"Error de importación: {str(e)}\n\nAsegúrate de que herramientas_ia/auditor_sistema.py esté disponible.")

        except Exception as e:
            self.error.emit(f"Error en auditoría por lotes: {str(e)}\n{traceback.format_exc()}")


class RepairWorker(QThread):
    """
    Worker para reprocesar caso completo (FUNC-06)

    Elimina datos antiguos + regenera con extractores actuales
    """

    progress = Signal(int, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, case_id: str, parent=None):
        """
        Inicializa worker de reparación

        Args:
            case_id: ID del caso a reprocesar
            parent: Widget padre
        """
        super().__init__(parent)
        self.case_id = case_id
        self._is_cancelled = False

    def cancel(self):
        """Cancela reparación"""
        self._is_cancelled = True

    def run(self):
        """Ejecuta reprocesamiento completo"""
        try:
            self.progress.emit(0, f"Iniciando reprocesamiento de {self.case_id}...")

            from herramientas_ia.auditor_sistema import AuditorSistema

            auditor = AuditorSistema()

            self.progress.emit(20, "Eliminando datos antiguos...")

            # Ejecutar FUNC-06
            resultado = auditor.reprocesar_caso_completo(self.case_id)

            if self._is_cancelled:
                return

            self.progress.emit(60, "Regenerando con extractores actuales...")

            if resultado and resultado.get('exito', False):
                self.progress.emit(80, "Validando caso regenerado...")

                # Obtener comparación antes/después
                comparacion = resultado.get('comparacion', {})
                score_nuevo = comparacion.get('despues', {}).get('score', 0.0)

                self.progress.emit(
                    100,
                    f"Reprocesamiento completado. Score nuevo: {score_nuevo:.1f}%"
                )

                self.finished.emit(resultado)
            else:
                error_msg = resultado.get('error', 'Error desconocido')
                self.error.emit(f"Fallo al reprocesar {self.case_id}: {error_msg}")

        except ImportError as e:
            self.error.emit(f"Error de importación: {str(e)}")

        except Exception as e:
            self.error.emit(f"Error en reprocesamiento: {str(e)}\n{traceback.format_exc()}")


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QTextEdit, QVBoxLayout,
        QWidget, QPushButton, QLineEdit, QHBoxLayout, QLabel
    )

    app = QApplication(sys.argv)

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test AuditWorker")
            self.resize(800, 600)

            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)

            # Input para caso ID
            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel("Caso ID:"))
            self.case_input = QLineEdit()
            self.case_input.setText("IHQ251001")
            input_layout.addWidget(self.case_input)
            layout.addLayout(input_layout)

            # Log
            self.log = QTextEdit()
            self.log.setReadOnly(True)
            layout.addWidget(self.log)

            # Botones
            btn_layout = QHBoxLayout()

            btn_audit = QPushButton("Auditoría Inteligente")
            btn_audit.clicked.connect(self.start_audit)
            btn_layout.addWidget(btn_audit)

            btn_repair = QPushButton("Reprocesar Caso")
            btn_repair.clicked.connect(self.start_repair)
            btn_layout.addWidget(btn_repair)

            layout.addLayout(btn_layout)

        def start_audit(self):
            case_id = self.case_input.text()
            self.log.clear()
            self.log.append(f"=== Iniciando auditoría de {case_id} ===\n")

            self.worker = AuditWorker(case_id, 'inteligente')
            self.worker.progress.connect(
                lambda p, m: self.log.append(f"[{p}%] {m}")
            )
            self.worker.finished.connect(
                lambda r: self.log.append(f"\n=== RESULTADO ===\n{r}")
            )
            self.worker.error.connect(
                lambda e: self.log.append(f"\n=== ERROR ===\n{e}")
            )

            self.worker.start()

        def start_repair(self):
            case_id = self.case_input.text()
            self.log.clear()
            self.log.append(f"=== Reprocesando {case_id} ===\n")

            self.worker = RepairWorker(case_id)
            self.worker.progress.connect(
                lambda p, m: self.log.append(f"[{p}%] {m}")
            )
            self.worker.finished.connect(
                lambda r: self.log.append(f"\n=== COMPLETADO ===\n{r}")
            )
            self.worker.error.connect(
                lambda e: self.log.append(f"\n=== ERROR ===\n{e}")
            )

            self.worker.start()

    window = TestWindow()
    window.show()

    sys.exit(app.exec())
