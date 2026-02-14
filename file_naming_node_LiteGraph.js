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
                    output_collapsed: true
                }, this.properties);

                // Ajouter de l'espace en haut du node pour les entrées
                this.widgets_start_y = 125;

                this.buildUI();
                return r;
            };

            // Fonction pour activer le mode picking
            nodeType.prototype.startPicking = function(targetWidget) {
                const self = this;
                const canvas = app.canvas;
                const graph = app.graph;
                
                console.log("🔗 Picking mode activated - Click on a node to select a widget");
                
                // Créer un overlay qui capture tous les clics
                const overlay = document.createElement("div");
                overlay.id = "widget-picker-overlay";
                overlay.style.position = "fixed";
                overlay.style.top = "0";
                overlay.style.left = "0";
                overlay.style.width = "100%";
                overlay.style.height = "100%";
                overlay.style.zIndex = "9998";
                overlay.style.cursor = "url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"black\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71\"/><path d=\"M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71\"/></svg>') 0 24, auto";
                overlay.style.backgroundColor = "rgba(74, 158, 255, 0.05)";
                
                // Texte d'instruction
                const instruction = document.createElement("div");
                instruction.style.position = "fixed";
                instruction.style.top = "20px";
                instruction.style.left = "50%";
                instruction.style.transform = "translateX(-50%)";
                instruction.style.backgroundColor = "rgba(74, 158, 255, 0.95)";
                instruction.style.color = "#fff";
                instruction.style.padding = "12px 24px";
                instruction.style.borderRadius = "8px";
                instruction.style.fontSize = "14px";
                instruction.style.fontWeight = "bold";
                instruction.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
                instruction.style.zIndex = "9999";
                instruction.textContent = "🔗 Click on a node to pick a widget (ESC to cancel)";
                
                document.body.appendChild(overlay);
                document.body.appendChild(instruction);
                
                // Handler pour le clic sur l'overlay
                const clickHandler = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Récupérer le canvas element
                    const canvasElement = canvas.canvas;
                    const rect = canvasElement.getBoundingClientRect();
                    
                    // Coordonnées relatives au canvas
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    // Coordonnées dans le graph (tenir compte du zoom et du pan)
                    const graphX = x / canvas.ds.scale - canvas.ds.offset[0];
                    const graphY = y / canvas.ds.scale - canvas.ds.offset[1];
                    
                    console.log("Click at:", { x, y, graphX, graphY });
                    
                    // Trouver le node à cette position
                    let foundNode = null;
                    const nodes = graph._nodes || [];
                    
                    for (let i = nodes.length - 1; i >= 0; i--) {
                        const node = nodes[i];
                        if (!node) continue;
                        
                        // Vérifier si le clic est dans le node
                        if (graphX >= node.pos[0] && 
                            graphX <= node.pos[0] + node.size[0] &&
                            graphY >= node.pos[1] &&
                            graphY <= node.pos[1] + node.size[1]) {
                            foundNode = node;
                            console.log("Found node:", node.title || node.type);
                            break;
                        }
                    }
                    
                    // Nettoyer l'overlay et l'instruction
                    document.body.removeChild(overlay);
                    document.body.removeChild(instruction);
                    document.removeEventListener("keydown", escHandler);
                    
                    if (foundNode && foundNode !== self) {
                        // Récupérer les widgets sélectionnables
                        const widgets = foundNode.widgets || [];
                        const selectableWidgets = widgets.filter(w => 
                            w.type !== "button" && 
                            w.name && 
                            !w.name.startsWith("▶") && 
                            !w.name.startsWith("▼")
                        );
                        
                        if (selectableWidgets.length === 0) {
                            alert("This node has no selectable widgets");
                            return;
                        }
                        
                        // Afficher le sélecteur de widget
                        self.showWidgetSelector(foundNode, selectableWidgets, targetWidget);
                    }
                };
                
                // Handler pour ESC
                const escHandler = (e) => {
                    if (e.key === "Escape") {
                        console.log("Picking cancelled");
                        document.body.removeChild(overlay);
                        document.body.removeChild(instruction);
                        document.removeEventListener("keydown", escHandler);
                    }
                };
                
                overlay.addEventListener("click", clickHandler);
                document.addEventListener("keydown", escHandler);
            };
            
            // Fonction pour afficher le sélecteur de widget
            nodeType.prototype.showWidgetSelector = function(sourceNode, widgets, targetWidget) {
                // Créer un popup HTML
                const popup = document.createElement("div");
                popup.style.position = "fixed";
                popup.style.left = "50%";
                popup.style.top = "50%";
                popup.style.transform = "translate(-50%, -50%)";
                popup.style.backgroundColor = "#2a2a2a";
                popup.style.border = "2px solid #555";
                popup.style.borderRadius = "8px";
                popup.style.padding = "20px";
                popup.style.zIndex = "10000";
                popup.style.minWidth = "300px";
                popup.style.maxWidth = "500px";
                popup.style.maxHeight = "600px";
                popup.style.overflowY = "auto";
                popup.style.boxShadow = "0 4px 20px rgba(0,0,0,0.5)";
                
                // Titre
                const title = document.createElement("div");
                title.textContent = `Select widget from: ${sourceNode.title || sourceNode.type}`;
                title.style.color = "#fff";
                title.style.fontSize = "16px";
                title.style.fontWeight = "bold";
                title.style.marginBottom = "15px";
                title.style.borderBottom = "1px solid #555";
                title.style.paddingBottom = "10px";
                popup.appendChild(title);
                
                // Liste des widgets
                const list = document.createElement("div");
                widgets.forEach((widget, index) => {
                    if (widget.type === "button" || !widget.name) return;
                    
                    const item = document.createElement("div");
                    item.textContent = `${widget.name} (${widget.type})`;
                    item.style.padding = "10px";
                    item.style.margin = "5px 0";
                    item.style.backgroundColor = "#3a3a3a";
                    item.style.color = "#fff";
                    item.style.cursor = "pointer";
                    item.style.borderRadius = "4px";
                    item.style.transition = "background-color 0.2s";
                    
                    item.onmouseover = () => {
                        item.style.backgroundColor = "#4a4a4a";
                    };
                    
                    item.onmouseout = () => {
                        item.style.backgroundColor = "#3a3a3a";
                    };
                    
                    item.onclick = () => {
                        // Construire la référence #id:widget
                        const reference = `#${sourceNode.id}:${widget.name}`;
                        
                        // Mettre à jour le widget cible
                        if (targetWidget.callback) {
                            targetWidget.callback(reference);
                        }
                        targetWidget.value = reference;
                        
                        // Forcer le rafraîchissement
                        this.setDirtyCanvas(true, true);
                        
                        // Fermer le popup
                        document.body.removeChild(popup);
                        document.body.removeChild(overlay);
                    };
                    
                    list.appendChild(item);
                });
                popup.appendChild(list);
                
                // Bouton annuler
                const cancelBtn = document.createElement("button");
                cancelBtn.textContent = "Cancel";
                cancelBtn.style.marginTop = "15px";
                cancelBtn.style.padding = "8px 20px";
                cancelBtn.style.backgroundColor = "#555";
                cancelBtn.style.color = "#fff";
                cancelBtn.style.border = "none";
                cancelBtn.style.borderRadius = "4px";
                cancelBtn.style.cursor = "pointer";
                cancelBtn.style.width = "100%";
                
                cancelBtn.onclick = () => {
                    document.body.removeChild(popup);
                    document.body.removeChild(overlay);
                };
                
                popup.appendChild(cancelBtn);
                
                // Overlay semi-transparent
                const overlay = document.createElement("div");
                overlay.style.position = "fixed";
                overlay.style.left = "0";
                overlay.style.top = "0";
                overlay.style.width = "100%";
                overlay.style.height = "100%";
                overlay.style.backgroundColor = "rgba(0,0,0,0.5)";
                overlay.style.zIndex = "9999";
                
                overlay.onclick = () => {
                    document.body.removeChild(popup);
                    document.body.removeChild(overlay);
                };
                
                document.body.appendChild(overlay);
                document.body.appendChild(popup);
            };

            nodeType.prototype.buildUI = function() {
                this.widgets = [];

                const addHeader = (text, collapsedProp) => {
                    const isCollapsed = this.properties[collapsedProp];
                    const arrow = isCollapsed ? "▶" : "▼";
                    const w = this.addWidget("button", `${arrow} ${text}`, null, () => {
                        this.properties[collapsedProp] = !this.properties[collapsedProp];
                        this.buildUI();
                    });
                    w.serialize = false;

                    // Style pour headers - transparent
                    w.computeSize = function(width) {
                        return [width, 22];
                    };

                    const originalDraw = w.draw;
                    w.draw = function(ctx, node, widget_width, y, H) {
                        // Fond noir à 5% d'opacité
                        ctx.fillStyle = "rgba(0, 0, 0, 0.06)";
                        ctx.fillRect(0, y, widget_width, H);

                        // Texte blanc en gras
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

                    const originalDraw = widget.draw;
                    widget.draw = function(ctx, node, widget_width, y, H) {
                        // Fond avec 20% d'opacité pour boutons rouge et vert
                        if (bgColor === "#3a1a1a") {
                            ctx.fillStyle = "rgba(255, 68, 68, 0.05)";
                        } else if (bgColor === "#1a3a1a") {
                            ctx.fillStyle = "rgba(68, 225, 68, 0.05)";
                        } else {
                            ctx.fillStyle = bgColor;
                        }
                        ctx.fillRect(2, y + 1, widget_width - 4, H - 2);

                        // Texte
                        ctx.fillStyle = textColor;
                        ctx.font = "12px Arial";
                        ctx.textAlign = "center";
                        ctx.fillText(this.label || this.name, widget_width * 0.5, y + H * 0.65);
                        ctx.textAlign = "left";
                    };
                };
                
                // Fonction helper pour ajouter un widget text avec bouton picker
                const addTextWidgetWithPicker = (name, value, callback) => {
                    const textWidget = this.addWidget("text", name, value, callback);
                    
                    // Ajouter un bouton picker
                    const pickerBtn = this.addWidget("button", "🔗 Pick", null, () => {
                        this.startPicking(textWidget);
                    });
                    pickerBtn.serialize = false;
                    
                    // Style du bouton picker
                    pickerBtn.computeSize = function(width) {
                        return [width, 20];
                    };
                    
                    const originalDraw = pickerBtn.draw;
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
                        });

                        addTextWidgetWithPicker(
                            `value (text or #id:widget)`, 
                            field.value || "", 
                            (v) => {
                                this.data_fields[i].value = v;
                            }
                        );

                        const delBtn = this.addWidget("button", "❌", null, () => {
                            this.data_fields.splice(i, 1);
                            this.buildUI();
                        });
                        delBtn.serialize = false;
                        styleButton(delBtn, "#3a1a1a");
                    }

                    const addBtn = this.addWidget("button", "➕ Add Field", null, () => {
                        this.data_fields.push({ name: "field", value: "" });
                        this.buildUI();
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
                    addTextWidgetWithPicker(
                        "extract (#id:widget)", 
                        this.properties.model_extract, 
                        (v) => {
                            this.properties.model_extract = v;
                        }
                    );
                }

                // LORAS
                const lorasCollapsed = addHeader("LORAS", "loras_collapsed");
                if (!lorasCollapsed) {
                    if (!this.properties.loras_extracts) this.properties.loras_extracts = [];
                    for (let i = 0; i < this.properties.loras_extracts.length; i++) {
                        addTextWidgetWithPicker(
                            `lora ${i}`, 
                            this.properties.loras_extracts[i], 
                            (v) => {
                                this.properties.loras_extracts[i] = v;
                            }
                        );

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

                    this.addWidget("combo", "model", this.properties.model, (v) => {
                        this.properties.model = v;
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
