import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.diagram_parser import DiagramParser

print("=" * 60)
print("TESTING MERMAID PARSER")
print("=" * 60)

# Test with original file
print("\n1. Testing with original file:")
parser1 = DiagramParser('static/data/mermaid_ref.txt')
print(f"   Diagrams found: {len(parser1.diagrams)}")
print(f"   Sections found: {len(parser1.sections)}")

# Test with clean file (if it exists)
clean_file = 'static/data/mermaid_clean.txt'
if os.path.exists(clean_file):
    print("\n2. Testing with clean file:")
    parser2 = DiagramParser(clean_file)
    print(f"   Diagrams found: {len(parser2.diagrams)}")
    print(f"   Sections found: {len(parser2.sections)}")

print("\n" + "=" * 60)
print("DIAGRAM DETAILS:")
print("=" * 60)

if parser1.diagrams:
    for i, diagram in enumerate(parser1.diagrams[:5], 1):
        print(f"\n{i}. {diagram['title']} (Section {diagram['section']})")
        print(f"   Type: {diagram['type']}")
        print(f"   Content length: {len(diagram['content'])} chars")
        print(f"   First 50 chars: {diagram['content'][:50]}...")
else:
    print("No diagrams parsed from original file")

print("\n" + "=" * 60)
print("RAW FILE ANALYSIS:")
print("=" * 60)

# Read and analyze the file
with open('static/data/mermaid_ref.txt', 'r') as f:
    content = f.read()

# Count sections by looking for "X. " pattern
import re
section_matches = re.findall(r'\n(\d+)\.\s+', content)
print(f"\nFound {len(section_matches)} section headers in file:")
for i, match in enumerate(set(section_matches), 1):
    print(f"  {i}. Section {match}")

# Show first few lines
print(f"\nFirst 200 characters of file:")
print(content[:200])
