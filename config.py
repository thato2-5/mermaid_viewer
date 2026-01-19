import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MESSAGE = "Mermaid Diagram Viewer"
    
    # Diagram configuration
    DIAGRAM_FILE = 'static/data/mermaid_ref.txt'
    DIAGRAM_TYPES = ['architecture', 'schema', 'flow', 'sequence', 'erDiagram', 'stateDiagram']
    
    # App settings
    APP_NAME = "Mermaid Diagram Viewer"
    DEBUG = True
