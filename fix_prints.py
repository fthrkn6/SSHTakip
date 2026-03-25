#!/usr/bin/env python3
"""
Utility script to convert print() calls to logger.info/error/warning
"""
import re
import sys

def convert_prints_to_logger(file_path):
    """Convert print() calls to logger calls"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace print calls with specific keywords
    replacements = [
        # Error/Warning prints
        (r'print\(\s*f?"(\[ERROR\]|\[FAIL\]|\[WARNING\]|\[WARN\])(.+?)"\s*(?:,\s*flush=True)?\)', 
         r'logger.error(f"\\2")'),
        
        # Info/OK/Success prints
        (r'print\(\s*f?"(\[OK\]|\[INFO\]|\[SUCCESS\])(.+?)"\s*(?:,\s*flush=True)?\)', 
         r'logger.info(f"\\2")'),
        
        # Debug/Sync prints
        (r'print\(\s*f?"(\[SYNC|DEBUG|GET-DEBUG])(.+?)"\s*(?:,\s*flush=True)?\)', 
         r'logger.debug(f"\\2")'),
        
        # Generic f-string prints
        (r'print\(\s*f"([^"]*?)"\s*(?:,\s*flush=True)?\)', 
         r'logger.info(f"\\1")'),
        
        # String prints (no f-string)
        (r'print\(\s*"([^"]*?)"\s*(?:,\s*flush=True)?\)', 
         r'logger.info("\\1")'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Converted prints in {file_path}")
        return True
    return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        convert_prints_to_logger(sys.argv[1])
    else:
        # Convert common files
        files = [
            'app.py',
            'seed_perms.py',
            'add_roles.py',
            'routes/reports.py',
            'routes/dashboard.py',
            'routes/fracas.py',
            'routes/kpi.py',
        ]
        for f in files:
            try:
                convert_prints_to_logger(f)
            except Exception as e:
                print(f"✗ Error in {f}: {e}")
