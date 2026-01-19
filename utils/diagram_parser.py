import re
from typing import List, Dict, Optional

class DiagramParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sections = []
        self.diagrams = []
        self.load_file()
    
    def load_file(self):
        """Load and parse the mermaid reference file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"File loaded. Content length: {len(content)} characters")
            
            # If file is empty, use sample data
            if not content.strip():
                print("File is empty, loading sample data")
                self.load_sample_data()
                return
            
            # NEW APPROACH: Find sections by looking for numbered headings followed by newline
            # Pattern to find "X. Title" where X is a number
            section_pattern = r'(\n|^)(\d+)\.\s+(.+?)\n\n'
            matches = list(re.finditer(section_pattern, content, re.DOTALL))
            
            print(f"Found {len(matches)} sections using pattern matching")
            
            if not matches:
                # Try alternative pattern
                section_pattern = r'^(\d+)\.\s+(.+?)$'
                matches = list(re.finditer(section_pattern, content, re.MULTILINE))
                print(f"Found {len(matches)} sections using alternative pattern")
            
            for i, match in enumerate(matches):
                section_num = int(match.group(2))
                title = match.group(3).strip()
                
                # Find the content for this section (until next section or end of file)
                start_pos = match.end()
                if i + 1 < len(matches):
                    end_pos = matches[i + 1].start()
                else:
                    end_pos = len(content)
                
                section_content = content[start_pos:end_pos].strip()
                
                if section_content:
                    # Extract diagram content (skip any blank lines at start)
                    lines = section_content.split('\n')
                    diagram_lines = []
                    
                    for line in lines:
                        line = line.strip()
                        if line:  # Skip empty lines
                            diagram_lines.append(line)
                    
                    diagram_content = '\n'.join(diagram_lines)
                    
                    if diagram_content:
                        diagram_type = self.detect_diagram_type(diagram_content)
                        
                        diagram_data = {
                            'id': len(self.diagrams) + 1,
                            'title': title,
                            'content': diagram_content,
                            'type': diagram_type,
                            'section': section_num
                        }
                        
                        self.diagrams.append(diagram_data)
                        
                        self.sections.append({
                            'number': section_num,
                            'title': title,
                            'content_preview': diagram_content[:100] + '...' if len(diagram_content) > 100 else diagram_content
                        })
                        
                        print(f"Parsed diagram {section_num}: {title} ({diagram_type})")
            
            print(f"Successfully parsed {len(self.diagrams)} diagrams")
            
            # If no diagrams were parsed, try a simpler approach
            if len(self.diagrams) == 0:
                print("Trying simpler parsing approach...")
                self.simple_parse(content)
            
            # If still no diagrams, load sample data
            if len(self.diagrams) == 0:
                print("No diagrams found in file, loading sample data")
                self.load_sample_data()
                
        except FileNotFoundError:
            print(f"Warning: File {self.file_path} not found. Using sample data.")
            self.load_sample_data()
        except Exception as e:
            print(f"Error parsing file: {e}")
            import traceback
            traceback.print_exc()
            self.load_sample_data()
    
    def simple_parse(self, content: str):
        """Simpler parsing approach for problematic files"""
        # Split by double newlines to get sections
        sections = content.strip().split('\n\n')
        
        print(f"Simple parse: Found {len(sections)} potential sections")
        
        current_section = None
        current_title = None
        current_content = []
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if this section starts with a number and dot (e.g., "1. Title")
            if re.match(r'^\d+\.\s+', section):
                # Save previous section if exists
                if current_section is not None and current_content:
                    diagram_content = '\n'.join(current_content)
                    if diagram_content.strip():
                        diagram_type = self.detect_diagram_type(diagram_content)
                        
                        diagram_data = {
                            'id': len(self.diagrams) + 1,
                            'title': current_title,
                            'content': diagram_content,
                            'type': diagram_type,
                            'section': current_section
                        }
                        
                        self.diagrams.append(diagram_data)
                        
                        self.sections.append({
                            'number': current_section,
                            'title': current_title,
                            'content_preview': diagram_content[:100] + '...' if len(diagram_content) > 100 else diagram_content
                        })
                
                # Start new section
                match = re.match(r'^(\d+)\.\s+(.+)$', section, re.DOTALL)
                if match:
                    current_section = int(match.group(1))
                    current_title = match.group(2).strip()
                    current_content = []
                else:
                    # Try to extract title from first line
                    lines = section.split('\n')
                    if lines:
                        first_line = lines[0]
                        match = re.match(r'^(\d+)\.\s+(.+)$', first_line)
                        if match:
                            current_section = int(match.group(1))
                            current_title = match.group(2).strip()
                            current_content = lines[1:] if len(lines) > 1 else []
            elif current_section is not None:
                # This is part of the current section
                current_content.append(section)
        
        # Don't forget the last section
        if current_section is not None and current_content:
            diagram_content = '\n'.join(current_content)
            if diagram_content.strip():
                diagram_type = self.detect_diagram_type(diagram_content)
                
                diagram_data = {
                    'id': len(self.diagrams) + 1,
                    'title': current_title,
                    'content': diagram_content,
                    'type': diagram_type,
                    'section': current_section
                }
                
                self.diagrams.append(diagram_data)
                
                self.sections.append({
                    'number': current_section,
                    'title': current_title,
                    'content_preview': diagram_content[:100] + '...' if len(diagram_content) > 100 else diagram_content
                })
        
        print(f"Simple parse successfully extracted {len(self.diagrams)} diagrams")
    
    def detect_diagram_type(self, content: str) -> str:
        """Detect the type of diagram"""
        content = content.strip()
        
        if content.startswith('graph'):
            return 'graph'
        elif content.startswith('flowchart'):
            return 'flowchart'
        elif content.startswith('sequenceDiagram'):
            return 'sequence'
        elif content.startswith('erDiagram'):
            return 'er'
        elif content.startswith('stateDiagram'):
            return 'state'
        elif content.startswith('classDiagram'):
            return 'class'
        elif content.startswith('gantt'):
            return 'gantt'
        elif content.startswith('pie'):
            return 'pie'
        else:
            # Try to detect from content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('graph'):
                    return 'graph'
                elif line.startswith('flowchart'):
                    return 'flowchart'
                elif line.startswith('sequenceDiagram'):
                    return 'sequence'
                elif line.startswith('erDiagram'):
                    return 'er'
                elif line.startswith('stateDiagram'):
                    return 'state'
            return 'unknown'
    
    def load_sample_data(self):
        """Load sample data if file not found or empty"""
        sample_diagrams = [
            {
                'id': 1,
                'title': 'System Architecture Diagram',
                'content': 'graph TB\n    subgraph "Client Layer"\n        A[Web Browser]\n        B[Mobile Browser]\n    end\n    \n    subgraph "Flask Application Layer"\n        C[Flask App]\n        D[Authentication Module]\n        E[API Endpoints]\n        F[Report Generation]\n        G[QR Code Service]\n    end\n    \n    subgraph "Database Layer"\n        H[(PostgreSQL)]\n        I[Users Table]\n        J[Learners Table]\n        K[Attendance Table]\n    end\n    \n    subgraph "External Services"\n        L[Azure Blob Storage - QR Codes]\n        M[PDF Generation - ReportLab]\n    end\n    \n    A --> C\n    B --> C\n    C --> D\n    C --> E\n    C --> F\n    C --> G\n    D --> H\n    E --> H\n    G --> L\n    F --> M\n    H --> I\n    H --> J\n    H --> K\n    \n    style A fill:#e1f5fe\n    style B fill:#e1f5fe\n    style C fill:#f3e5f5\n    style D fill:#fce4ec\n    style E fill:#e8f5e8\n    style F fill:#fff3e0\n    style G fill:#e0f2f1',
                'type': 'graph',
                'section': 1
            },
            {
                'id': 2,
                'title': 'Database Schema Diagram',
                'content': 'erDiagram\n    User ||--o{ Attendance : manages\n    User {\n        int id PK\n        string username UK\n        string email UK\n        string password_hash\n    }\n    \n    Learner ||--o{ Attendance : has\n    Learner {\n        int id PK\n        string student_id UK\n        string first_name\n        string last_name\n        string email\n        string phone\n        string course\n        string pin_hash\n        datetime created_at\n        string qr_code_path\n    }\n    \n    Attendance {\n        int id PK\n        int learner_id FK\n        datetime timestamp\n        string status\n        text notes\n    }\n    \n    QRCodeGenerator ||..|| Learner : generates_for\n    QRCodeGenerator {\n        -- Static Class --\n        generate_qr_code()\n        upload_to_azure()\n        save_locally()\n    }',
                'type': 'er',
                'section': 2
            },
            {
                'id': 3,
                'title': 'Authentication & Session Flow Diagram',
                'content': 'sequenceDiagram\n    participant User as User\n    participant Flask as Flask App\n    participant DB as Database\n    participant Session as Session Manager\n    \n    User->>Flask: GET /login\n    Flask-->>User: Render Login Form\n    \n    User->>Flask: POST /login (credentials)\n    Flask->>DB: Query User Table\n    DB-->>Flask: User Data\n    \n    alt Valid Credentials\n        Flask->>Session: Create Session\n        Flask->>User: Redirect to /dashboard\n        User->>Flask: Access Protected Route\n        Flask->>Session: Verify Session\n        Session-->>Flask: Session Valid\n        Flask-->>User: Render Protected Content\n    else Invalid Credentials\n        Flask-->>User: Show Error Message\n    end\n    \n    User->>Flask: GET /logout\n    Flask->>Session: Destroy Session\n    Flask-->>User: Redirect to Login',
                'type': 'sequence',
                'section': 3
            },
            {
                'id': 4,
                'title': 'Attendance Marking Flow Diagram',
                'content': 'flowchart TD\n    Start([Start]) --> Access[Access Attendance URL]\n    Access --> PINCheck{PIN Verified?}\n    \n    PINCheck -- No --> PINPage[Redirect to PIN Validation]\n    PINPage --> PINEntry[Enter PIN]\n    PINEntry --> Verify[Verify PIN via API]\n    Verify --> CheckPIN{PIN Valid?}\n    \n    CheckPIN -- Yes --> Verified[Set Verified Flag]\n    CheckPIN -- No --> PINError[Show PIN Error]\n    PINError --> PINEntry\n    \n    PINCheck -- Yes --> Lookup[Lookup Student]\n    Lookup --> CheckExist{Student Exists?}\n    \n    CheckExist -- No --> NotFound[Show Student Not Found]\n    CheckExist -- Yes --> CheckToday{Attendance Today?}\n    \n    CheckToday -- Yes --> Update[Update Status]\n    Update --> Record[Record Updated]\n    \n    CheckToday -- No --> Create[Create New Record]\n    Create --> Record\n    \n    Record --> Display[Show Attendance Result]\n    Display --> End([End])\n    \n    NotFound --> End',
                'type': 'flowchart',
                'section': 4
            },
            {
                'id': 5,
                'title': 'API Endpoints Structure Diagram',
                'content': 'graph TB\n    subgraph "Authentication"\n        A1[GET /login]\n        A2[POST /login]\n        A3[GET /logout]\n    end\n    \n    subgraph "Protected Routes"\n        B1[GET / - Dashboard]\n        B2[GET /learners]\n        B3[GET /reports]\n        B4[GET /admin/system-status]\n    end\n    \n    subgraph "API Endpoints"\n        C1[GET /api/learners]\n        C2[GET /api/attendance]\n        C3[GET /api/analytics]\n        C4[POST /api/generate-report]\n        C5[POST /api/verify-pin]\n        C6[POST /api/set-pin/]\n        C7[GET /api/health]\n    end\n    \n    subgraph "Mobile Routes"\n        D1[GET /mobile/student-list]\n        D2[GET /mobile/attendance/]\n        D3[GET /mobile/absence/]\n        D4[GET /pin-validation/]\n    end\n    \n    subgraph "Public Routes"\n        E1[GET /public/student-cards]\n    end\n    \n    subgraph "Admin Routes"\n        F1[POST /api/bulk-set-pins]\n        F2[POST /api/reset-all-pins]\n        F3[GET /init-db]\n    end\n    \n    A1 & A2 --> B1\n    B1 --> C1 & C2 & C3\n    B2 --> D1\n    B3 --> C4\n    B4 --> C7\n    D1 --> D2 & D3\n    D2 & D3 --> D4\n    D4 --> C5',
                'type': 'graph',
                'section': 5
            }
        ]
        
        self.diagrams = sample_diagrams
        self.sections = []
        for diagram in sample_diagrams:
            self.sections.append({
                'number': diagram['section'],
                'title': diagram['title'],
                'content_preview': diagram['content'][:100] + '...' if len(diagram['content']) > 100 else diagram['content']
            })
        
        print("Loaded sample data with 5 diagrams")
    
    def get_all_diagrams(self) -> List[Dict]:
        """Get all diagrams"""
        return self.diagrams
    
    def get_diagram_by_id(self, diagram_id: int) -> Optional[Dict]:
        """Get diagram by ID"""
        for diagram in self.diagrams:
            if diagram['id'] == diagram_id:
                return diagram
        return None
    
    def get_diagram_by_section(self, section_num: int) -> Optional[Dict]:
        """Get diagram by section number"""
        for diagram in self.diagrams:
            if diagram['section'] == section_num:
                return diagram
        return None
    
    def get_all_sections(self) -> List[Dict]:
        """Get all sections"""
        return self.sections
    
    def search_diagrams(self, query: str) -> List[Dict]:
        """Search diagrams by title or content"""
        query = query.lower()
        results = []
        
        for diagram in self.diagrams:
            if (query in diagram['title'].lower() or 
                query in diagram['content'].lower()):
                results.append(diagram)
        
        return results
