"""
UI/Frontend Configuration and Utilities
Bootstrap 5 + Dark Mode + Form Validation
"""

from flask import Flask
from typing import Dict, List

class UIConfig:
    """Frontend configuration"""
    
    # Bootstrap 5
    BOOTSTRAP_VERSION = '5.3.0'
    BOOTSWATCH_THEME = 'cosmo'  # Modern theme
    
    # Color Scheme
    COLORS = {
        'primary': '#007bff',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }
    
    # Status Colors (Equipment)
    STATUS_COLORS = {
        'operational': '#00B050',      # Green
        'maintenance': '#FFC000',      # Orange
        'down': '#FF0000',             # Red
        'offline': '#808080'          # Gray
    }
    
    # Chart Colors
    CHART_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]


# Dark Mode Toggle (JS to be included in templates)
DARK_MODE_SCRIPT = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;
    
    // Load preference
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        htmlElement.setAttribute('data-bs-theme', 'dark');
        if (darkModeToggle) darkModeToggle.checked = true;
    }
    
    // Toggle handler
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            const isDark = this.checked;
            localStorage.setItem('darkMode', isDark);
            htmlElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
        });
    }
});
</script>
"""

# Custom CSS for Dark Mode & Enhancements
CUSTOM_CSS = """
/* Dark Mode Variables */
:root[data-bs-theme="dark"] {
    --bs-body-bg: #1a1a1a;
    --bs-body-color: #e9ecef;
    --bs-border-color: #495057;
}

/* Equipment Status Badges */
.badge-operational {
    background-color: #00B050;
    color: white;
}

.badge-maintenance {
    background-color: #FFC000;
    color: black;
}

.badge-down {
    background-color: #FF0000;
    color: white;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}

.kpi-card .kpi-value {
    font-size: 2.5rem;
    font-weight: bold;
}

.kpi-card .kpi-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Smooth Transitions */
* {
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* Status Indicator Pulse */
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 5px;
}

.status-indicator.operational {
    background-color: #00B050;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(0, 176, 80, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(0, 176, 80, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(0, 176, 80, 0);
    }
}

/* Responsive Tables */
@media (max-width: 768px) {
    table {
        font-size: 0.85rem;
    }
    
    .table thead {
        display: none;
    }
    
    .table, .table tbody, .table tr, .table td {
        display: block;
    }
    
    .table tr {
        margin-bottom: 15px;
        border: 1px solid #ddd;
    }
    
    .table td {
        text-align: right;
        padding-left: 50%;
        position: relative;
    }
    
    .table td::before {
        content: attr(data-label);
        position: absolute;
        left: 6px;
        font-weight: bold;
        text-align: left;
    }
}
"""
