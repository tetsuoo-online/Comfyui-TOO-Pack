import { app } from "../../scripts/app.js";

const CSS_STYLES = `
.file-naming-container {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 10px;
    color: #ffffff;
    font-family: Arial, sans-serif;
    font-size: 12px;
    width: 100%;
    box-sizing: border-box;
    max-height: 800px;
    overflow-y: auto;
    overflow-x: hidden;
}

.file-naming-container::-webkit-scrollbar {
    width: 8px;
}

.file-naming-container::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
}

.file-naming-container::-webkit-scrollbar-thumb {
    background: rgba(119, 119, 136, 0.5);
    border-radius: 4px;
}

.file-naming-container::-webkit-scrollbar-thumb:hover {
    background: rgba(119, 119, 136, 0.7);
}

.fn-header {
    background: rgba(0, 0, 0, 0.125);
    padding: 6px 10px;
    margin: 0 0 2px 0;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
}

.fn-header:hover {
    background: rgba(0, 0, 0, 0.2);
}

.fn-header-title {
    font-weight: bold;
    font-size: 13px;
    color: #ffffff;
}

.fn-arrow {
    margin-right: 8px;
    display: inline-block;
    width: 12px;
}

.fn-section-content {
    padding: 8px 4px;
    display: none;
    overflow: hidden;
}

.fn-section-content.active {
    display: block;
}

.fn-field-group {
    background: rgba(255, 255, 255, 0.03);
    padding: 8px;
    margin-bottom: 4px;
    border-radius: 4px;
    border-left: 2px solid rgba(119, 119, 136, 0.4);
    position: relative;
    transition: all 0.2s ease;
}

.fn-field-group.draggable {
    cursor: grab;
}

.fn-field-group.draggable:active {
    cursor: grabbing;
}

.fn-field-group.dragging {
    opacity: 0.5;
    transform: scale(0.95);
}

.fn-field-group.drag-over {
    border-top: 3px solid #44ff44;
    margin-top: 8px;
}

.fn-drag-handle {
    position: absolute;
    left: -2px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(119, 119, 136, 0.6);
    font-size: 16px;
    font-weight: bold;
    cursor: grab;
    padding: 4px;
    user-select: none;
}

.fn-drag-handle:hover {
    color: rgba(119, 119, 136, 1);
}

.fn-drag-handle:active {
    cursor: grabbing;
}

.fn-field-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
}

.fn-field-row:last-child {
    margin-bottom: 0;
}

.fn-label {
    color: #cccccc;
    font-size: 11px;
    min-width: 140px;
    flex-shrink: 0;
}

.fn-input, .fn-select {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    color: #ffffff;
    padding: 4px 8px;
    font-size: 11px;
    flex: 1;
    min-width: 0;
}

.fn-input:focus, .fn-select:focus {
    outline: none;
    border-color: rgba(119, 119, 136, 0.6);
    box-shadow: 0 0 0 2px rgba(119, 119, 136, 0.2);
}

.fn-input::placeholder {
    color: rgba(255, 255, 255, 0.3);
}

.fn-button {
    background: rgba(255, 68, 68, 0.2);
    border: 1px solid #ff4444;
    border-radius: 4px;
    color: #ffffff;
    padding: 4px 12px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    flex-shrink: 0;
}

.fn-button:hover {
    background: rgba(255, 68, 68, 0.35);
    transform: scale(1.05);
}

.fn-button.add {
    background: rgba(68, 255, 68, 0.2);
    border-color: #44ff44;
    width: 100%;
    margin-top: 4px;
}

.fn-button.add:hover {
    background: rgba(68, 255, 68, 0.35);
}

.fn-number-input {
    width: 70px;
    flex: 0 0 70px;
}

.fn-toggle {
    background: rgba(46, 204, 113, 0.2);
    border: 1px solid #2ecc71;
    border-radius: 4px;
    color: #ffffff;
    padding: 4px 16px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 60px;
    flex-shrink: 0;
}

.fn-toggle:hover {
    background: rgba(46, 204, 113, 0.35);
}

.fn-toggle.off {
    background: rgba(128, 128, 128, 0.2);
    border-color: #888888;
}

.fn-toggle.off:hover {
    background: rgba(128, 128, 128, 0.35);
}

.fn-button.pick {
    background: rgba(68, 138, 255, 0.2);
    border-color: #4a9eff;
    width: 100%;
    margin-top: 4px;
}

.fn-button.pick:hover {
    background: rgba(68, 138, 255, 0.35);
}

/* Popup styles */
.widget-picker-popup {
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background-color: #2a2a2a;
    border: 2px solid #555;
    border-radius: 8px;
    padding: 20px;
    z-index: 10000;
    min-width: 300px;
    max-width: 500px;
    max-height: 600px;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.widget-picker-title {
    color: #fff;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 15px;
    border-bottom: 1px solid #555;
    padding-bottom: 10px;
}

.widget-picker-item {
    padding: 10px;
    margin: 5px 0;
    background-color: #3a3a3a;
    color: #fff;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.widget-picker-item:hover {
    background-color: #4a4a4a;
}

.widget-picker-overlay {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0);
    z-index: 9997;
    pointer-events: none;
}

.widget-picker-modal-overlay {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    z-index: 9999;
}

.widget-picker-instruction {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background-color: rgba(74, 158, 255, 0.95);
    color: #fff;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 9999;
    pointer-events: none;
}

.widget-picker-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9998;
    pointer-events: none;
}
`;

function injectStyles() {
    if (!document.getElementById('file-naming-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'file-naming-styles';
        styleSheet.textContent = CSS_STYLES;
        document.head.appendChild(styleSheet);
        console.log('FileNaming CSS styles injected');
    }
}

app.registerExtension({
    name: "Comfy.FileNaming.DOM",

    async setup() {
        injectStyles();
    },

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "FileNaming (DOM)") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated?.apply(this, arguments);

                // Données initiales
                this.data_fields = this.data_fields || [
                    { name: "positive", value: "" },
                    { name: "negative", value: "" },
                    { name: "seed", value: "" },
                    { name: "steps", value: "" },
                    { name: "cfg", value: "" },
                    { name: "sampler", value: "" },
                    { name: "scheduler", value: "" }
                ];

                this.text_replace_pairs = this.text_replace_pairs || [
                    { input: "", output: "", target: "" }
                ];

                if (!this.properties) this.properties = {};
                this.properties = Object.assign({
                    date1: "YYYY-MM-DD",
                    date2: "YYYY-MM-DD_HHmmss",
                    date3: "HHmmss",
                    separator: "_",
                    output_format: "webp",
                    embed_workflow: true,
                    save_metadata: true,
                    quality: 95,
                    output_folder: "",
                    prefix: "",
                    extra1: "",
                    extra2: "",
                    extra3: "",
                    model: "",
                    suffix: "",
                    model_extract: "",
                    loras_extracts: [],
                    data_collapsed: true,
                    dateformat_collapsed: true,
                    model_collapsed: true,
                    loras_collapsed: true,
                    textreplace_collapsed: true,
                    naming_collapsed: true,
                    output_collapsed: true,
                    _scrollTop: 0
                }, this.properties);

                // Masquer les widgets originaux
                setTimeout(() => {
                    if (this.widgets) {
                        this.widgets.forEach(w => {
                            if (w.name !== "image") {
                                w.computeSize = () => [0, -4];
                                w.type = "hidden";
                            }
                        });
                    }
                }, 100);

                this.buildDOMUI();
                this.setSize([400, 800]);

                return r;
            };

            // Fonction helper pour créer les event listeners de drag-and-drop
            nodeType.prototype.makeDraggable = function(group, index, array, arrayName) {
				const self = this;
                group.draggable = true;
                group.classList.add('draggable');
                group.dataset.index = index;
                group.dataset.arrayName = arrayName;

                // Ajouter le handle de drag
                const dragHandle = document.createElement('div');
                dragHandle.className = 'fn-drag-handle';
                dragHandle.textContent = '⋮⋮';
                dragHandle.title = 'Drag to reorder';
                group.insertBefore(dragHandle, group.firstChild);

                group.addEventListener('dragstart', (e) => {
                    group.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', index);
                });

                group.addEventListener('dragend', (e) => {
                    group.classList.remove('dragging');
                    document.querySelectorAll('.fn-field-group').forEach(g => {
                        g.classList.remove('drag-over');
                    });
                });

                group.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';

                    const dragging = document.querySelector('.dragging');
                    if (dragging && dragging !== group && dragging.dataset.arrayName === group.dataset.arrayName) {
                        group.classList.add('drag-over');
                    }
                });

                group.addEventListener('dragleave', (e) => {
                    group.classList.remove('drag-over');
                });

                group.addEventListener('drop', (e) => {
                    e.preventDefault();
                    group.classList.remove('drag-over');

                    const dragging = document.querySelector('.dragging');
                    if (!dragging || dragging.dataset.arrayName !== group.dataset.arrayName) return;

                    const fromIndex = parseInt(dragging.dataset.index);
                    const toIndex = parseInt(group.dataset.index);

                    if (fromIndex === toIndex) return;

                    // Réorganiser le tableau
                    const targetArray = arrayName === 'data_fields' ? self.data_fields : self.text_replace_pairs;
                    const [movedItem] = targetArray.splice(fromIndex, 1);
                    targetArray.splice(toIndex, 0, movedItem);

                    // Rebuild UI
                    self.rebuildUI();
                });
            };

            // Système de picking de widget
            nodeType.prototype.startPicking = function(inputElement) {
                const self = this;
                const canvas = app.canvas;
                const graph = app.graph;
                
                console.log("🔗 Picking mode activated");
                
                // Changer le curseur du document
                const originalCursor = document.body.style.cursor;
                document.body.style.cursor = "crosshair";
                
                // Overlay semi-transparent
                const overlay = document.createElement("div");
                overlay.className = "widget-picker-overlay";
                
                // Message d'instruction
                const instruction = document.createElement("div");
                instruction.className = "widget-picker-instruction";
                instruction.innerHTML = "🔗 Click on a node to pick a widget &nbsp;•&nbsp; ESC to cancel";
                
                // Canvas pour dessiner les overlays rouges
                const overlayCanvas = document.createElement("canvas");
                overlayCanvas.className = "widget-picker-canvas";
                overlayCanvas.width = window.innerWidth;
                overlayCanvas.height = window.innerHeight;
                
                document.body.appendChild(overlay);
                document.body.appendChild(instruction);
                document.body.appendChild(overlayCanvas);
                
                // Fonction pour dessiner les rectangles rouges
                const drawRedOverlays = () => {
                    const ctx = overlayCanvas.getContext("2d");
                    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                    
                    const canvasRect = canvas.canvas.getBoundingClientRect();
                    const nodes = graph._nodes || [];
                    
                    nodes.forEach(node => {
                        if (!node) return;
                        
                        // Vérifier si le node a des widgets sélectionnables
                        const widgets = node.widgets || [];
                        const hasSelectable = widgets.some(w => 
                            w.type !== "button" && 
                            w.name && 
                            !w.name.startsWith("▶") && 
                            !w.name.startsWith("▼")
                        );
                        
                        // Si pas sélectionnable OU c'est le node lui-même, dessiner en rouge
                        if (!hasSelectable || node === self) {
                            const x = canvasRect.left + (node.pos[0] + canvas.ds.offset[0]) * canvas.ds.scale;
                            const y = canvasRect.top + (node.pos[1] + canvas.ds.offset[1]) * canvas.ds.scale;
                            const w = node.size[0] * canvas.ds.scale;
                            const h = node.size[1] * canvas.ds.scale;
                            
                            ctx.fillStyle = "rgba(100, 20, 20, 0.5)";
                            ctx.fillRect(x, y, w, h);
                        }
                    });
                };
                
                // Animation loop
                const animate = () => {
                    if (document.body.contains(overlay)) {
                        drawRedOverlays();
                        self.pickingAnimation = requestAnimationFrame(animate);
                    }
                };
                animate();
                
                // Click handler
                const handleClick = (e) => {
                    if (e.button !== 0) return; // Seulement left-click
                    
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    
                    const rect = canvas.canvas.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const graphX = x / canvas.ds.scale - canvas.ds.offset[0];
                    const graphY = y / canvas.ds.scale - canvas.ds.offset[1];
                    
                    // Trouver le node
                    const nodes = graph._nodes || [];
                    let foundNode = null;
                    
                    for (let i = nodes.length - 1; i >= 0; i--) {
                        const node = nodes[i];
                        if (!node) continue;
                        
                        if (graphX >= node.pos[0] && graphX <= node.pos[0] + node.size[0] &&
                            graphY >= node.pos[1] && graphY <= node.pos[1] + node.size[1]) {
                            foundNode = node;
                            break;
                        }
                    }
                    
                    if (foundNode && foundNode.id !== self.id) {
                        const widgets = foundNode.widgets || [];
                        
                        const selectable = widgets.filter(w => 
                            w.type !== "button" && 
                            w.name && 
                            !w.name.startsWith("▶") && 
                            !w.name.startsWith("▼")
                        );
                        
                        if (selectable.length > 0) {
                            cleanup();
                            self.showWidgetSelector(foundNode, selectable, inputElement);
                            return;
                        }
                    }
                    
                    cleanup();
                };
                
                // ESC handler
                const handleEsc = (e) => {
                    if (e.key === "Escape") {
                        cleanup();
                    }
                };
                
                // Cleanup function
                const cleanup = () => {
                    document.body.style.cursor = originalCursor;
                    
                    if (clickHandlerTimeout) {
                        clearTimeout(clickHandlerTimeout);
                    }
                    
                    if (self.pickingAnimation) {
                        cancelAnimationFrame(self.pickingAnimation);
                        self.pickingAnimation = null;
                    }
                    
                    if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
                    if (instruction.parentNode) instruction.parentNode.removeChild(instruction);
                    if (overlayCanvas.parentNode) overlayCanvas.parentNode.removeChild(overlayCanvas);
                    
                    canvas.canvas.removeEventListener("click", handleClick, true);
                    document.removeEventListener("keydown", handleEsc);
                };
                
                document.addEventListener("keydown", handleEsc);
                
                // Attendre un court instant avant d'activer le click handler
                let clickHandlerTimeout = setTimeout(() => {
                    canvas.canvas.addEventListener("click", handleClick, true);
                }, 100);
            };
            
            // Popup de sélection de widget
            nodeType.prototype.showWidgetSelector = function(sourceNode, widgets, inputElement) {
                const self = this;
                
                const popup = document.createElement("div");
                popup.className = "widget-picker-popup";
                
                const title = document.createElement("div");
                title.className = "widget-picker-title";
                title.textContent = `Select widget from: ${sourceNode.title || sourceNode.type}`;
                popup.appendChild(title);
                
                widgets.forEach(widget => {
                    const item = document.createElement("div");
                    item.className = "widget-picker-item";
                    item.textContent = `${widget.name} (${widget.type})`;
                    
                    item.onclick = () => {
                        const reference = `#${sourceNode.id}:${widget.name}`;
                        inputElement.value = reference;
                        
                        // Déclencher l'événement input pour que les listeners réagissent
                        const event = new Event('input', { bubbles: true });
                        inputElement.dispatchEvent(event);
                        
                        self.rebuildUI();
                        document.body.removeChild(popup);
                        document.body.removeChild(bgOverlay);
                    };
                    
                    popup.appendChild(item);
                });
                
                const cancelBtn = document.createElement("button");
                cancelBtn.className = "fn-button";
                cancelBtn.textContent = "Cancel";
                cancelBtn.style.marginTop = "15px";
                cancelBtn.style.width = "100%";
                cancelBtn.onclick = () => {
                    document.body.removeChild(popup);
                    document.body.removeChild(bgOverlay);
                };
                popup.appendChild(cancelBtn);
                
                const bgOverlay = document.createElement("div");
                bgOverlay.className = "widget-picker-modal-overlay";
                bgOverlay.onclick = () => {
                    document.body.removeChild(popup);
                    document.body.removeChild(bgOverlay);
                };
                
                document.body.appendChild(bgOverlay);
                document.body.appendChild(popup);
            };

            nodeType.prototype.buildDOMUI = function() {
                // Sauvegarder la position de scroll actuelle
                if (this.domWidget && this.domWidget.element) {
                    const container = this.domWidget.element.querySelector('.file-naming-container');
                    if (container) {
                        this.properties._scrollTop = container.scrollTop;
                    }
                }

                // Nettoyer l'ancien widget DOM s'il existe
                if (this.domWidget) {
                    if (this.domWidget.element && this.domWidget.element.parentNode) {
                        this.domWidget.element.parentNode.removeChild(this.domWidget.element);
                    }

                    // Retirer de la liste des widgets
                    const index = this.widgets?.indexOf(this.domWidget);
                    if (index !== -1 && index !== undefined) {
                        this.widgets.splice(index, 1);
                    }
                    this.domWidget = null;
                }

                const container = document.createElement('div');
                container.className = 'file-naming-container';

                // Ajouter un listener pour sauvegarder le scroll en continu
                container.addEventListener('scroll', () => {
                    this.properties._scrollTop = container.scrollTop;
                });

                // DATA Section (avec drag-and-drop)
                this.createSection(container, "DATA", "data_collapsed", () => {
                    const content = document.createElement('div');

                    this.data_fields.forEach((field, index) => {
                        const group = document.createElement('div');
                        group.className = 'fn-field-group';

                        const row1 = document.createElement('div');
                        row1.className = 'fn-field-row';

                        const label1 = document.createElement('div');
                        label1.className = 'fn-label';
                        label1.textContent = 'Name:';

                        const input1 = document.createElement('input');
                        input1.className = 'fn-input';
                        input1.value = field.name;
                        input1.addEventListener('input', (e) => {
                            this.data_fields[index].name = e.target.value;
                        });

                        row1.appendChild(label1);
                        row1.appendChild(input1);

                        const row2 = document.createElement('div');
                        row2.className = 'fn-field-row';

                        const label2 = document.createElement('div');
                        label2.className = 'fn-label';
                        label2.textContent = 'Value:';

                        const input2 = document.createElement('input');
                        input2.className = 'fn-input';
                        input2.placeholder = 'text or #id:widget';
                        input2.value = field.value || '';
                        input2.addEventListener('input', (e) => {
                            this.data_fields[index].value = e.target.value;
                        });

                        const deleteBtn = document.createElement('button');
                        deleteBtn.className = 'fn-button';
                        deleteBtn.textContent = '❌';
                        deleteBtn.addEventListener('click', () => {
                            this.data_fields.splice(index, 1);
                            this.rebuildUI();
                        });

                        row2.appendChild(label2);
                        row2.appendChild(input2);
                        row2.appendChild(deleteBtn);
                        
                        // Ajouter le bouton Pick pour Value
                        const rowPick = document.createElement('div');
                        rowPick.className = 'fn-field-row';
                        
                        const pickBtn = document.createElement('button');
                        pickBtn.className = 'fn-button pick';
                        pickBtn.textContent = '🔗 Pick Widget';
                        pickBtn.addEventListener('click', () => {
                            this.startPicking(input2);
                        });
                        
                        rowPick.appendChild(pickBtn);

                        group.appendChild(row1);
                        group.appendChild(row2);
                        group.appendChild(rowPick);

                        // Rendre le groupe draggable
                        this.makeDraggable(group, index, this.data_fields, 'data_fields');

                        content.appendChild(group);
                    });

                    const addBtn = document.createElement('button');
                    addBtn.className = 'fn-button add';
                    addBtn.textContent = '➕ Add Field';
                    addBtn.addEventListener('click', () => {
                        this.data_fields.push({ name: 'field', value: '' });
                        this.rebuildUI();
                    });

                    content.appendChild(addBtn);
                    return content;
                });

                // DATE FORMAT Section
                this.createSection(container, "DATE FORMAT", "dateformat_collapsed", () => {
                    const content = document.createElement('div');

                    ['date1', 'date2', 'date3'].forEach(key => {
                        const row = document.createElement('div');
                        row.className = 'fn-field-row';

                        const label = document.createElement('div');
                        label.className = 'fn-label';
                        label.textContent = key + ':';

                        const input = document.createElement('input');
                        input.className = 'fn-input';
                        input.value = this.properties[key];
                        input.addEventListener('input', (e) => {
                            this.properties[key] = e.target.value;
                        });

                        row.appendChild(label);
                        row.appendChild(input);
                        content.appendChild(row);
                    });

                    return content;
                });

                // MODEL Section
                this.createSection(container, "MODEL", "model_collapsed", () => {
                    const content = document.createElement('div');

                    const row = document.createElement('div');
                    row.className = 'fn-field-row';

                    const label = document.createElement('div');
                    label.className = 'fn-label';
                    label.textContent = 'Extract (#id:widget):';

                    const input = document.createElement('input');
                    input.className = 'fn-input';
                    input.value = this.properties.model_extract;
                    input.addEventListener('input', (e) => {
                        this.properties.model_extract = e.target.value;
                    });

                    row.appendChild(label);
                    row.appendChild(input);
                    content.appendChild(row);
                    
                    // Ajouter le bouton Pick
                    const rowPick = document.createElement('div');
                    rowPick.className = 'fn-field-row';
                    
                    const pickBtn = document.createElement('button');
                    pickBtn.className = 'fn-button pick';
                    pickBtn.textContent = '🔗 Pick Widget';
                    pickBtn.addEventListener('click', () => {
                        this.startPicking(input);
                    });
                    
                    rowPick.appendChild(pickBtn);
                    content.appendChild(rowPick);

                    return content;
                });

                // LORAS Section
                this.createSection(container, "LORAS", "loras_collapsed", () => {
                    const content = document.createElement('div');

                    if (!this.properties.loras_extracts) this.properties.loras_extracts = [];

                    this.properties.loras_extracts.forEach((lora, index) => {
                        const row = document.createElement('div');
                        row.className = 'fn-field-row';

                        const label = document.createElement('div');
                        label.className = 'fn-label';
                        label.textContent = `Lora ${index}:`;

                        const input = document.createElement('input');
                        input.className = 'fn-input';
                        input.value = lora;
                        input.addEventListener('input', (e) => {
                            this.properties.loras_extracts[index] = e.target.value;
                        });

                        const deleteBtn = document.createElement('button');
                        deleteBtn.className = 'fn-button';
                        deleteBtn.textContent = '❌';
                        deleteBtn.addEventListener('click', () => {
                            this.properties.loras_extracts.splice(index, 1);
                            this.rebuildUI();
                        });

                        row.appendChild(label);
                        row.appendChild(input);
                        row.appendChild(deleteBtn);
                        content.appendChild(row);
                        
                        // Ajouter le bouton Pick pour ce Lora
                        const rowPick = document.createElement('div');
                        rowPick.className = 'fn-field-row';
                        
                        const pickBtn = document.createElement('button');
                        pickBtn.className = 'fn-button pick';
                        pickBtn.textContent = '🔗 Pick Widget';
                        pickBtn.addEventListener('click', () => {
                            this.startPicking(input);
                        });
                        
                        rowPick.appendChild(pickBtn);
                        content.appendChild(rowPick);
                    });

                    const addBtn = document.createElement('button');
                    addBtn.className = 'fn-button add';
                    addBtn.textContent = '➕ Add Lora';
                    addBtn.addEventListener('click', () => {
                        this.properties.loras_extracts.push('');
                        this.rebuildUI();
                    });

                    content.appendChild(addBtn);
                    return content;
                });

                // TEXT REPLACE Section (avec drag-and-drop)
                this.createSection(container, "TEXT REPLACE", "textreplace_collapsed", () => {
                    const content = document.createElement('div');
                    const allFields = ['', '[any1]', '[any2]', '[any3]', ...this.data_fields.map(f => f.name), 'model', 'loras'];

                    this.text_replace_pairs.forEach((pair, index) => {
                        const group = document.createElement('div');
                        group.className = 'fn-field-group';

                        const row1 = document.createElement('div');
                        row1.className = 'fn-field-row';

                        const label1 = document.createElement('div');
                        label1.className = 'fn-label';
                        label1.textContent = 'Target:';

                        const select = document.createElement('select');
                        select.className = 'fn-select';

                        allFields.forEach(field => {
                            const option = document.createElement('option');
                            option.value = field;
                            option.textContent = field || '(select)';
                            if (field === pair.target) option.selected = true;
                            select.appendChild(option);
                        });

                        select.addEventListener('change', (e) => {
                            this.text_replace_pairs[index].target = e.target.value;
                        });

                        row1.appendChild(label1);
                        row1.appendChild(select);

                        const row2 = document.createElement('div');
                        row2.className = 'fn-field-row';

                        const label2 = document.createElement('div');
                        label2.className = 'fn-label';
                        label2.textContent = 'Input:';

                        const input2 = document.createElement('input');
                        input2.className = 'fn-input';
                        input2.value = pair.input;
                        input2.addEventListener('input', (e) => {
                            this.text_replace_pairs[index].input = e.target.value;
                        });

                        row2.appendChild(label2);
                        row2.appendChild(input2);

                        const row3 = document.createElement('div');
                        row3.className = 'fn-field-row';

                        const label3 = document.createElement('div');
                        label3.className = 'fn-label';
                        label3.textContent = 'Output:';

                        const input3 = document.createElement('input');
                        input3.className = 'fn-input';
                        input3.value = pair.output;
                        input3.addEventListener('input', (e) => {
                            this.text_replace_pairs[index].output = e.target.value;
                        });

                        const deleteBtn = document.createElement('button');
                        deleteBtn.className = 'fn-button';
                        deleteBtn.textContent = '❌';
                        deleteBtn.addEventListener('click', () => {
                            this.text_replace_pairs.splice(index, 1);
                            this.rebuildUI();
                        });

                        row3.appendChild(label3);
                        row3.appendChild(input3);
                        row3.appendChild(deleteBtn);

                        group.appendChild(row1);
                        group.appendChild(row2);
                        group.appendChild(row3);

                        // Rendre le groupe draggable
                        this.makeDraggable(group, index, this.text_replace_pairs, 'text_replace_pairs');

                        content.appendChild(group);
                    });

                    const addBtn = document.createElement('button');
                    addBtn.className = 'fn-button add';
                    addBtn.textContent = '➕ Add Replace';
                    addBtn.addEventListener('click', () => {
                        this.text_replace_pairs.push({ input: '', output: '', target: '' });
                        this.rebuildUI();
                    });

                    content.appendChild(addBtn);
                    return content;
                });

                // NAMING Section
                this.createSection(container, "NAMING", "naming_collapsed", () => {
                    const content = document.createElement('div');
                    const namingFields = ['', '[any1]', '[any2]', '[any3]', ...this.data_fields.map(f => f.name), 'model', 'loras', '%date1', '%date2', '%date3'];

                    ['output_folder', 'prefix', 'extra1', 'extra2', 'extra3', 'model', 'suffix'].forEach(key => {
                        const row = document.createElement('div');
                        row.className = 'fn-field-row';

                        const label = document.createElement('div');
                        label.className = 'fn-label';
                        label.textContent = key + ':';

                        const select = document.createElement('select');
                        select.className = 'fn-select';

                        namingFields.forEach(field => {
                            const option = document.createElement('option');
                            option.value = field;
                            option.textContent = field || '(none)';
                            if (field === this.properties[key]) option.selected = true;
                            select.appendChild(option);
                        });

                        select.addEventListener('change', (e) => {
                            this.properties[key] = e.target.value;
                        });

                        row.appendChild(label);
                        row.appendChild(select);
                        content.appendChild(row);
                    });

                    const separatorRow = document.createElement('div');
                    separatorRow.className = 'fn-field-row';

                    const separatorLabel = document.createElement('div');
                    separatorLabel.className = 'fn-label';
                    separatorLabel.textContent = 'separator:';

                    const separatorInput = document.createElement('input');
                    separatorInput.className = 'fn-input';
                    separatorInput.value = this.properties.separator;
                    separatorInput.addEventListener('input', (e) => {
                        this.properties.separator = e.target.value;
                    });

                    separatorRow.appendChild(separatorLabel);
                    separatorRow.appendChild(separatorInput);
                    content.appendChild(separatorRow);

                    return content;
                });

                // OUTPUT Section
                this.createSection(container, "OUTPUT", "output_collapsed", () => {
                    const content = document.createElement('div');

                    const formatRow = document.createElement('div');
                    formatRow.className = 'fn-field-row';

                    const formatLabel = document.createElement('div');
                    formatLabel.className = 'fn-label';
                    formatLabel.textContent = 'format:';

                    const formatSelect = document.createElement('select');
                    formatSelect.className = 'fn-select';

                    ['png', 'jpg', 'webp'].forEach(format => {
                        const option = document.createElement('option');
                        option.value = format;
                        option.textContent = format;
                        if (format === this.properties.output_format) option.selected = true;
                        formatSelect.appendChild(option);
                    });

                    formatSelect.addEventListener('change', (e) => {
                        this.properties.output_format = e.target.value;
                    });

                    formatRow.appendChild(formatLabel);
                    formatRow.appendChild(formatSelect);
                    content.appendChild(formatRow);

                    const qualityRow = document.createElement('div');
                    qualityRow.className = 'fn-field-row';

                    const qualityLabel = document.createElement('div');
                    qualityLabel.className = 'fn-label';
                    qualityLabel.textContent = 'quality:';

                    const qualityInput = document.createElement('input');
                    qualityInput.className = 'fn-input fn-number-input';
                    qualityInput.type = 'number';
                    qualityInput.min = 1;
                    qualityInput.max = 100;
                    qualityInput.value = this.properties.quality;
                    qualityInput.addEventListener('input', (e) => {
                        this.properties.quality = parseInt(e.target.value);
                    });

                    qualityRow.appendChild(qualityLabel);
                    qualityRow.appendChild(qualityInput);
                    content.appendChild(qualityRow);

                    const metadataRow = document.createElement('div');
                    metadataRow.className = 'fn-field-row';

                    const metadataLabel = document.createElement('div');
                    metadataLabel.className = 'fn-label';
                    metadataLabel.textContent = 'save metadata:';

                    const metadataToggle = document.createElement('button');
                    metadataToggle.className = 'fn-toggle' + (this.properties.save_metadata ? '' : ' off');
                    metadataToggle.textContent = this.properties.save_metadata ? 'ON' : 'OFF';
                    metadataToggle.addEventListener('click', () => {
                        this.properties.save_metadata = !this.properties.save_metadata;
                        metadataToggle.textContent = this.properties.save_metadata ? 'ON' : 'OFF';
                        metadataToggle.className = 'fn-toggle' + (this.properties.save_metadata ? '' : ' off');
                    });

                    metadataRow.appendChild(metadataLabel);
                    metadataRow.appendChild(metadataToggle);
                    content.appendChild(metadataRow);

                    const workflowRow = document.createElement('div');
                    workflowRow.className = 'fn-field-row';

                    const workflowLabel = document.createElement('div');
                    workflowLabel.className = 'fn-label';
                    workflowLabel.textContent = 'embed workflow:';

                    const workflowToggle = document.createElement('button');
                    workflowToggle.className = 'fn-toggle' + (this.properties.embed_workflow ? '' : ' off');
                    workflowToggle.textContent = this.properties.embed_workflow ? 'ON' : 'OFF';
                    workflowToggle.addEventListener('click', () => {
                        this.properties.embed_workflow = !this.properties.embed_workflow;
                        workflowToggle.textContent = this.properties.embed_workflow ? 'ON' : 'OFF';
                        workflowToggle.className = 'fn-toggle' + (this.properties.embed_workflow ? '' : ' off');
                    });

                    workflowRow.appendChild(workflowLabel);
                    workflowRow.appendChild(workflowToggle);
                    content.appendChild(workflowRow);

                    return content;
                });

                // Ajouter le DOM au node
                if (this.addDOMWidget) {
                    this.domWidget = this.addDOMWidget('filenamingui', 'div', container);
                    console.log('DOM widget added successfully');

                    // Restaurer la position de scroll après que le DOM soit complètement construit
                    requestAnimationFrame(() => {
                        if (container && this.properties._scrollTop > 0) {
                            container.scrollTop = this.properties._scrollTop;
                        }
                    });
                }
            };

            nodeType.prototype.createSection = function(container, title, collapsedProp, contentBuilder) {
                const section = document.createElement('div');

                const header = document.createElement('div');
                header.className = 'fn-header';

                const headerTitle = document.createElement('div');
                headerTitle.className = 'fn-header-title';

                const arrow = document.createElement('span');
                arrow.className = 'fn-arrow';
                arrow.textContent = this.properties[collapsedProp] ? '▶' : '▼';

                headerTitle.appendChild(arrow);
                headerTitle.appendChild(document.createTextNode(title));

                const content = document.createElement('div');
                content.className = 'fn-section-content';
                if (!this.properties[collapsedProp]) {
                    content.classList.add('active');
                }

                const builtContent = contentBuilder.call(this);
                content.appendChild(builtContent);

                header.addEventListener('click', () => {
                    this.properties[collapsedProp] = !this.properties[collapsedProp];
                    arrow.textContent = this.properties[collapsedProp] ? '▶' : '▼';
                    content.classList.toggle('active');
                });

                header.appendChild(headerTitle);
                section.appendChild(header);
                section.appendChild(content);
                container.appendChild(section);
            };

            nodeType.prototype.rebuildUI = function() {
                console.log('Rebuilding UI...');
                this.buildDOMUI();
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, true);
                }
            };

            nodeType.prototype.onSerialize = function(o) {
                o.data_fields = this.data_fields;
                o.text_replace_pairs = this.text_replace_pairs;
                // Important: sauvegarder les properties pour le Python
                if (!o.properties) o.properties = {};
                Object.assign(o.properties, this.properties);
            };

            nodeType.prototype.onConfigure = function(o) {
                console.log('onConfigure called with:', o);
                if (o.data_fields) this.data_fields = o.data_fields;
                if (o.text_replace_pairs) this.text_replace_pairs = o.text_replace_pairs;

                // Attendre que les propriétés soient bien chargées
                setTimeout(() => {
                    console.log('Rebuilding UI after configure');
                    this.buildDOMUI();
                    if (this.graph) {
                        this.graph.setDirtyCanvas(true, true);
                    }
                }, 200);
            };

            // Gérer le recreate (Fix node)
            const onRemoved = nodeType.prototype.onRemoved;
            nodeType.prototype.onRemoved = function() {
                console.log('onRemoved called');
                if (this.domWidget && this.domWidget.element && this.domWidget.element.parentNode) {
                    this.domWidget.element.parentNode.removeChild(this.domWidget.element);
                }

                if (onRemoved) {
                    return onRemoved.apply(this, arguments);
                }
            };
        }
    }
});
