#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCRWorker - Worker asíncrono para procesamiento OCR
Worker QThread para procesar PDFs con OCR sin bloquear la UI

Características:
- Procesamiento asíncrono en background
- Emisión de progreso en tiempo real
- Manejo robusto de errores
- Cancelación segura
"""

from PySide6.QtCore import QThread, Signal
from pathlib import Path
from typing import List, Dict, Any, Optional
import traceback


class OCRWorker(QThread):
    """
    Worker para procesamiento OCR asíncrono

    Signals:
        progress(int, str): Emite (porcentaje, mensaje) durante procesamiento
        file_processed(str, dict): Emite (archivo, resultado) por cada PDF procesado
        finished(dict): Emite resultados finales cuando completa
        error(str): Emite mensaje de error si falla
    """

    # Signals
    progress = Signal(int, str)           # (porcentaje, mensaje)
    file_processed = Signal(str, dict)    # (archivo, resultado)
    finished = Signal(dict)               # resultados finales
    error = Signal(str)                   # mensaje de error

    def __init__(self, pdf_paths: List[str], parent=None):
        """
        Inicializa el worker OCR

        Args:
            pdf_paths: Lista de rutas a archivos PDF
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self.pdf_paths = pdf_paths
        self._is_cancelled = False
        self.results = {
            'success': [],
            'failed': [],
            'total': len(pdf_paths),
            'success_count': 0,
            'failed_count': 0
        }

    def cancel(self):
        """Cancela el procesamiento de manera segura"""
        self._is_cancelled = True
        self.progress.emit(0, "Cancelando procesamiento...")

    def run(self):
        """
        Ejecuta el procesamiento OCR en thread separado

        Este método se ejecuta automáticamente cuando se llama a start()
        """
        try:
            # Importar módulos del backend (API CORRECTA)
            from core.unified_extractor import process_ihq_paths
            from core.database_manager import init_db
            import tempfile

            # Inicializar BD si no existe
            init_db()

            self.progress.emit(0, f"Iniciando procesamiento de {len(self.pdf_paths)} archivos...")

            # El backend procesa TODOS los PDFs de una vez
            # Crear directorio temporal para salida
            with tempfile.TemporaryDirectory() as temp_output:
                try:
                    # Emitir progreso inicial
                    self.progress.emit(
                        5,
                        f"Procesando {len(self.pdf_paths)} archivos con unified_extractor..."
                    )

                    # LLAMAR AL BACKEND EXISTENTE
                    # process_ihq_paths() retorna el número de casos procesados
                    casos_procesados = process_ihq_paths(
                        pdf_paths=self.pdf_paths,
                        output_dir=temp_output
                    )

                    # Emitir progreso durante procesamiento
                    # (el backend no emite progreso interno, así que simulamos)
                    for i in range(10, 90, 10):
                        if self._is_cancelled:
                            self.progress.emit(0, "Procesamiento cancelado")
                            return
                        self.progress.emit(i, f"Procesando casos... ({i}%)")
                        self.msleep(100)  # Pequeña pausa para actualizar UI

                    # Resultado exitoso
                    self.progress.emit(95, f"Procesamiento completado: {casos_procesados} casos")

                    # Actualizar contadores
                    self.results['success_count'] = casos_procesados
                    self.results['failed_count'] = 0

                    # Registrar éxito por cada archivo
                    for pdf_path in self.pdf_paths:
                        self.results['success'].append({
                            'file': pdf_path,
                            'casos_procesados': casos_procesados // len(self.pdf_paths)  # Estimación
                        })

                except Exception as e:
                    # Error durante procesamiento
                    error_msg = f"Error en process_ihq_paths: {str(e)}"
                    self.progress.emit(0, f"✗ {error_msg}")

                    self.results['failed_count'] = len(self.pdf_paths)
                    for pdf_path in self.pdf_paths:
                        self.results['failed'].append({
                            'file': pdf_path,
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        })

                    # Emitir error
                    self.error.emit(error_msg)
                    return

            # Completado
            self.progress.emit(100, "Procesamiento completado")

            # Emitir resumen final
            summary_msg = (
                f"\n=== RESUMEN ===\n"
                f"Total: {self.results['total']}\n"
                f"Exitosos: {self.results['success_count']}\n"
                f"Fallidos: {self.results['failed_count']}"
            )
            self.progress.emit(100, summary_msg)

            # Emitir signal de finalización
            self.finished.emit(self.results)

        except ImportError as e:
            # Error al importar módulos del backend
            error_msg = (
                f"Error de importación: {str(e)}\n\n"
                "Asegúrate de que los módulos del backend estén disponibles:\n"
                "- core/unified_extractor.py\n"
                "- core/database_manager.py"
            )
            self.error.emit(error_msg)
            self.progress.emit(0, "ERROR: Módulos backend no disponibles")

        except Exception as e:
            # Error general durante procesamiento
            error_msg = (
                f"Error crítico durante procesamiento:\n\n"
                f"{str(e)}\n\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            self.error.emit(error_msg)
            self.progress.emit(0, f"ERROR: {str(e)}")


class OCRBatchWorker(QThread):
    """
    Worker para procesamiento OCR en lotes grandes

    Optimizado para manejar +100 archivos con mejor control de memoria
    """

    progress = Signal(int, str)
    batch_completed = Signal(int, dict)  # (batch_number, results)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, pdf_paths: List[str], batch_size: int = 10, parent=None):
        """
        Inicializa el worker de lotes

        Args:
            pdf_paths: Lista de rutas PDF
            batch_size: Tamaño de cada lote (default: 10)
            parent: Widget padre
        """
        super().__init__(parent)
        self.pdf_paths = pdf_paths
        self.batch_size = batch_size
        self._is_cancelled = False

        # Dividir en lotes
        self.batches = [
            pdf_paths[i:i+batch_size]
            for i in range(0, len(pdf_paths), batch_size)
        ]

        self.results = {
            'success': [],
            'failed': [],
            'total': len(pdf_paths),
            'batches_processed': 0,
            'total_batches': len(self.batches)
        }

    def cancel(self):
        """Cancela procesamiento"""
        self._is_cancelled = True

    def run(self):
        """Ejecuta procesamiento por lotes"""
        try:
            self.progress.emit(
                0,
                f"Procesando {self.results['total']} archivos en "
                f"{self.results['total_batches']} lotes"
            )

            for batch_idx, batch in enumerate(self.batches):
                if self._is_cancelled:
                    return

                # Crear worker para este lote
                worker = OCRWorker(batch)

                # Conectar signals del worker
                worker.progress.connect(
                    lambda p, m: self.progress.emit(p, m)
                )

                # Ejecutar de manera síncrona (esperamos que termine)
                worker.run()

                # Consolidar resultados
                batch_results = worker.results
                self.results['success'].extend(batch_results['success'])
                self.results['failed'].extend(batch_results['failed'])
                self.results['batches_processed'] += 1

                # Emitir progreso de lote
                batch_progress = int(
                    (self.results['batches_processed'] / self.results['total_batches']) * 100
                )
                self.batch_completed.emit(batch_idx + 1, batch_results)

                self.progress.emit(
                    batch_progress,
                    f"Lote {batch_idx+1}/{self.results['total_batches']} completado"
                )

            # Finalizado
            self.finished.emit(self.results)

        except Exception as e:
            self.error.emit(f"Error en procesamiento por lotes: {str(e)}")


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton

    app = QApplication(sys.argv)

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test OCRWorker")
            self.resize(800, 600)

            # Widget central
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)

            # Text edit para logs
            self.log = QTextEdit()
            self.log.setReadOnly(True)
            layout.addWidget(self.log)

            # Botón para iniciar
            btn = QPushButton("Iniciar Procesamiento")
            btn.clicked.connect(self.start_processing)
            layout.addWidget(btn)

            self.worker = None

        def start_processing(self):
            # Archivos de prueba (ajustar rutas)
            files = [
                "test1.pdf",
                "test2.pdf"
            ]

            self.worker = OCRWorker(files)
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
