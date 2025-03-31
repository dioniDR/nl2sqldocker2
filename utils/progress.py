#!/usr/bin/env python3
"""
progress.py - Indicadores de progreso visual

PROPÓSITO:
    Proporciona indicadores visuales del progreso del sistema,
    incluyendo barras de progreso, temporizadores y mensajes de estado.

ENTRADA:
    - Nombre de la fase actual
    - Valores de progreso (0-100)
    - Mensajes descriptivos

SALIDA:
    - Indicadores visuales en consola
    - Información de tiempo transcurrido

ERRORES:
    - InvalidPhaseError: Fase no reconocida
    - ProgressValueError: Valor de progreso fuera de rango

DEPENDENCIAS:
    - tqdm: Para barras de progreso
    - time: Para temporizadores
    - core.config: Para configuración de visibilidad
"""

import sys
import time
from enum import Enum
from typing import Optional, List, Dict, Any
from tqdm import tqdm
from colorama import init, Fore, Style

# Manejar importación condicional para evitar problemas de importación circular
try:
    from core.config import Config, SHOW_PROGRESS
except ImportError:
    # Configuración predeterminada para pruebas locales
    class Config:
        pass

    SHOW_PROGRESS = True  # Mostrar progreso por defecto si no se encuentra la configuración

# Inicializar colorama para soporte de colores en Windows
init()

class PhaseStatus(Enum):
    """Estados posibles para una fase."""
    PENDING = "⏳"
    RUNNING = "🔄"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"

class Phase:
    """Representa una fase del sistema con su nombre y progreso."""
    
    def __init__(self, name: str, description: str, weight: int = 1):
        """
        Inicializa una fase del sistema.
        
        Args:
            name: Identificador único de la fase
            description: Descripción legible para humanos
            weight: Peso relativo de la fase (para progreso global)
        """
        self.name = name
        self.description = description
        self.weight = weight
        self.status = PhaseStatus.PENDING
        self.progress = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.message = ""
        self._progress_bar = None
    
    @property
    def elapsed_time(self) -> Optional[float]:
        """Tiempo transcurrido en segundos o None si no ha iniciado."""
        if self.start_time is None:
            return None
            
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time
    
    @property
    def is_completed(self) -> bool:
        """Indica si la fase ha sido completada (éxito o error)."""
        return self.status in (PhaseStatus.SUCCESS, PhaseStatus.ERROR)
    
    def format_time(self) -> str:
        """Formatea el tiempo transcurrido para mostrar."""
        elapsed = self.elapsed_time
        
        if elapsed is None:
            return "--:--"
            
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        return f"{minutes:02d}:{seconds:02d}"
    
    def __str__(self) -> str:
        """Representación en texto de la fase."""
        status_str = self.status.value
        time_str = f"⏱️ ({self.format_time()})" if self.elapsed_time is not None else ""
        
        return f"[{status_str}] {self.name} {time_str}: {self.progress}%"

class ProgressTracker:
    """Gestiona el seguimiento del progreso de todas las fases del sistema."""
    
    # Fases predefinidas del sistema
    PHASES = {
        "setup": Phase("FASE 1: VALIDACIÓN", "Verificando configuración...", 1),
        "db_connection": Phase("FASE 2: CONEXIÓN BD", "Conectando a base de datos...", 2),
        "schema_analysis": Phase("FASE 3: ANÁLISIS ESQUEMA", "Analizando estructura de base de datos...", 3),
        "ai_provider": Phase("FASE 4: VERIFICACIÓN IA", "Comprobando proveedores de IA...", 2),
        "system_start": Phase("FASE 5: INICIO SISTEMA", "Preparando interfaz...", 1)
    }
    
    def __init__(self):
        """Inicializa el seguimiento de progreso."""
        # Copiar las fases predefinidas para no modificar la clase
        self.phases = {k: Phase(v.name, v.description, v.weight) for k, v in self.PHASES.items()}
        self.current_phase_key: Optional[str] = None
        self.global_start_time: Optional[float] = None
        self._last_status_lines = 0
    
    def start_phase(self, phase_key: str, message: Optional[str] = None) -> None:
        """
        Inicia una fase del sistema.
        
        Args:
            phase_key: Clave de la fase a iniciar
            message: Mensaje opcional de inicio
        """
        if not SHOW_PROGRESS:
            return
            
        if phase_key not in self.phases:
            raise ValueError(f"Fase no reconocida: {phase_key}")
        
        # Si es la primera fase, registrar tiempo global
        if self.global_start_time is None:
            self.global_start_time = time.time()
        
        phase = self.phases[phase_key]
        phase.start_time = time.time()
        phase.status = PhaseStatus.RUNNING
        phase.progress = 0
        
        if message:
            phase.message = message
        
        self.current_phase_key = phase_key
        self._update_display()
    
    def update_progress(self, progress: float, message: Optional[str] = None) -> None:
        """
        Actualiza el progreso de la fase actual.
        
        Args:
            progress: Valor de progreso (0-100)
            message: Mensaje opcional de progreso
        """
        if not SHOW_PROGRESS or self.current_phase_key is None:
            return
            
        if not 0 <= progress <= 100:
            progress = max(0, min(100, progress))
        
        phase = self.phases[self.current_phase_key]
        phase.progress = progress
        
        if message:
            phase.message = message
        
        self._update_display()
    
    def complete_phase(self, 
                      success: bool = True, 
                      message: Optional[str] = None,
                      status: Optional[PhaseStatus] = None) -> None:
        """
        Completa la fase actual.
        
        Args:
            success: True si la fase fue exitosa, False si hubo error
            message: Mensaje opcional de finalización
            status: Estado explícito (anula success si proporcionado)
        """
        if not SHOW_PROGRESS or self.current_phase_key is None:
            return
            
        phase = self.phases[self.current_phase_key]
        phase.progress = 100
        phase.end_time = time.time()
        
        if status is not None:
            phase.status = status
        else:
            phase.status = PhaseStatus.SUCCESS if success else PhaseStatus.ERROR
        
        if message:
            phase.message = message
        
        self._update_display(force_full=True)
        print()  # Línea adicional después de completar una fase
    
    def _update_display(self, force_full: bool = False) -> None:
        """
        Actualiza la visualización en consola.
        
        Args:
            force_full: Si es True, muestra todas las fases
        """
        if not SHOW_PROGRESS:
            return
        
        # Limpiar líneas anteriores
        if self._last_status_lines > 0:
            sys.stdout.write(f"\033[{self._last_status_lines}A")  # Subir N líneas
            sys.stdout.write("\033[J")  # Limpiar hasta el final de la pantalla
        
        lines_count = 0
        
        # Mostrar fases completadas y actual
        shown_phases = []
        for key, phase in self.phases.items():
            if force_full or key == self.current_phase_key or phase.is_completed:
                shown_phases.append(key)
        
        for key in shown_phases:
            phase = self.phases[key]
            
            # Colorear según el estado
            color = Fore.RESET
            if phase.status == PhaseStatus.SUCCESS:
                color = Fore.GREEN
            elif phase.status == PhaseStatus.ERROR:
                color = Fore.RED
            elif phase.status == PhaseStatus.WARNING:
                color = Fore.YELLOW
            elif phase.status == PhaseStatus.RUNNING:
                color = Fore.CYAN
            
            # Mostrar encabezado de la fase
            print(f"{color}{phase.name}{Style.RESET_ALL} ⏱️ ({phase.format_time()})")
            lines_count += 1
            
            # Mostrar mensaje descriptivo
            message = phase.description if not phase.message else phase.message
            print(f"{message}")
            lines_count += 1
            
            # Mostrar barra de progreso si la fase está en curso
            progress_char = "■"
            empty_char = "□"
            bar_width = 50
            
            filled = int(phase.progress / 100 * bar_width)
            bar = progress_char * filled + empty_char * (bar_width - filled)
            
            print(f"[{bar}] {phase.progress}%")
            lines_count += 1
            
            # Si la fase está completa, mostrar estado final
            if phase.is_completed:
                status_text = "ÉXITO" if phase.status == PhaseStatus.SUCCESS else "ERROR"
                print(f"{color}{phase.status.value} {status_text}: {phase.message}{Style.RESET_ALL}")
                lines_count += 1
            
            # Separador entre fases
            print()
            lines_count += 1
        
        # Registrar cuántas líneas hemos mostrado
        self._last_status_lines = lines_count
        
        # Forzar actualización inmediata
        sys.stdout.flush()
    
    def get_elapsed_time(self) -> Optional[float]:
        """
        Obtiene el tiempo total transcurrido.
        
        Returns:
            Tiempo total en segundos o None si no se ha iniciado
        """
        if self.global_start_time is None:
            return None
            
        return time.time() - self.global_start_time
    
    def get_formatted_summary(self) -> str:
        """
        Genera un resumen del progreso de todas las fases.
        
        Returns:
            Texto con el resumen formateado
        """
        if self.global_start_time is None:
            return "No se ha iniciado ninguna fase."
            
        total_time = self.get_elapsed_time()
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        summary = f"Resumen de ejecución (Tiempo total: {minutes:02d}:{seconds:02d})\n\n"
        
        # Analizar estados
        completed = sum(1 for p in self.phases.values() if p.is_completed)
        successful = sum(1 for p in self.phases.values() if p.status == PhaseStatus.SUCCESS)
        errors = sum(1 for p in self.phases.values() if p.status == PhaseStatus.ERROR)
        
        summary += f"Fases completadas: {completed}/{len(self.phases)}\n"
        summary += f"Exitosas: {successful}\n"
        summary += f"Con errores: {errors}\n\n"
        
        # Detalles por fase
        for key, phase in self.phases.items():
            status = phase.status.value
            if phase.elapsed_time is not None:
                time_str = phase.format_time()
                summary += f"{status} {phase.name}: {time_str}\n"
            else:
                summary += f"{status} {phase.name}: No iniciada\n"
        
        return summary

# Instancia global para uso en todo el proyecto
tracker = ProgressTracker()

# Funciones de conveniencia para usar en otros módulos
def start_phase(phase_key: str, message: Optional[str] = None) -> None:
    """Inicia una fase del sistema."""
    tracker.start_phase(phase_key, message)

def update_progress(progress: float, message: Optional[str] = None) -> None:
    """Actualiza el progreso de la fase actual."""
    tracker.update_progress(progress, message)

def complete_phase(success: bool = True, message: Optional[str] = None) -> None:
    """Completa la fase actual."""
    tracker.complete_phase(success, message)

def show_error(message: str) -> None:
    """Muestra un mensaje de error con formato apropiado."""
    if SHOW_PROGRESS:
        print(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")

def show_warning(message: str) -> None:
    """Muestra un mensaje de advertencia con formato apropiado."""
    if SHOW_PROGRESS:
        print(f"{Fore.YELLOW}[ADVERTENCIA] {message}{Style.RESET_ALL}")

def show_success(message: str) -> None:
    """Muestra un mensaje de éxito con formato apropiado."""
    if SHOW_PROGRESS:
        print(f"{Fore.GREEN}[ÉXITO] {message}{Style.RESET_ALL}")

def show_info(message: str) -> None:
    """Muestra un mensaje informativo con formato apropiado."""
    if SHOW_PROGRESS:
        print(f"{Fore.CYAN}[INFO] {message}{Style.RESET_ALL}")

# Ejemplo de uso cuando se ejecuta directamente
if __name__ == "__main__":
    print("Demostración de indicadores de progreso\n")
    
    # Ejemplo de uso con seguimiento de fases
    start_phase("setup", "Verificando configuración inicial")
    
    for i in range(10):
        update_progress(i * 10, f"Paso {i+1} de 10")
        time.sleep(0.2)
    
    complete_phase(True, "Configuración validada correctamente")
    
    start_phase("db_connection", "Conectando a MariaDB")
    
    for i in range(20):
        update_progress(i * 5, f"Intentando conexión {i+1}")
        time.sleep(0.1)
    
    complete_phase(True, "Conexión establecida correctamente")
    
    start_phase("schema_analysis")
    
    for i in range(10):
        update_progress(i * 10, f"Analizando tabla {i+1} de 10")
        time.sleep(0.3)
    
    complete_phase(True, "Esquema analizado: 10 tablas, 50 columnas")
    
    print("\nResumen final:\n")
    print(tracker.get_formatted_summary())
    
    # Ejemplos de mensajes formatados
    print("\nEjemplos de mensajes formatados:")
    show_info("Este es un mensaje informativo")
    show_success("Esta operación se completó correctamente")
    show_warning("Esta operación podría tener problemas")
    show_error("Esta operación falló por alguna razón")
