import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

function chainCallback(object, property, callback) {
    if (object == undefined) {
        console.error("Tried to add callback to non-existent object");
        return;
    }
    if (property in object && object[property]) {
        const callback_orig = object[property];
        object[property] = function () {
            const r = callback_orig.apply(this, arguments);
            return callback.apply(this, arguments) ?? r;
        };
    } else {
        object[property] = callback;
    }
}

function fitHeight(node) {
    node.setSize([node.size[0], node.computeSize([node.size[0], node.size[1]])[1]]);
    node?.graph?.setDirtyCanvas(true);
}

app.registerExtension({
    name: "TOO.SimpleImageLoader.Preview",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "TOOSimpleImageLoader") {

            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                const previewNode = this;

                // Create preview widget
                var element = document.createElement("div");
                element.style.width = "100%";

                var previewWidget = this.addDOMWidget("imagepreview", "preview", element, {
                    serialize: false,
                    hideOnZoom: false,
                    getValue() { return element.value; },
                    setValue(v) { element.value = v; }
                });

                previewWidget.computeSize = function (width) {
                    if (this.aspectRatio && !this.parentEl.hidden) {
                        let height = (previewNode.size[0] - 20) / this.aspectRatio + 10;
                        if (!(height > 0)) height = 0;
                        return [width, height];
                    }
                    return [width, -4];
                };

                previewWidget.value = { hidden: false, params: {}, enabled: true };
                previewWidget.parentEl = document.createElement("div");
                previewWidget.parentEl.className = "simple_image_loader_preview";
                previewWidget.parentEl.style.width = "100%";
                element.appendChild(previewWidget.parentEl);

                previewWidget.imgEl = document.createElement("img");
                previewWidget.imgEl.style.width = "100%";
                previewWidget.imgEl.style.objectFit = "contain";

                previewWidget.imgEl.onload = () => {
                    previewWidget.aspectRatio = previewWidget.imgEl.naturalWidth / previewWidget.imgEl.naturalHeight;
                    fitHeight(previewNode);
                };

                previewWidget.imgEl.onerror = () => {
                    previewWidget.parentEl.hidden = true;
                    fitHeight(previewNode);
                };

                previewWidget.parentEl.appendChild(previewWidget.imgEl);

                // Function to clear preview
                previewWidget.clearPreview = function() {
                    this.imgEl.src = "";
                    this.imgEl.hidden = true;
                    this.parentEl.hidden = true;
                    this.aspectRatio = null;
                    fitHeight(previewNode);
                };

                // updateParameters function
                var timeout = null;
                previewNode.updateParameters = (params, force_update) => {
                    if (!previewWidget.value.params) {
                        previewWidget.value = { hidden: false, params: {}, enabled: true };
                    }

                    // Always update params (even if preview OFF)
                    Object.assign(previewWidget.value.params, params);

                    if (timeout) {
                        clearTimeout(timeout);
                    }

                    if (force_update) {
                        previewWidget.updateSource();
                    } else {
                        timeout = setTimeout(() => previewWidget.updateSource(), 100);
                    }
                };

                previewWidget.updateSource = function () {
                    // Don't load if disabled
                    if (!this.value.enabled) {
                        console.log("TOOSimpleImageLoader: Preview disabled, not loading");
                        return;
                    }

                    if (this.value.params == undefined || !this.value.params.filename) {
                        console.log("TOOSimpleImageLoader: No filename, not loading");
                        return;
                    }

                    let params = { ...this.value.params };
                    params.timestamp = Date.now();

                    this.parentEl.hidden = this.value.hidden;

                    // Use custom route /too/view/image
                    const url = api.apiURL('/too/view/image?' + new URLSearchParams(params));
                    console.log("TOOSimpleImageLoader: Loading image from", params.filename);

                    this.imgEl.src = url;
                    this.imgEl.hidden = false;
                };

                previewWidget.callback = previewWidget.updateSource;

                // Listen to show_preview toggle
                const showPreviewWidget = this.widgets.find((w) => w.name === "show_preview");

                if (showPreviewWidget) {
                    chainCallback(showPreviewWidget, "callback", (value) => {
                        console.log("TOOSimpleImageLoader: show_preview changed to", value);

                        // Update enabled state
                        previewWidget.value.enabled = value;

                        if (value) {
                            // Enabled: show and reload with current params
                            previewWidget.value.hidden = false;
                            previewWidget.parentEl.hidden = false;

                            // Reload image with current params (including new path)
                            if (previewWidget.value.params && previewWidget.value.params.filename) {
                                console.log("TOOSimpleImageLoader: Reloading with current params:", previewWidget.value.params.filename);
                                previewWidget.updateSource();
                            }
                        } else {
                            // Disabled: clear visual preview BUT keep params for when re-enabled
                            console.log("TOOSimpleImageLoader: Clearing visual preview, keeping params");
                            previewWidget.clearPreview();
                        }

                        fitHeight(previewNode);
                    });

                    // Apply initial state
                    if (showPreviewWidget.value !== undefined) {
                        previewWidget.value.enabled = showPreviewWidget.value;
                        if (!showPreviewWidget.value) {
                            previewWidget.clearPreview();
                        }
                    }
                }

                // Callback on img_path for immediate preview
                const imgPathWidget = this.widgets.find((w) => w.name === "img_path");

                if (imgPathWidget) {
                    chainCallback(imgPathWidget, "callback", (value) => {
                        console.log("TOOSimpleImageLoader: img_path changed to", value);

                        if (!value) {
                            // Clear params AND preview
                            previewWidget.value.params = {};
                            previewWidget.clearPreview();
                            return;
                        }

                        // Check toggle state
                        const showPreview = showPreviewWidget ? showPreviewWidget.value : true;
                        console.log("TOOSimpleImageLoader: show_preview is", showPreview);

                        // Create params (ALWAYS, even if preview OFF)
                        let params = {
                            filename: value,
                            type: "path",
                            format: "folder"
                        };

                        // Update params (will be used when re-enabled)
                        previewNode.updateParameters(params, showPreview); // force_update only if enabled

                        if (!showPreview) {
                            console.log("TOOSimpleImageLoader: Preview disabled, params saved but not loading");
                        }
                    });

                    // Trigger immediately if already filled AND show_preview is true
                    if (imgPathWidget.value && showPreviewWidget && showPreviewWidget.value) {
                        imgPathWidget.callback(imgPathWidget.value);
                    }
                }
            });

            // Context menu
            chainCallback(nodeType.prototype, "getExtraMenuOptions", function (_, options) {
                const previewWidget = this.widgets?.find((w) => w.name === "imagepreview");
                if (!previewWidget) return;

                let optNew = [];
                const url = previewWidget.imgEl?.src;

                if (url && url !== "" && !previewWidget.value.hidden && previewWidget.value.enabled) {
                    optNew.push(
                        {
                            content: "Open preview",
                            callback: () => {
                                window.open(url, "_blank");
                            },
                        },
                        {
                            content: "Save preview",
                            callback: () => {
                                const a = document.createElement("a");
                                a.href = url;
                                a.setAttribute("download", previewWidget.value.params.filename || "image.png");
                                document.body.append(a);
                                a.click();
                                requestAnimationFrame(() => a.remove());
                            },
                        }
                    );
                }

                // Toggle is now handled by show_preview widget
                const visDesc = (previewWidget.value.enabled ? "Disable" : "Enable") + " preview";
                optNew.push({
                    content: visDesc,
                    callback: () => {
                        const showPreviewWidget = this.widgets?.find((w) => w.name === "show_preview");
                        if (showPreviewWidget) {
                            showPreviewWidget.value = !showPreviewWidget.value;
                            if (showPreviewWidget.callback) {
                                showPreviewWidget.callback(showPreviewWidget.value);
                            }
                        }
                    },
                });

                if (options.length > 0 && options[0] != null && optNew.length > 0) {
                    optNew.push(null);
                }
                options.unshift(...optNew);
            });
        }
    },
});
