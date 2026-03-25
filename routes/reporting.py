"""
Advanced Reporting & Export Routes
Report generation, template management, scheduled exports
"""

from flask import Blueprint, jsonify, render_template, request, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime
from utils_report_manager import template_manager, report_builder, ReportTemplate, ReportTemplateManager
import logging
import io
import os

logger = logging.getLogger(__name__)

bp = Blueprint('reporting', __name__, url_prefix='/api/reports')


@bp.route('/templates', methods=['GET'])
@login_required
def list_templates():
    """
    List all available report templates
    """
    try:
        templates = template_manager.list_templates()
        
        return jsonify({
            'success': True,
            'count': len(templates),
            'templates': [
                {
                    'name': t.name,
                    'title': t.title,
                    'description': t.description,
                    'format': t.format,
                    'orientation': t.orientation,
                    'include_charts': t.include_charts,
                    'email_enabled': t.email_enabled,
                    'schedule': t.schedule_cron
                }
                for t in templates
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"List templates error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/templates/<template_name>', methods=['GET'])
@login_required
def get_template(template_name):
    """
    Get specific report template details
    """
    try:
        template = template_manager.get_template(template_name)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({
            'success': True,
            'template': {
                'name': template.name,
                'title': template.title,
                'description': template.description,
                'modules': template.modules,
                'filters': template.filters,
                'format': template.format,
                'orientation': template.orientation,
                'include_charts': template.include_charts,
                'include_summary': template.include_summary,
                'email_enabled': template.email_enabled,
                'schedule_cron': template.schedule_cron
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Get template error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/generate', methods=['POST'])
@login_required
def generate_report():
    """
    Generate report from template
    
    Request body:
    {
        "template_name": "daily_ops",
        "filters": {
            "date_range": "today",
            "project_code": "belgrad"
        },
        "format": "pdf"
    }
    """
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        filters = data.get('filters', {})
        export_format = data.get('format', 'pdf')
        
        if not template_name:
            return jsonify({'error': 'template_name required'}), 400
        
        # Check user has access
        project_code = filters.get('project_code')
        if project_code and not current_user.can_access_project(project_code):
            return jsonify({'error': 'Unauthorized access to project'}), 403
        
        # Build report
        report = report_builder.build_report(template_name, filters)
        
        # Get data (would fetch from database in real implementation)
        # For now, return report structure
        report['generated_by'] = current_user.username
        report['generated_at'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'success': True,
            'report': report,
            'status': 'generated',
            'ready_for_export': True
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Generate report error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/export', methods=['POST'])
@login_required
def export_report():
    """
    Export report in specified format
    
    Request body:
    {
        "template_name": "daily_ops",
        "format": "pdf",
        "filters": {...}
    }
    """
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        export_format = data.get('format', 'pdf')
        
        if not template_name:
            return jsonify({'error': 'template_name required'}), 400
        
        if export_format not in ['pdf', 'html', 'xlsx', 'json']:
            return jsonify({'error': 'Unsupported format'}), 400
        
        # Generate report
        report = report_builder.build_report(template_name, data.get('filters', {}))
        
        # Export to format
        file_path = report_builder.export_to_format(report, export_format)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Failed to generate export file'}), 500
        
        # Determine MIME type
        mime_types = {
            'pdf': 'application/pdf',
            'html': 'text/html',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json'
        }
        
        return send_file(
            file_path,
            mimetype=mime_types.get(export_format, 'application/octet-stream'),
            as_attachment=True,
            download_name=f"{template_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        )
    
    except Exception as e:
        logger.error(f"Export report error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/schedule', methods=['POST'])
@login_required
def schedule_report():
    """
    Schedule automated report generation
    
    Request body:
    {
        "template_name": "daily_ops",
        "cron_expression": "0 18 * * *",
        "email_recipients": ["admin@example.com"],
        "format": "pdf"
    }
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        cron_expr = data.get('cron_expression')
        recipients = data.get('email_recipients', [])
        
        # This would schedule a Celery task in production
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': f'Report {template_name} scheduled',
            'cron': cron_expr,
            'recipients': recipients,
            'status': 'scheduled'
        }), 201
    
    except Exception as e:
        logger.error(f"Schedule report error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/queue', methods=['GET'])
@login_required
def report_queue():
    """
    Get queued reports and their generation status
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # This would query task queue in production
        return jsonify({
            'success': True,
            'queued_reports': [],
            'in_progress': [],
            'completed': []
        }), 200
    
    except Exception as e:
        logger.error(f"Report queue error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/cache/<report_id>', methods=['GET', 'DELETE'])
@login_required
def cached_report(report_id):
    """
    Get or clear cached report
    """
    try:
        if request.method == 'GET':
            # Retrieve cached report
            cache_key = f'report:{report_id}'
            cached = current_app.cache_manager.get(cache_key)
            
            if not cached:
                return jsonify({'error': 'Report not in cache'}), 404
            
            return jsonify({
                'success': True,
                'report_id': report_id,
                'cached': cached
            }), 200
        
        else:  # DELETE
            # Clear from cache
            cache_key = f'report:{report_id}'
            current_app.cache_manager.delete(cache_key)
            
            return jsonify({
                'success': True,
                'message': 'Report cleared from cache'
            }), 200
    
    except Exception as e:
        logger.error(f"Cached report error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/templates/custom', methods=['POST'])
@login_required
def create_custom_template():
    """
    Create custom report template (admin only)
    
    Request body:
    {
        "name": "custom_report",
        "title": "Custom Report",
        "description": "User-defined report",
        "modules": ["summary", "failures"],
        "format": "pdf"
    }
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        
        template = ReportTemplate(
            name=data.get('name'),
            title=data.get('title'),
            description=data.get('description'),
            modules=data.get('modules', []),
            filters=data.get('filters', {}),
            format=data.get('format', 'pdf'),
            orientation=data.get('orientation', 'portrait'),
            include_charts=data.get('include_charts', True),
            email_enabled=data.get('email_enabled', False)
        )
        
        success = template_manager.create_custom_template(template)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Template {template.name} created',
                'template': {
                    'name': template.name,
                    'title': template.title
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create template'}), 500
    
    except Exception as e:
        logger.error(f"Create custom template error: {e}")
        return jsonify({'error': str(e)}), 500
