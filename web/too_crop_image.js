import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.TOOCropImage",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "TOOCropImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated?.apply(this, arguments);

                // Initialize properties for INSET CROP
                if (!this.properties) this.properties = {};
                this.properties = Object.assign({
                    crop_left: 0,
                    crop_right: 0,
                    crop_top: 0,
                    crop_bottom: 0,
                    box_color: "#4a9eff",
                    show_grid: true
                }, this.properties);

                // State
                this.imageData = null;
                this.imageWidth = 0;
                this.imageHeight = 0;
                this.currentPath = "";
                this.dragging = false;
                this.resizing = false;
                this.dragStart = { x: 0, y: 0 };
                this.activeHandle = null;

                // Force exact initial size
                this.size = [350, 200];
                this.setSize([350, 200]);
                
                // Allow manual resize
                this.resizable = true;

                // Monitor img_path changes and setup widget callbacks
                this.setupPathMonitoring();
                this.setupWidgetCallbacks();
                
                // Setup global mouseup listener to prevent sticky handles
                this.setupGlobalMouseUp();

                return r;
            };
            
            // Global mouseup listener to catch events outside the node
            nodeType.prototype.setupGlobalMouseUp = function() {
                const self = this;
                
                if (!this.globalMouseUpHandler) {
                    this.globalMouseUpHandler = function(e) {
                        if (self.dragging || self.resizing) {
                            self.dragging = false;
                            self.resizing = false;
                            self.activeHandle = null;
                            
                            // Try to reset cursor if canvas is available
                            const canvas = app?.canvas;
                            if (canvas && canvas.canvas) {
                                canvas.canvas.style.cursor = "default";
                            }
                            
                            self.setDirtyCanvas(true, true);
                        }
                    };
                    
                    document.addEventListener('mouseup', this.globalMouseUpHandler);
                }
            };
            
            // Cleanup on remove
            nodeType.prototype.onRemoved = function() {
                if (this.globalMouseUpHandler) {
                    document.removeEventListener('mouseup', this.globalMouseUpHandler);
                    this.globalMouseUpHandler = null;
                }
            };

            // Monitor img_path widget changes
            nodeType.prototype.setupPathMonitoring = function() {
                const self = this;
                
                // Watch for widget value changes
                const originalCallback = this.widgets?.[0]?.callback;
                if (this.widgets && this.widgets[0] && this.widgets[0].name === "img_path") {
                    this.widgets[0].callback = function(value) {
                        if (originalCallback) originalCallback.apply(this, arguments);
                        
                        // Clear preview if path is empty or cleared
                        if (!value || !value.trim()) {
                            self.imageData = null;
                            self.imageWidth = 0;
                            self.imageHeight = 0;
                            self.currentPath = "";
                            self.setDirtyCanvas(true, true);
                            return;
                        }
                        
                        // Load new image if path changed
                        if (value && value !== self.currentPath) {
                            self.loadImage(value);
                        }
                    };
                }
            };

            // Setup callbacks on crop widgets
            nodeType.prototype.setupWidgetCallbacks = function() {
                const self = this;
                
                setTimeout(() => {
                    if (!self.widgets) return;
                    
                    for (const widget of self.widgets) {
                        if (widget.name === "left") {
                            const origCallback = widget.callback;
                            widget.callback = function(value) {
                                if (origCallback) origCallback.apply(this, arguments);
                                self.properties.crop_left = Math.round(value);
                                self.setDirtyCanvas(true, true);
                            };
                        }
                        if (widget.name === "right") {
                            const origCallback = widget.callback;
                            widget.callback = function(value) {
                                if (origCallback) origCallback.apply(this, arguments);
                                self.properties.crop_right = Math.round(value);
                                self.setDirtyCanvas(true, true);
                            };
                        }
                        if (widget.name === "top") {
                            const origCallback = widget.callback;
                            widget.callback = function(value) {
                                if (origCallback) origCallback.apply(this, arguments);
                                self.properties.crop_top = Math.round(value);
                                self.setDirtyCanvas(true, true);
                            };
                        }
                        if (widget.name === "bottom") {
                            const origCallback = widget.callback;
                            widget.callback = function(value) {
                                if (origCallback) origCallback.apply(this, arguments);
                                self.properties.crop_bottom = Math.round(value);
                                self.setDirtyCanvas(true, true);
                            };
                        }
                        if (widget.name === "h_offset") {
                            const origCallback = widget.callback;
                            widget.callback = function(value) {
                                if (origCallback) origCallback.apply(this, arguments);
                                if (!self.imageWidth) return; // Wait for image to load
                                
                                const offset = Math.round(value);
                                const selWidth = self.imageWidth - self.properties.crop_left - self.properties.crop_right;
                                
                                self.properties.crop_left = Math.max(0, Math.min(offset, self.imageWidth - selWidth));
                                self.properties.crop_right = self.imageWidth - self.properties.crop_left - selWidth;
                                
                                for (const w of self.widgets) {
                                    if (w.name === "left") w.value = self.properties.crop_left;
                                    if (w.name === "right") w.value = self.properties.crop_right;
                                }
                                self.setDirtyCanvas(true, true);
                            };
                        }
                        if (widget.name === "v_offset") {
                            const origCallback = widget.callback;
                            widget.callback = function(value) {
                                if (origCallback) origCallback.apply(this, arguments);
                                if (!self.imageHeight) return; // Wait for image to load
                                
                                const offset = Math.round(value);
                                const selHeight = self.imageHeight - self.properties.crop_top - self.properties.crop_bottom;
                                
                                self.properties.crop_top = Math.max(0, Math.min(offset, self.imageHeight - selHeight));
                                self.properties.crop_bottom = self.imageHeight - self.properties.crop_top - selHeight;
                                
                                for (const w of self.widgets) {
                                    if (w.name === "top") w.value = self.properties.crop_top;
                                    if (w.name === "bottom") w.value = self.properties.crop_bottom;
                                }
                                self.setDirtyCanvas(true, true);
                            };
                        }
                    }
                }, 100);
            };

            // Load image from path
            nodeType.prototype.loadImage = async function(path) {
                if (!path || !path.trim()) {
                    this.imageData = null;
                    return;
                }

                this.currentPath = path;

                try {
                    const url = `/too/view/image?filename=${encodeURIComponent(path)}&type=path&t=${Date.now()}`;
                    const response = await fetch(url);
                    
                    if (!response.ok) {
                        console.error("Failed to load image:", response.statusText);
                        this.imageData = null;
                        return;
                    }

                    const blob = await response.blob();
                    const img = new Image();
                    
                    img.onload = () => {
                        this.imageData = img;
                        this.imageWidth = img.width;
                        this.imageHeight = img.height;

                        // Initialize to no crop
                        if (!this.properties.crop_left && !this.properties.crop_right && 
                            !this.properties.crop_top && !this.properties.crop_bottom) {
                            this.properties.crop_left = 0;
                            this.properties.crop_right = 0;
                            this.properties.crop_top = 0;
                            this.properties.crop_bottom = 0;
                            this.updateWidgets();
                        }

                        // Auto-expand node to show image preview (no gap between widgets and preview)
                        const widgetCount = this.widgets ? this.widgets.length : 0;
                        const imageInputConnected = this.inputs && this.inputs.some(input => 
                            input.name === "image" && input.link != null
                        );
                        const warningHeight = imageInputConnected ? 27 : 0;
                        const minHeight = 30 + (widgetCount * 30) + warningHeight + 280 + 35;
                        
                        if (this.size[1] < minHeight) {
                            this.size[1] = minHeight;
                        }

                        this.setDirtyCanvas(true, true);
                    };

                    img.src = URL.createObjectURL(blob);

                } catch (error) {
                    console.error("Error loading image:", error);
                    this.imageData = null;
                }
            };

            // Update widget values from properties
            nodeType.prototype.updateWidgets = function() {
                if (!this.widgets) return;

                for (const widget of this.widgets) {
                    if (widget.name === "left") widget.value = this.properties.crop_left;
                    if (widget.name === "right") widget.value = this.properties.crop_right;
                    if (widget.name === "top") widget.value = this.properties.crop_top;
                    if (widget.name === "bottom") widget.value = this.properties.crop_bottom;
                    
                    // Sync offsets: offset = position of selection
                    if (widget.name === "h_offset") {
                        widget.value = this.properties.crop_left;
                        // Update max based on current selection width
                        const selWidth = this.imageWidth - this.properties.crop_left - this.properties.crop_right;
                        widget.options.max = Math.max(0, this.imageWidth - selWidth);
                    }
                    if (widget.name === "v_offset") {
                        widget.value = this.properties.crop_top;
                        const selHeight = this.imageHeight - this.properties.crop_top - this.properties.crop_bottom;
                        widget.options.max = Math.max(0, this.imageHeight - selHeight);
                    }
                }
            };

            // Get handle at position
            nodeType.prototype.getHandleAt = function(x, y, rect) {
                const handleSize = 12;
                const handles = this.getHandles(rect);

                for (const [name, pos] of Object.entries(handles)) {
                    const dx = x - pos.x;
                    const dy = y - pos.y;
                    if (Math.abs(dx) <= handleSize && Math.abs(dy) <= handleSize) {
                        return name;
                    }
                }

                return null;
            };

            // Get all handle positions
            nodeType.prototype.getHandles = function(rect) {
                const { x, y, width, height } = rect;
                return {
                    "nw": { x: x, y: y },
                    "n": { x: x + width / 2, y: y },
                    "ne": { x: x + width, y: y },
                    "e": { x: x + width, y: y + height / 2 },
                    "se": { x: x + width, y: y + height },
                    "s": { x: x + width / 2, y: y + height },
                    "sw": { x: x, y: y + height },
                    "w": { x: x, y: y + height / 2 }
                };
            };

            // Convert canvas coords to image coords
            nodeType.prototype.canvasToImage = function(canvasX, canvasY, displayRect) {
                const scaleX = this.imageWidth / displayRect.width;
                const scaleY = this.imageHeight / displayRect.height;
                
                const relX = canvasX - displayRect.x;
                const relY = canvasY - displayRect.y;
                
                return {
                    x: Math.round(relX * scaleX),
                    y: Math.round(relY * scaleY)
                };
            };

            // Convert image coords to canvas coords
            nodeType.prototype.imageToCanvas = function(imgX, imgY, displayRect) {
                const scaleX = displayRect.width / this.imageWidth;
                const scaleY = displayRect.height / this.imageHeight;
                
                return {
                    x: displayRect.x + imgX * scaleX,
                    y: displayRect.y + imgY * scaleY
                };
            };

            // Mouse handlers
            nodeType.prototype.onMouseDown = function(e, localPos, canvas) {
                if (!this.imageData) return;

                const displayRect = this.getDisplayRect();
                if (!displayRect) return;

                const cropRect = this.getCropRect(displayRect);
                const handle = this.getHandleAt(localPos[0], localPos[1], cropRect);

                if (handle) {
                    this.resizing = true;
                    this.activeHandle = handle;
                    this.dragStart = { x: localPos[0], y: localPos[1] };
                    return true;
                }

                // Check if inside crop box
                if (localPos[0] >= cropRect.x && localPos[0] <= cropRect.x + cropRect.width &&
                    localPos[1] >= cropRect.y && localPos[1] <= cropRect.y + cropRect.height) {
                    this.dragging = true;
                    this.dragStart = { x: localPos[0], y: localPos[1] };
                    return true;
                }
            };

            nodeType.prototype.onMouseMove = function(e, localPos, canvas) {
                if (!this.imageData) return;

                const displayRect = this.getDisplayRect();
                if (!displayRect) return;

                // Safety: if mouse button is not pressed but we think we're dragging, reset
                if ((this.dragging || this.resizing) && e.buttons !== 1) {
                    this.dragging = false;
                    this.resizing = false;
                    this.activeHandle = null;
                    canvas.canvas.style.cursor = "default";
                    return false;
                }

                if (this.resizing && this.activeHandle) {
                    const imgCurrent = this.canvasToImage(localPos[0], localPos[1], displayRect);
                    const imgStart = this.canvasToImage(this.dragStart.x, this.dragStart.y, displayRect);
                    const imgDx = imgCurrent.x - imgStart.x;
                    const imgDy = imgCurrent.y - imgStart.y;

                    const handle = this.activeHandle;
                    let { crop_left, crop_right, crop_top, crop_bottom } = this.properties;

                    // INSET CROP LOGIC: handles adjust how much we remove from each edge
                    if (handle.includes('w')) {
                        // Left handle: moving right increases crop_left
                        crop_left += imgDx;
                    }
                    if (handle.includes('e')) {
                        // Right handle: moving left increases crop_right
                        crop_right -= imgDx;
                    }
                    if (handle.includes('n')) {
                        // Top handle: moving down increases crop_top
                        crop_top += imgDy;
                    }
                    if (handle.includes('s')) {
                        // Bottom handle: moving up increases crop_bottom
                        crop_bottom -= imgDy;
                    }

                    // Clamp to valid ranges
                    crop_left = Math.max(0, Math.min(crop_left, this.imageWidth - crop_right - 1));
                    crop_right = Math.max(0, Math.min(crop_right, this.imageWidth - crop_left - 1));
                    crop_top = Math.max(0, Math.min(crop_top, this.imageHeight - crop_bottom - 1));
                    crop_bottom = Math.max(0, Math.min(crop_bottom, this.imageHeight - crop_top - 1));

                    this.properties.crop_left = Math.round(crop_left);
                    this.properties.crop_right = Math.round(crop_right);
                    this.properties.crop_top = Math.round(crop_top);
                    this.properties.crop_bottom = Math.round(crop_bottom);

                    this.dragStart = { x: localPos[0], y: localPos[1] };
                    this.updateWidgets();
                    this.setDirtyCanvas(true, true);
                    return true;
                }

                if (this.dragging) {
                    const imgStart = this.canvasToImage(this.dragStart.x, this.dragStart.y, displayRect);
                    const imgCurrent = this.canvasToImage(localPos[0], localPos[1], displayRect);
                    const imgDx = imgCurrent.x - imgStart.x;
                    const imgDy = imgCurrent.y - imgStart.y;

                    let { crop_left, crop_right, crop_top, crop_bottom } = this.properties;

                    // Moving the visible area: decrease crop on one side, increase on other
                    crop_left += imgDx;
                    crop_right -= imgDx;
                    crop_top += imgDy;
                    crop_bottom -= imgDy;

                    // Clamp
                    if (crop_left < 0) {
                        crop_right += crop_left;
                        crop_left = 0;
                    }
                    if (crop_right < 0) {
                        crop_left += crop_right;
                        crop_right = 0;
                    }
                    if (crop_top < 0) {
                        crop_bottom += crop_top;
                        crop_top = 0;
                    }
                    if (crop_bottom < 0) {
                        crop_top += crop_bottom;
                        crop_bottom = 0;
                    }

                    // Check total bounds
                    const maxLeft = this.imageWidth - crop_right - 1;
                    const maxRight = this.imageWidth - crop_left - 1;
                    const maxTop = this.imageHeight - crop_bottom - 1;
                    const maxBottom = this.imageHeight - crop_top - 1;

                    crop_left = Math.min(crop_left, maxLeft);
                    crop_right = Math.min(crop_right, maxRight);
                    crop_top = Math.min(crop_top, maxTop);
                    crop_bottom = Math.min(crop_bottom, maxBottom);

                    this.properties.crop_left = Math.round(crop_left);
                    this.properties.crop_right = Math.round(crop_right);
                    this.properties.crop_top = Math.round(crop_top);
                    this.properties.crop_bottom = Math.round(crop_bottom);

                    this.dragStart = { x: localPos[0], y: localPos[1] };
                    this.updateWidgets();
                    this.setDirtyCanvas(true, true);
                    return true;
                }

                // Update cursor (only when not dragging/resizing)
                const cropRect = this.getCropRect(displayRect);
                const handle = this.getHandleAt(localPos[0], localPos[1], cropRect);
                
                if (handle) {
                    const cursors = {
                        "nw": "nw-resize", "n": "n-resize", "ne": "ne-resize",
                        "e": "e-resize", "se": "se-resize", "s": "s-resize",
                        "sw": "sw-resize", "w": "w-resize"
                    };
                    canvas.canvas.style.cursor = cursors[handle] || "default";
                } else if (localPos[0] >= cropRect.x && localPos[0] <= cropRect.x + cropRect.width &&
                           localPos[1] >= cropRect.y && localPos[1] <= cropRect.y + cropRect.height) {
                    canvas.canvas.style.cursor = "move";
                } else {
                    canvas.canvas.style.cursor = "default";
                }
            };

            nodeType.prototype.onMouseUp = function(e, localPos, canvas) {
                // Always reset state on mouseup, even if we weren't dragging
                const wasDragging = this.dragging || this.resizing;
                
                this.dragging = false;
                this.resizing = false;
                this.activeHandle = null;
                
                if (canvas && canvas.canvas) {
                    canvas.canvas.style.cursor = "default";
                }
                
                // Return true if we were handling an interaction
                return wasDragging;
            };

            // Get display rectangle for image
            nodeType.prototype.getDisplayRect = function() {
                if (!this.imageData) return null;

                // Calculate Y offset based on widgets - no gap between widgets and preview
                const widgetCount = this.widgets ? this.widgets.length : 0;
                const titleHeight = 30;
                const widgetHeight = widgetCount * 30;
                
                // Check if image input is connected (need warning banner)
                const imageInputConnected = this.inputs && this.inputs.some(input => 
                    input.name === "image" && input.link != null
                );
                const warningHeight = imageInputConnected ? 27 : 0;
                
                const canvasStartY = widgetHeight + warningHeight;

                const padding = 10;
                const availWidth = this.size[0] - padding * 2;
                const availHeight = 280; // Fixed preview height
                const imgAspect = this.imageWidth / this.imageHeight;
                const availAspect = availWidth / availHeight;

                let displayWidth, displayHeight;

                if (imgAspect > availAspect) {
                    displayWidth = availWidth;
                    displayHeight = availWidth / imgAspect;
                } else {
                    displayHeight = availHeight;
                    displayWidth = availHeight * imgAspect;
                }

                return {
                    x: padding + (availWidth - displayWidth) / 2,
                    y: canvasStartY,
                    width: displayWidth,
                    height: displayHeight
                };
            };

            // Get crop rectangle in canvas coords (the visible area AFTER cropping)
            nodeType.prototype.getCropRect = function(displayRect) {
                // Calculate visible area after removing pixels from each side
                const visibleLeft = this.properties.crop_left;
                const visibleTop = this.properties.crop_top;
                const visibleRight = this.imageWidth - this.properties.crop_right;
                const visibleBottom = this.imageHeight - this.properties.crop_bottom;

                const topLeft = this.imageToCanvas(visibleLeft, visibleTop, displayRect);
                const bottomRight = this.imageToCanvas(visibleRight, visibleBottom, displayRect);

                return {
                    x: topLeft.x,
                    y: topLeft.y,
                    width: bottomRight.x - topLeft.x,
                    height: bottomRight.y - topLeft.y
                };
            };

            // Draw on canvas
            nodeType.prototype.onDrawForeground = function(ctx) {
                // Check if image input is connected
                const imageInputConnected = this.inputs && this.inputs.some(input => 
                    input.name === "image" && input.link != null
                );

                if (!this.imageData) {
                    // Show different message based on whether image input is connected
                    const widgetCount = this.widgets ? this.widgets.length : 0;
                    const titleHeight = 30;
                    const widgetHeight = widgetCount * 30;
                    const yStart = widgetHeight;
                    
                    // Only show message if node is tall enough
                    if (this.size[1] > yStart + 40) {
                        ctx.fillStyle = "#888";
                        ctx.font = "12px Arial";
                        ctx.textAlign = "center";
                        
                        if (imageInputConnected) {
                            // Image input connected but no preview
                            ctx.fillStyle = "#ff9800";
                            ctx.fillText("⚠ Preview disabled when using image input", this.size[0] / 2, yStart + 20);
                            ctx.fillStyle = "#888";
                            ctx.font = "11px Arial";
                            ctx.fillText("[ Set img_path for interactive preview ]", this.size[0] / 2, yStart + 36);
                        } else {
                            // No image at all
                            ctx.fillText("[ Set img_path for interactive preview ]", this.size[0] / 2, yStart + 20);
                        }
                    }
                    return;
                }

                // If we have preview image but input is connected, show warning
                if (imageInputConnected && this.imageData) {
                    const widgetCount = this.widgets ? this.widgets.length : 0;
                    const warningY = widgetCount * 30;
                    
                    ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                    ctx.fillRect(10, warningY, this.size[0] - 20, 22);
                    ctx.fillStyle = "#d4a017";
                    ctx.font = "11px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("⚠ Preview shows img_path, execution uses image input", this.size[0] / 2, warningY + 14);
                    ctx.textAlign = "left";
                }

                const displayRect = this.getDisplayRect();
                if (!displayRect) return;

                // Draw image
                ctx.drawImage(
                    this.imageData,
                    displayRect.x,
                    displayRect.y,
                    displayRect.width,
                    displayRect.height
                );

                // Draw darkened overlay outside crop
                ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
                
                const cropRect = this.getCropRect(displayRect);
                
                // Top
                ctx.fillRect(displayRect.x, displayRect.y, displayRect.width, cropRect.y - displayRect.y);
                // Bottom
                ctx.fillRect(displayRect.x, cropRect.y + cropRect.height, displayRect.width, 
                    (displayRect.y + displayRect.height) - (cropRect.y + cropRect.height));
                // Left
                ctx.fillRect(displayRect.x, cropRect.y, cropRect.x - displayRect.x, cropRect.height);
                // Right
                ctx.fillRect(cropRect.x + cropRect.width, cropRect.y, 
                    (displayRect.x + displayRect.width) - (cropRect.x + cropRect.width), cropRect.height);

                // Draw crop box
                ctx.strokeStyle = this.properties.box_color;
                ctx.lineWidth = 2;
                ctx.strokeRect(cropRect.x, cropRect.y, cropRect.width, cropRect.height);

                // Draw grid
                if (this.properties.show_grid) {
                    ctx.strokeStyle = this.properties.box_color;
                    ctx.lineWidth = 1;
                    ctx.globalAlpha = 0.3;
                    
                    // Rule of thirds
                    const third_w = cropRect.width / 3;
                    const third_h = cropRect.height / 3;
                    
                    ctx.beginPath();
                    ctx.moveTo(cropRect.x + third_w, cropRect.y);
                    ctx.lineTo(cropRect.x + third_w, cropRect.y + cropRect.height);
                    ctx.moveTo(cropRect.x + third_w * 2, cropRect.y);
                    ctx.lineTo(cropRect.x + third_w * 2, cropRect.y + cropRect.height);
                    ctx.moveTo(cropRect.x, cropRect.y + third_h);
                    ctx.lineTo(cropRect.x + cropRect.width, cropRect.y + third_h);
                    ctx.moveTo(cropRect.x, cropRect.y + third_h * 2);
                    ctx.lineTo(cropRect.x + cropRect.width, cropRect.y + third_h * 2);
                    ctx.stroke();
                    
                    ctx.globalAlpha = 1.0;
                }

                // Draw handles
                const handles = this.getHandles(cropRect);
                const handleSize = 8;

                ctx.fillStyle = this.properties.box_color;
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;

                for (const pos of Object.values(handles)) {
                    ctx.fillRect(pos.x - handleSize / 2, pos.y - handleSize / 2, handleSize, handleSize);
                    ctx.strokeRect(pos.x - handleSize / 2, pos.y - handleSize / 2, handleSize, handleSize);
                }

                // Draw info - centered
                const croppedWidth = this.imageWidth - this.properties.crop_left - this.properties.crop_right;
                const croppedHeight = this.imageHeight - this.properties.crop_top - this.properties.crop_bottom;
                
                const info = `Original: ${this.imageWidth}×${this.imageHeight}  →  Cropped: ${croppedWidth}×${croppedHeight}`;

                const infoY = displayRect.y + displayRect.height + 10;

                ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
                ctx.fillRect(10, infoY, this.size[0] - 20, 25);
                ctx.fillStyle = "#ffffff";
                ctx.font = "12px monospace";
                ctx.textAlign = "center";
                ctx.fillText(info, this.size[0] / 2, infoY + 17);
                ctx.textAlign = "left";
            };

            // Load image on configure
            nodeType.prototype.onConfigure = function(info) {
                if (info.widgets_values && info.widgets_values[0]) {
                    const path = info.widgets_values[0];
                    if (path && path !== this.currentPath) {
                        this.loadImage(path);
                    }
                }
            };
        }
    }
});
