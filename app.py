from flask import Flask, render_template, request, jsonify, abort, g
from config import Config
from utils.diagram_parser import DiagramParser
import os
import re

app = Flask(__name__)
app.config.from_object(Config)

# Initialize diagram parser with debug info
print(f"Loading diagrams from: {app.config['DIAGRAM_FILE']}")
parser = DiagramParser(app.config['DIAGRAM_FILE'])
print(f"Total diagrams loaded: {len(parser.get_all_diagrams())}")

# Custom filter for slugifying strings
def slugify_filter(text):
    """Convert text to URL-friendly slug"""
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

# Register the filter with Jinja2
app.jinja_env.filters['slugify'] = slugify_filter

@app.before_request
def before_request():
    """Load diagrams for use in base template"""
    g.diagrams = parser.get_all_diagrams()
    g.sections = parser.get_all_sections()
    
    # Debug info
    print(f"Request to {request.path} - Loaded {len(g.diagrams)} diagrams")

@app.context_processor
def inject_common_data():
    """Inject common data into all templates"""
    return {
        'app_name': app.config['APP_NAME'],
        'diagrams': g.get('diagrams', []),
        'sections': g.get('sections', [])
    }

@app.route('/')
def index():
    """Home page with list of diagrams"""
    diagrams = parser.get_all_diagrams()
    sections = parser.get_all_sections()
    
    # Get first diagram for preview if available
    preview_diagram = diagrams[0] if diagrams else None
    
    return render_template('index.html', 
                         diagrams=diagrams,
                         sections=sections,
                         preview_diagram=preview_diagram)

@app.route('/diagrams')
def list_diagrams():
    """List all available diagrams"""
    diagrams = parser.get_all_diagrams()
    return render_template('list_diagrams.html', 
                         diagrams=diagrams)

@app.route('/diagram/<int:section_id>')
def show_diagram(section_id):
    """Display a specific diagram by section ID"""
    try:
        diagram = parser.get_diagram_by_id(section_id)
        if not diagram:
            abort(404, description="Diagram not found")
        
        # Get all diagrams for navigation
        all_diagrams = parser.get_all_diagrams()
        
        return render_template('diagram.html',
                             diagram=diagram,
                             diagrams=all_diagrams)
    except Exception as e:
        abort(500, description=str(e))

@app.route('/diagram/section/<int:section_num>')
def show_diagram_by_section(section_num):
    """Display diagram by section number (1-indexed)"""
    try:
        diagram = parser.get_diagram_by_section(section_num)
        if not diagram:
            abort(404, description="Diagram not found")
        
        # Get all diagrams for navigation
        all_diagrams = parser.get_all_diagrams()
        
        return render_template('diagram.html',
                             diagram=diagram,
                             diagrams=all_diagrams)
    except Exception as e:
        abort(500, description=str(e))

@app.route('/api/diagrams')
def api_get_diagrams():
    """API endpoint to get all diagrams"""
    diagrams = parser.get_all_diagrams()
    return jsonify(diagrams)

@app.route('/api/diagram/<int:diagram_id>')
def api_get_diagram(diagram_id):
    """API endpoint to get specific diagram"""
    diagram = parser.get_diagram_by_id(diagram_id)
    if not diagram:
        return jsonify({'error': 'Diagram not found'}), 404
    return jsonify(diagram)

@app.route('/api/search')
def api_search_diagrams():
    """Search diagrams by keyword"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = parser.search_diagrams(query)
    return jsonify(results)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('diagram.html',
                         diagram={
                             'id': 0,
                             'title': '404 - Diagram Not Found',
                             'content': 'graph TD\n    A[Diagram Not Found] --> B[Return to Home]\n    B --> C[Browse Available Diagrams]',
                             'type': 'flowchart',
                             'section': 0
                         },
                         error_message=str(e),
                         diagrams=parser.get_all_diagrams()), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('diagram.html',
                         diagram={
                             'id': 0,
                             'title': '500 - Internal Server Error',
                             'content': 'graph TD\n    A[Server Error] --> B[Try Again]\n    B --> C[Contact Support if Problem Persists]',
                             'type': 'flowchart',
                             'section': 0
                         },
                         error_message=str(e),
                         diagrams=parser.get_all_diagrams()), 500

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=5000)
