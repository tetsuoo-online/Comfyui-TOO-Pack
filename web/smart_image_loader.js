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
    name: "TOO.SmartImageLoader.Preview",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SmartImageLoader") {

            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                const previewNode = this;

                // Créer le widget preview
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
                previewWidget.parentEl.className = "smart_image_loader_preview";
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

                // Fonction pour vider la preview
                previewWidget.clearPreview = function() {
                    this.imgEl.src = "";
                    this.imgEl.hidden = true;
                    this.parentEl.hidden = true;
                    this.aspectRatio = null;
                    fitHeight(previewNode);
                };

                // Fonction updateParameters
                var timeout = null;
                previewNode.updateParameters = (params, force_update) => {
                    if (!previewWidget.value.params) {
                        previewWidget.value = { hidden: false, params: {}, enabled: true };
                    }

                    // TOUJOURS mettre à jour les params (même si preview OFF)
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
                    // NE PAS charger si désactivé
                    if (!this.value.enabled) {
                        console.log("SmartImageLoader: Preview disabled, not loading");
                        return;
                    }

                    if (this.value.params == undefined || !this.value.params.filename) {
                        console.log("SmartImageLoader: No filename, not loading");
                        return;
                    }

                    let params = { ...this.value.params };
                    params.timestamp = Date.now();

                    this.parentEl.hidden = this.value.hidden;

                    // Utiliser la route custom /too/view/image
                    const url = api.apiURL('/too/view/image?' + new URLSearchParams(params));
                    console.log("SmartImageLoader: Loading image from", params.filename);

                    this.imgEl.src = url;
                    this.imgEl.hidden = false;
                };

                previewWidget.callback = previewWidget.updateSource;

                // ÉCOUTER LE TOGGLE show_preview
                const showPreviewWidget = this.widgets.find((w) => w.name === "show_preview");

                if (showPreviewWidget) {
                    chainCallback(showPreviewWidget, "callback", (value) => {
                        console.log("SmartImageLoader: show_preview changed to", value);

                        // Mettre à jour l'état enabled
                        previewWidget.value.enabled = value;

                        if (value) {
                            // Activé : afficher et recharger avec les params ACTUELS
                            previewWidget.value.hidden = false;
                            previewWidget.parentEl.hidden = false;

                            // Recharger l'image avec les params actuels (y compris nouveau path)
                            if (previewWidget.value.params && previewWidget.value.params.filename) {
                                console.log("SmartImageLoader: Reloading with current params:", previewWidget.value.params.filename);
                                previewWidget.updateSource();
                            }
                        } else {
                            // Désactivé : vider la preview visuelle
                            // MAIS garder les params pour quand on réactivera
                            console.log("SmartImageLoader: Clearing visual preview, keeping params");
                            previewWidget.clearPreview();
                        }

                        fitHeight(previewNode);
                    });

                    // Appliquer l'état initial
                    if (showPreviewWidget.value !== undefined) {
                        previewWidget.value.enabled = showPreviewWidget.value;
                        if (!showPreviewWidget.value) {
                            previewWidget.clearPreview();
                        }
                    }
                }

                // CALLBACK SUR img_path pour preview immédiate
                const imgPathWidget = this.widgets.find((w) => w.name === "img_path");

                if (imgPathWidget) {
                    chainCallback(imgPathWidget, "callback", (value) => {
                        console.log("SmartImageLoader: img_path changed to", value);

                        if (!value) {
                            // Vider les params ET la preview
                            previewWidget.value.params = {};
                            previewWidget.clearPreview();
                            return;
                        }

                        // Vérifier l'état du toggle
                        const showPreview = showPreviewWidget ? showPreviewWidget.value : true;
                        console.log("SmartImageLoader: show_preview is", showPreview);

                        // Créer les params (TOUJOURS, même si preview OFF)
                        let params = {
                            filename: value,
                            type: "path",
                            format: "folder"
                        };

                        // Mettre à jour les params (ce qui sera utilisé lors de la réactivation)
                        previewNode.updateParameters(params, showPreview); // force_update seulement si enabled

                        if (!showPreview) {
                            console.log("SmartImageLoader: Preview disabled, params saved but not loading");
                        }
                    });

                    // Déclencher immédiatement si déjà rempli ET show_preview est true
                    if (imgPathWidget.value && showPreviewWidget && showPreviewWidget.value) {
                        imgPathWidget.callback(imgPathWidget.value);
                    }
                }
            });

            // Menu contextuel (comme VHS)
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

                // Le toggle est maintenant géré par le widget show_preview
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
