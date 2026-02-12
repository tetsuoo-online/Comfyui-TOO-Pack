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

                // DATA
                const dataCollapsed = addHeader("DATA", "data_collapsed");
                if (!dataCollapsed) {
                    for (let i = 0; i < this.data_fields.length; i++) {
                        const field = this.data_fields[i];

                        this.addWidget("text", `name`, field.name, (v) => {
                            this.data_fields[i].name = v;
                        });

                        this.addWidget("text", `value (text or #id:widget)`, field.value || "", (v) => {
                            this.data_fields[i].value = v;
                        });

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
                    this.addWidget("text", "extract (#id:widget)", this.properties.model_extract, (v) => {
                        this.properties.model_extract = v;
                    });
                }

                // LORAS
                const lorasCollapsed = addHeader("LORAS", "loras_collapsed");
                if (!lorasCollapsed) {
                    if (!this.properties.loras_extracts) this.properties.loras_extracts = [];
                    for (let i = 0; i < this.properties.loras_extracts.length; i++) {
                        this.addWidget("text", `lora ${i}`, this.properties.loras_extracts[i], (v) => {
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
