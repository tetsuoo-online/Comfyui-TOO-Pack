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
                    output_collapsed: true
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

            nodeType.prototype.buildDOMUI = function() {
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

                // DATA Section
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

                        group.appendChild(row1);
                        group.appendChild(row2);
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

                // TEXT REPLACE Section
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
