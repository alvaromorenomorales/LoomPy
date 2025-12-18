"""Progress tracking and visualization for translation tasks."""

import sys
import time
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class TaskProgress:
    """Represents progress state for a single task."""
    task_name: str
    total_items: int
    processed_items: int = 0
    start_time: float = 0.0
    estimated_speed: Optional[float] = None  # items per second
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.processed_items / self.total_items) * 100.0
    
    @property
    def eta_seconds(self) -> Optional[float]:
        """Calculate estimated time remaining in seconds."""
        if not self.estimated_speed or self.estimated_speed == 0:
            return None
        
        remaining_items = self.total_items - self.processed_items
        return remaining_items / self.estimated_speed
    
    def format_eta(self) -> str:
        """Format ETA as human-readable string."""
        eta = self.eta_seconds
        if eta is None:
            return "calculando..."
        
        if eta < 60:
            return f"{int(eta)}s"
        elif eta < 3600:
            minutes = int(eta / 60)
            seconds = int(eta % 60)
            return f"{minutes:02d}:{seconds:02d}"
        else:
            hours = int(eta / 3600)
            minutes = int((eta % 3600) / 60)
            return f"{hours}h {minutes:02d}m"


class ProgressBar:
    """
    Visual progress bar with task tracking and time estimation.
    
    Features:
    - Dynamic percentage calculation
    - Time estimation based on processing speed
    - Task change notifications
    - Smooth progress updates
    """
    
    def __init__(self, bar_width: int = 40, enable_colors: bool = True):
        """
        Initialize progress bar.
        
        Args:
            bar_width: Width of the progress bar in characters
            enable_colors: Whether to use ANSI color codes
        """
        self.bar_width = bar_width
        self.enable_colors = enable_colors
        self.current_task: Optional[TaskProgress] = None
        self.last_update_time = 0.0
        self.min_update_interval = 0.1  # Minimum seconds between updates
        
        # ANSI color codes
        self.colors = {
            'green': '\033[92m',
            'blue': '\033[94m',
            'yellow': '\033[93m',
            'cyan': '\033[96m',
            'reset': '\033[0m',
            'bold': '\033[1m',
        } if enable_colors else {k: '' for k in ['green', 'blue', 'yellow', 'cyan', 'reset', 'bold']}
    
    def start_task(self, task_name: str, total_items: int):
        """
        Start tracking a new task.
        
        Args:
            task_name: Name of the task (e.g., "Traduciendo a inglés")
            total_items: Total number of items to process
        """
        self.current_task = TaskProgress(
            task_name=task_name,
            total_items=total_items,
            start_time=time.time()
        )
        
        # Print task change notification
        print(f"\n{self.colors['bold']}{self.colors['cyan']}▶ {task_name}{self.colors['reset']}")
        print(f"  Total de elementos: {total_items}")
        self._render()
    
    def update(self, processed_items: int, force: bool = False):
        """
        Update progress.
        
        Args:
            processed_items: Number of items processed so far
            force: Force update even if min interval hasn't passed
        """
        if not self.current_task:
            return
        
        # Throttle updates to avoid flickering
        current_time = time.time()
        if not force and (current_time - self.last_update_time) < self.min_update_interval:
            return
        
        self.current_task.processed_items = processed_items
        
        # Calculate speed after processing some items
        if processed_items >= 10 and self.current_task.estimated_speed is None:
            elapsed = current_time - self.current_task.start_time
            self.current_task.estimated_speed = processed_items / elapsed
        
        self.last_update_time = current_time
        self._render()
    
    def complete(self):
        """Mark current task as complete."""
        if not self.current_task:
            return
        
        self.current_task.processed_items = self.current_task.total_items
        self._render(final=True)
        
        # Print completion message
        elapsed = time.time() - self.current_task.start_time
        print(f"\n{self.colors['green']}✓ Completado en {self._format_time(elapsed)}{self.colors['reset']}\n")
        
        self.current_task = None
    
    def _render(self, final: bool = False):
        """Render the progress bar."""
        if not self.current_task:
            return
        
        task = self.current_task
        percentage = task.percentage
        
        # Calculate filled portion of bar
        filled_width = int(self.bar_width * percentage / 100)
        empty_width = self.bar_width - filled_width
        
        # Build progress bar
        bar = f"{self.colors['green']}{'█' * filled_width}{self.colors['reset']}"
        bar += f"{self.colors['blue']}{'░' * empty_width}{self.colors['reset']}"
        
        # Build info string
        info = f"{task.processed_items}/{task.total_items} elementos"
        
        # Add ETA if available and not final
        if not final and task.eta_seconds is not None:
            info += f" | ETA: {task.format_eta()}"
        
        # Print progress line (overwrite previous line)
        percentage_str = f"{percentage:5.1f}%"
        line = f"\r  [{bar}] {self.colors['yellow']}{percentage_str}{self.colors['reset']} | {info}"
        
        # Clear to end of line and print
        sys.stdout.write(line + ' ' * 10)
        sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Format elapsed time as human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"


def create_progress_callback(progress_bar: ProgressBar) -> Callable[[int], None]:
    """
    Create a progress callback function for use in translation pipeline.
    
    Args:
        progress_bar: ProgressBar instance to update
        
    Returns:
        Callback function that accepts processed item count
    """
    def callback(processed_items: int):
        progress_bar.update(processed_items)
    
    return callback
