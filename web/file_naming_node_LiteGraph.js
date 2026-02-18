import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.FileNaming.LiteGraph",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "FileNaming (LiteGraph)") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated?.apply(this, arguments);

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
                    extra4: "",
                    suffix: "",
                    model_extract: "",
                    loras_extracts: [],
                    data_collapsed: true,
                    dateformat_collapsed: true,
                    model_collapsed: true,
                    loras_collapsed: true,
                    textreplace_collapsed: true,
                    naming_collapsed: true,
                    output_collapsed: true
                }, this.properties);

                // Ajouter de l'espace en haut du node pour les entrées
                this.widgets_start_y = 100;

                this.buildUI();
                return r;
            };

// Système de picking de widget - Version avec cercle et overlays rouges
nodeType.prototype.startPicking = function(targetWidget) {
    const self = this;
    const canvas = app.canvas;
    const graph = app.graph;
    
    console.log("🔗 Picking mode activated");
    
    // Sauvegarder le curseur original
    const originalCursor = document.body.style.cursor;
    document.body.style.cursor = "default";
    
    // Overlay transparent (nécessaire pour le z-index)
    const overlay = document.createElement("div");
    overlay.id = "widget-picker-overlay";
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: transparent;
        z-index: 9997;
        pointer-events: none;
    `;
    
    // Message d'instruction
    const instruction = document.createElement("div");
    instruction.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #4a9eff;
        color: white;
        padding: 12px 24px;
        border-radius: 40px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        pointer-events: none;
        border: 2px solid white;
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    instruction.innerHTML = `
        <span style="font-size: 20px;">🔗</span>
        <span>Click a node to pick a widget</span>
        <span style="background: rgba(255,255,255,0.3); padding: 2px 8px; border-radius: 20px; font-size: 12px;">ESC</span>
    `;
    
    // Canvas pour dessiner les overlays rouges (à garder !)
    const overlayCanvas = document.createElement("canvas");
    overlayCanvas.id = "widget-picker-canvas";
    overlayCanvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9996;
        pointer-events: none;
    `;
    overlayCanvas.width = window.innerWidth;
    overlayCanvas.height = window.innerHeight;
    
    // Cercle qui suit la souris - SANS transition pour plus de fluidité
    const crosshair = document.createElement("div");
    crosshair.id = "picker-crosshair";
    crosshair.style.cssText = `
        position: fixed;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(74, 158, 255, 0.2);
        border: 2px solid #4a9eff;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 9998;
        box-shadow: 0 0 15px rgba(74, 158, 255, 0.3);
        will-change: left, top; /* Optimisation performance */
    `;
    
    // Animation simple pour le cercle (sans transition)
    const style = document.createElement("style");
    style.id = "picker-style";
    style.textContent = `
        @keyframes softPulse {
            0% { transform: translate(-50%, -50%) scale(0.7); opacity: 0.8; }
            50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.5; }
            100% { transform: translate(-50%, -50%) scale(0.7); opacity: 0.8; }
        }
        #picker-crosshair {
            animation: softPulse 1s infinite;
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(overlay);
    document.body.appendChild(overlayCanvas);
    document.body.appendChild(instruction);
    document.body.appendChild(crosshair);
    
    // Fonction pour dessiner les rectangles rouges
    const drawRedOverlays = () => {
        const ctx = overlayCanvas.getContext("2d");
        ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        
        const canvasElement = canvas.canvas;
        const canvasRect = canvasElement.getBoundingClientRect();
        const nodes = graph._nodes || [];
        
        nodes.forEach(node => {
            if (!node) return;
            
            const widgets = node.widgets || [];
            const hasSelectable = widgets.some(w => 
                w.type !== "button" && 
                w.name && 
                !w.name.startsWith("▶") && 
                !w.name.startsWith("▼")
            );
            
            // Garder les overlays rouges sur les nodes non-sélectionnables
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
    
    // Animation loop pour les overlays rouges
    const animate = () => {
        if (document.getElementById("widget-picker-overlay")) {
            drawRedOverlays();
            self.pickingAnimation = requestAnimationFrame(animate);
        }
    };
    animate();
    
    // Faire suivre le cercle - utiliser requestAnimationFrame pour plus de fluidité
    let mouseX = 0, mouseY = 0;
    const handleMouseMove = (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    };
    
    const updateCrosshair = () => {
        if (crosshair && crosshair.parentNode) {
            crosshair.style.left = mouseX + "px";
            crosshair.style.top = mouseY + "px";
            requestAnimationFrame(updateCrosshair);
        }
    };
    
    document.addEventListener("mousemove", handleMouseMove);
    requestAnimationFrame(updateCrosshair);
    
    // Click handler
    const handleClick = (e) => {
        if (e.button !== 0) return;
        
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        
        const canvasElement = canvas.canvas;
        const rect = canvasElement.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const graphX = x / canvas.ds.scale - canvas.ds.offset[0];
        const graphY = y / canvas.ds.scale - canvas.ds.offset[1];
        
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
                self.showWidgetSelector(foundNode, selectable, targetWidget);
                return;
            }
        }
        
        cleanup();
    };
    
    const handleEsc = (e) => {
        if (e.key === "Escape") {
            cleanup();
        }
    };
    
    const cleanup = () => {
        document.body.style.cursor = originalCursor;
        document.removeEventListener("mousemove", handleMouseMove);
        
        if (clickHandlerTimeout) {
            clearTimeout(clickHandlerTimeout);
        }
        
        if (self.pickingAnimation) {
            cancelAnimationFrame(self.pickingAnimation);
            self.pickingAnimation = null;
        }
        
        const elements = [
            document.getElementById("widget-picker-overlay"),
            document.getElementById("widget-picker-canvas"),
            document.getElementById("picker-crosshair"),
            instruction
        ];
        
        elements.forEach(el => {
            if (el && el.parentNode) {
                el.parentNode.removeChild(el);
            }
        });
        
        const styleEl = document.getElementById("picker-style");
        if (styleEl) styleEl.remove();
        
        canvas.canvas.removeEventListener("click", handleClick, true);
        document.removeEventListener("keydown", handleEsc);
    };
    
    document.addEventListener("keydown", handleEsc);
    
    let clickHandlerTimeout = setTimeout(() => {
        canvas.canvas.addEventListener("click", handleClick, true);
        console.log("Click handler activated");
    }, 100);
};            
            // Popup de sélection de widget
            nodeType.prototype.showWidgetSelector = function(sourceNode, widgets, targetWidget) {
				const self = this;
                const popup = document.createElement("div");
                popup.style.cssText = `
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
                `;
                
                const title = document.createElement("div");
                title.textContent = `Select widget from: ${sourceNode.title || sourceNode.type}`;
                title.style.cssText = `
                    color: #fff;
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #555;
                    padding-bottom: 10px;
                `;
                popup.appendChild(title);
                
                widgets.forEach(widget => {
                    const item = document.createElement("div");
                    item.textContent = `${widget.name} (${widget.type})`;
                    item.style.cssText = `
                        padding: 10px;
                        margin: 5px 0;
                        background-color: #3a3a3a;
                        color: #fff;
                        cursor: pointer;
                        border-radius: 4px;
                        transition: background-color 0.2s;
                    `;
                    
                    item.onmouseover = () => item.style.backgroundColor = "#4a4a4a";
                    item.onmouseout = () => item.style.backgroundColor = "#3a3a3a";
                    
                    item.onclick = () => {
                        const reference = `#${sourceNode.id}:${widget.name}`;
                        if (targetWidget.callback) {
                            targetWidget.callback(reference);
                        }
                        targetWidget.value = reference;
                        this.setDirtyCanvas(true, true);
                        document.body.removeChild(popup);
                        document.body.removeChild(bgOverlay);
                    };
                    
                    popup.appendChild(item);
                });
                
                const cancelBtn = document.createElement("button");
                cancelBtn.textContent = "Cancel";
                cancelBtn.style.cssText = `
                    margin-top: 15px;
                    padding: 8px 20px;
                    background-color: #555;
                    color: #fff;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    width: 100%;
                `;
                cancelBtn.onclick = () => {
                    document.body.removeChild(popup);
                    document.body.removeChild(bgOverlay);
                };
                popup.appendChild(cancelBtn);
                
                const bgOverlay = document.createElement("div");
                bgOverlay.style.cssText = `
                    position: fixed;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                    z-index: 9999;
                `;
                bgOverlay.onclick = () => {
                    document.body.removeChild(popup);
                    document.body.removeChild(bgOverlay);
                };
                
                document.body.appendChild(bgOverlay);
                document.body.appendChild(popup);
            };

            nodeType.prototype.buildUI = function() {
                this.widgets = [];
				
				const collapseAllBtn = this.addWidget("button", "▲ Collapse all", null, () => {
				// Liste de toutes les propriétés de collapse
					const collapseProps = [
						"data_collapsed",
						"dateformat_collapsed", 
						"model_collapsed",
						"loras_collapsed",
						"textreplace_collapsed",
						"naming_collapsed",
						"output_collapsed"
					];
					
					// Tout mettre en true (collapsed)
					collapseProps.forEach(prop => {
						this.properties[prop] = true;
					});
					
					// Reconstruire l'interface
					this.buildUI();
				});
				collapseAllBtn.serialize = false;
				
				// Styliser le bouton
				collapseAllBtn.computeSize = function(width) {
					return [width, 24];
				};
				
				collapseAllBtn.draw = function(ctx, node, widget_width, y, H) {
					// Fond légèrement plus foncé
					ctx.fillStyle = "rgba(51,51,51,0.25)";
					ctx.fillRect(2+widget_width/4, y, widget_width/2 - 4, H - 2);
					
					// Bordure subtile
					ctx.strokeStyle = "rgba(134, 172, 230,0.2)";
					ctx.lineWidth = 0;
					ctx.strokeRect(2+widget_width/4, y, widget_width/2 - 4, H - 2);
					
					// Texte
					ctx.fillStyle = "#7090c0";
					ctx.font = "bold 12px Arial";
					ctx.textAlign = "center";
					ctx.fillText("▲ Collapse All Sections", widget_width * 0.5, y + H * 0.65);
					ctx.textAlign = "left";
				};

                const addHeader = (text, collapsedProp) => {
                    const isCollapsed = this.properties[collapsedProp];
                    const arrow = isCollapsed ? "▶" : "▼";
                    const w = this.addWidget("button", `${arrow} ${text}`, null, () => {
                        this.properties[collapsedProp] = !this.properties[collapsedProp];
                        this.buildUI();
                    });
                    w.serialize = false;

                    w.computeSize = function(width) {
                        return [width, 22];
                    };

                    w.draw = function(ctx, node, widget_width, y, H) {
                        ctx.fillStyle = "rgba(0, 0, 0, 0.06)";
                        ctx.fillRect(0, y, widget_width, H);
                        ctx.fillStyle = "#ffffff";
                        ctx.font = "bold 12px Arial";
                        ctx.fillText(this.label || this.name, 6, y + H * 0.7);
                    };

                    return isCollapsed;
                };

                const styleButton = (widget, bgColor, textColor = "#ffffff") => {
                    widget.computeSize = function(width) {
                        return [width, 22];
                    };

                    widget.draw = function(ctx, node, widget_width, y, H) {
                        if (bgColor === "#3a1a1a") {
                            ctx.fillStyle = "rgba(255, 68, 68, 0.08)";
                        } else if (bgColor === "#1a3a1a") {
                            ctx.fillStyle = "rgba(68, 225, 68, 0.06)";
                        } else {
                            ctx.fillStyle = bgColor;
                        }
                        ctx.fillRect(2, y + 1, widget_width - 4, H - 2);

                        ctx.fillStyle = textColor;
                        ctx.font = "12px Arial";
                        ctx.textAlign = "center";
                        ctx.fillText(this.label || this.name, widget_width * 0.5, y + H * 0.65);
                        ctx.textAlign = "left";
                    };
                };
                
                const addTextWithPicker = (label, value, callback) => {
                    const textWidget = this.addWidget("text", label, value, callback);
                    
                    const pickerBtn = this.addWidget("button", "🔗 Pick", null, () => {
                        this.startPicking(textWidget);
                    });
                    pickerBtn.serialize = false;
                    
                    pickerBtn.computeSize = function(width) {
                        return [width, 20];
                    };
                    
                    pickerBtn.draw = function(ctx, node, widget_width, y, H) {
                        ctx.fillStyle = "rgba(68, 138, 255, 0.1)";
                        ctx.fillRect(2, y + 1, widget_width - 4, H - 2);
                        ctx.fillStyle = "#4a9eff";
                        ctx.font = "11px Arial";
                        ctx.textAlign = "center";
                        ctx.fillText("🔗 Pick Widget", widget_width * 0.5, y + H * 0.65);
                        ctx.textAlign = "left";
                    };
                    
                    return textWidget;
                };

                // DATA
                const dataCollapsed = addHeader("DATA", "data_collapsed");
                if (!dataCollapsed) {
                    for (let i = 0; i < this.data_fields.length; i++) {
                        const field = this.data_fields[i];

                        this.addWidget("text", `name`, field.name, (v) => {
                            this.data_fields[i].name = v;
							this.setDirtyCanvas(true, true);
                        });

                        addTextWithPicker(`value (text or #id:widget)`, field.value || "", (v) => {
                            this.data_fields[i].value = v;
                        });

                        const delBtn = this.addWidget("button", "❌", null, () => {
                            this.data_fields.splice(i, 1);
                            this.buildUI();
							this.setDirtyCanvas(true, true);  // ← forcer affichage
                        });
                        delBtn.serialize = false;
                        styleButton(delBtn, "#3a1a1a");
                    }

					const addBtn = this.addWidget("button", "Add Field", null, () => {
						// Trouver le premier numéro libre
						let index = 1;
						const existingNames = this.data_fields.map(f => f.name);
						while (existingNames.includes(`field${index}`)) {
							index++;
						}
						const newName = `field${index}`;

						this.data_fields.push({ name: newName, value: "" });
						this.buildUI();
						this.setDirtyCanvas(true, true);
						setTimeout(() => {
							const newFieldWidgets = this.widgets.filter(w =>
								w.name === "name" && w.value === newName
							);
							if (newFieldWidgets[0]) {
								newFieldWidgets[0].element?.focus();
								newFieldWidgets[0].element?.select();
							}
						}, 50);
                    });
                    addBtn.serialize = false;
                    styleButton(addBtn, "#1a3a1a");
                }

                // DATE FORMAT
                const dateFormatCollapsed = addHeader("DATE FORMAT", "dateformat_collapsed");
                if (!dateFormatCollapsed) {
                    this.addWidget("text", "date1", this.properties.date1, (v) => this.properties.date1 = v);
                    this.addWidget("text", "date2", this.properties.date2, (v) => this.properties.date2 = v);
                    this.addWidget("text", "date3", this.properties.date3, (v) => this.properties.date3 = v);
                }

                // MODEL
                const modelCollapsed = addHeader("MODEL", "model_collapsed");
                if (!modelCollapsed) {
                    addTextWithPicker("extract (#id:widget)", this.properties.model_extract, (v) => {
                        this.properties.model_extract = v;
                    });
                }

                // LORAS
                const lorasCollapsed = addHeader("LORAS", "loras_collapsed");
                if (!lorasCollapsed) {
                    if (!this.properties.loras_extracts) this.properties.loras_extracts = [];
                    for (let i = 0; i < this.properties.loras_extracts.length; i++) {
                        addTextWithPicker(`lora ${i}`, this.properties.loras_extracts[i], (v) => {
                            this.properties.loras_extracts[i] = v;
                        });

                        const delBtn = this.addWidget("button", "❌", null, () => {
                            this.properties.loras_extracts.splice(i, 1);
                            this.buildUI();
                        });
                        delBtn.serialize = false;
                        styleButton(delBtn, "#3a1a1a");
                    }

                    const addLoraBtn = this.addWidget("button", "➕ Lora", null, () => {
                        this.properties.loras_extracts.push("");
                        this.buildUI();
                    });
                    addLoraBtn.serialize = false;
                    styleButton(addLoraBtn, "#1a3a1a");
                }

                // TEXT REPLACE
                const textReplaceCollapsed = addHeader("TEXT REPLACE", "textreplace_collapsed");
                if (!textReplaceCollapsed) {
                    const allFields = ["", "[any1]", "[any2]", "[any3]", ...this.data_fields.map(f => f.name), "model", "loras"];

                    for (let i = 0; i < this.text_replace_pairs.length; i++) {
                        const pair = this.text_replace_pairs[i];

                        this.addWidget("combo", `target`, pair.target || "", (v) => {
                            this.text_replace_pairs[i].target = v;
                        }, { values: allFields });

                        this.addWidget("text", `in`, pair.input, (v) => {
                            this.text_replace_pairs[i].input = v;
                        });

                        this.addWidget("text", `out`, pair.output, (v) => {
                            this.text_replace_pairs[i].output = v;
                        });

                        const delBtn = this.addWidget("button", "❌", null, () => {
                            this.text_replace_pairs.splice(i, 1);
                            this.buildUI();
                        });
                        delBtn.serialize = false;
                        styleButton(delBtn, "#3a1a1a");
                    }

                    const addReplaceBtn = this.addWidget("button", "➕ Replace", null, () => {
                        this.text_replace_pairs.push({ input: "", output: "", target: "" });
                        this.buildUI();
                    });
                    addReplaceBtn.serialize = false;
                    styleButton(addReplaceBtn, "#1a3a1a");
                }

                // NAMING
                const namingCollapsed = addHeader("NAMING", "naming_collapsed");
                if (!namingCollapsed) {
                    const namingFields = [
                        "",
                        "[any1]",
                        "[any2]",
                        "[any3]",
                        ...this.data_fields.map(f => f.name),
                        "model", "loras",
                        "%date1", "%date2", "%date3"
                    ];

                    this.addWidget("combo", "output_folder", this.properties.output_folder, (v) => {
                        this.properties.output_folder = v;
                    }, { values: namingFields });

                    this.addWidget("combo", "prefix", this.properties.prefix, (v) => {
                        this.properties.prefix = v;
                    }, { values: namingFields });

                    this.addWidget("combo", "extra1", this.properties.extra1, (v) => {
                        this.properties.extra1 = v;
                    }, { values: namingFields });

                    this.addWidget("combo", "extra2", this.properties.extra2, (v) => {
                        this.properties.extra2 = v;
                    }, { values: namingFields });

                    this.addWidget("combo", "extra3", this.properties.extra3, (v) => {
                        this.properties.extra3 = v;
                    }, { values: namingFields });

                    this.addWidget("combo", "extra4", this.properties.extra4, (v) => {
                        this.properties.extra4 = v;
                    }, { values: namingFields });

                    this.addWidget("combo", "suffix", this.properties.suffix, (v) => {
                        this.properties.suffix = v;
                    }, { values: namingFields });

                    this.addWidget("text", "separator", this.properties.separator, (v) => {
                        this.properties.separator = v;
                    });
                }

                // OUTPUT
                const outputCollapsed = addHeader("OUTPUT", "output_collapsed");
                if (!outputCollapsed) {
                    this.addWidget("combo", "format", this.properties.output_format, (v) => {
                        this.properties.output_format = v;
                    }, { values: ["png", "jpg", "webp"] });

                    this.addWidget("number", "quality", this.properties.quality, (v) => {
                        this.properties.quality = v;
                    }, { min: 1, max: 100, step: 1 });

                    this.addWidget("toggle", "save metadata", this.properties.save_metadata, (v) => {
                        this.properties.save_metadata = v;
                    });

                    this.addWidget("toggle", "embed workflow", this.properties.embed_workflow, (v) => {
                        this.properties.embed_workflow = v;
                    });
                }

                const currentWidth = this.size ? this.size[0] : 300;
                const newSize = this.computeSize();
                this.setSize([Math.max(currentWidth, newSize[0], 300), newSize[1]]);
            };

            nodeType.prototype.onSerialize = function(o) {
                o.data_fields = this.data_fields;
                o.text_replace_pairs = this.text_replace_pairs;
            };

            nodeType.prototype.onConfigure = function(o) {
                if (o.data_fields) this.data_fields = o.data_fields;
                if (o.text_replace_pairs) this.text_replace_pairs = o.text_replace_pairs;
                this.buildUI();
            };
        }
    }
});
