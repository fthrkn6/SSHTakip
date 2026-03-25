"""
DEPRECATED: This module is kept for backward compatibility only.
Use utils_service_status_consolidated.py instead.

This module re-exports from the consolidated logger for backward compatibility.
"""

# Import and re-export consolidated logger
from utils_service_status_consolidated import ServiceStatusLogger, log_service_status

__all__ = ['ServiceStatusLogger', 'log_service_status']
