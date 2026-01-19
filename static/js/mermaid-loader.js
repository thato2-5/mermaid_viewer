/**
 * Mermaid Diagram Loader
 * Handles dynamic loading and rendering of Mermaid diagrams
 */

class MermaidLoader {
    constructor() {
        this.initialized = false;
        this.diagrams = [];
        this.currentTheme = 'default';
        this.zoomLevel = 1;
    }

    initialize() {
        if (typeof mermaid === 'undefined') {
            console.error('Mermaid.js not loaded');
            return false;
        }

        try {
            mermaid.initialize({
                startOnLoad: true,
                theme: this.currentTheme,
                securityLevel: 'loose',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                },
                sequence: {
                    useMaxWidth: true,
                    diagramMarginX: 50,
                    diagramMarginY: 10,
                    actorMargin: 50,
                    width: 150,
                    height: 65,
                    boxMargin: 10,
                    boxTextMargin: 5,
                    noteMargin: 10,
                    messageMargin: 35,
                    mirrorActors: true
                },
                gantt: {
                    useMaxWidth: true,
                    barHeight: 20,
                    barGap: 4,
                    topPadding: 50,
                    leftPadding: 75,
                    gridLineStartPadding: 35,
                    fontSize: 11,
                    numberSectionStyles: 4,
                    axisFormat: '%Y-%m-%d'
                },
                er: {
                    useMaxWidth: true
                }
            });

            this.initialized = true;
            this.renderAllDiagrams();
            this.setupEventListeners();
            
            console.log('MermaidLoader initialized');
            return true;
        } catch (error) {
            console.error('Failed to initialize Mermaid:', error);
            return false;
        }
    }

    renderAllDiagrams() {
        if (!this.initialized) return;

        const diagramElements = document.querySelectorAll('.mermaid-preview, .mermaid-container .mermaid');
        diagramElements.forEach((element, index) => {
            this.renderDiagram(element, index);
        });
    }

    renderDiagram(element, id) {
        if (!element || !this.initialized) return;

        const originalContent = element.textContent.trim();
        if (!originalContent) return;

        try {
            // Generate unique ID for the diagram
            const diagramId = `mermaid-diagram-${id}-${Date.now()}`;
            element.id = diagramId;
            
            // Clear and render
            element.textContent = '';
            
            mermaid.render(diagramId, originalContent, (svgCode) => {
                element.innerHTML = svgCode;
                
                // Store reference
                this.diagrams.push({
                    id: diagramId,
                    element: element,
                    content: originalContent
                });
                
                // Apply current zoom
                this.applyZoom(element);
                
                // Dispatch custom event
                element.dispatchEvent(new CustomEvent('mermaid-rendered', {
                    detail: { id: diagramId }
                }));
            });
        } catch (error) {
            console.error(`Failed to render diagram ${id}:`, error);
            element.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error rendering diagram:</strong><br>
                    ${error.message}
                </div>
            `;
        }
    }

    setupEventListeners() {
        // Theme switcher (if any theme buttons exist)
        document.querySelectorAll('[data-mermaid-theme]').forEach(button => {
            button.addEventListener('click', (e) => {
                const theme = e.target.dataset.mermaidTheme;
                this.switchTheme(theme);
            });
        });

        // Auto-render diagrams added dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) { // Element node
                            const mermaidElements = node.querySelectorAll ? 
                                node.querySelectorAll('.mermaid') : [];
                            mermaidElements.forEach((element, index) => {
                                this.renderDiagram(element, this.diagrams.length + index);
                            });
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    switchTheme(theme) {
        if (!this.initialized) return;

        try {
            mermaid.initialize({
                ...mermaid.mermaidAPI.getConfig(),
                theme: theme
            });

            this.currentTheme = theme;
            
            // Re-render all diagrams
            this.diagrams.forEach(diagram => {
                const element = diagram.element;
                const content = diagram.content;
                
                mermaid.render(diagram.id, content, (svgCode) => {
                    element.innerHTML = svgCode;
                    this.applyZoom(element);
                });
            });

            // Update theme buttons
            document.querySelectorAll('[data-mermaid-theme]').forEach(button => {
                if (button.dataset.mermaidTheme === theme) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            });

            console.log(`Switched to ${theme} theme`);
        } catch (error) {
            console.error('Failed to switch theme:', error);
        }
    }

    applyZoom(element) {
        if (this.zoomLevel !== 1) {
            element.style.transform = `scale(${this.zoomLevel})`;
            element.style.transformOrigin = 'top left';
        }
    }

    zoomIn() {
        this.zoomLevel = Math.min(this.zoomLevel + 0.1, 3);
        this.applyZoomToAll();
    }

    zoomOut() {
        this.zoomLevel = Math.max(this.zoomLevel - 0.1, 0.1);
        this.applyZoomToAll();
    }

    resetZoom() {
        this.zoomLevel = 1;
        this.applyZoomToAll();
    }

    applyZoomToAll() {
        this.diagrams.forEach(diagram => {
            this.applyZoom(diagram.element);
        });
    }

    exportDiagram(diagramId, format = 'svg') {
        const diagram = this.diagrams.find(d => d.id === diagramId);
        if (!diagram) {
            console.error(`Diagram ${diagramId} not found`);
            return null;
        }

        const svgElement = diagram.element.querySelector('svg');
        if (!svgElement) {
            console.error('SVG element not found');
            return null;
        }

        if (format === 'svg') {
            const serializer = new XMLSerializer();
            const source = serializer.serializeToString(svgElement);
            
            // Add XML declaration
            const xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>\n';
            const doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n';
            
            return xmlHeader + doctype + source;
        }

        return null;
    }

    downloadDiagram(diagramId, filename = 'diagram.svg') {
        const svgContent = this.exportDiagram(diagramId, 'svg');
        if (!svgContent) return false;

        const blob = new Blob([svgContent], { type: 'image/svg+xml' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        return true;
    }
}

// Create global instance
window.mermaidLoader = new MermaidLoader();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for Mermaid to load if loaded as module
    setTimeout(() => {
        if (typeof mermaid !== 'undefined') {
            window.mermaidLoader.initialize();
        } else {
            console.warn('Mermaid.js not loaded yet, retrying in 500ms...');
            setTimeout(() => {
                if (typeof mermaid !== 'undefined') {
                    window.mermaidLoader.initialize();
                } else {
                    console.error('Mermaid.js failed to load');
                }
            }, 500);
        }
    }, 100);
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MermaidLoader;
}
