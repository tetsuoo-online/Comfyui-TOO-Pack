import { app } from "../../scripts/app.js";

function convertToFormatted(value, unit) {
    let totalSeconds;
    if (unit === "Minutes") {
        totalSeconds = value * 60;
    } else if (unit === "Heures") {
        totalSeconds = value * 3600;
    } else {
        totalSeconds = value;
    }

    const rounded = Math.round(totalSeconds);
    const h = Math.floor(rounded / 3600);
    const m = Math.floor((rounded % 3600) / 60);
    const s = rounded % 60;

    const pad = (n) => String(n).padStart(2, "0");

    if (h > 0) return `${pad(h)}h${pad(m)}m${pad(s)}s`;
    if (m > 0) return `${pad(m)}m${pad(s)}s`;
    return `${pad(s)}s`;
}

app.registerExtension({
    name: "TOO.TimeConverter",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "TOOTimeConverter") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated?.apply(this, arguments);

            // Add display widget after standard widgets are created
            const displayWidget = this.addWidget(
                "button",
                "result_display",
                "",
                () => {},
                {}
            );

            displayWidget.serialize = false;

            displayWidget.computeSize = function (width) {
                return [width, 30];
            };

            displayWidget.draw = function (ctx, node, widget_width, y, H) {
                const valueWidget = node.widgets?.find(w => w.name === "value");
                const unitWidget  = node.widgets?.find(w => w.name === "unit");

                const value = parseFloat(valueWidget?.value ?? 0);
                const unit  = unitWidget?.value ?? "Secondes";

                const formatted = isNaN(value) ? "—" : convertToFormatted(value, unit);

                // Background
                const radius = 6;
                ctx.beginPath();
                ctx.roundRect
                    ? ctx.roundRect(16, y + 8, widget_width - 32, H - 4, radius)
                    : ctx.rect(16, y + 2, widget_width - 32, H - 4);
                ctx.fillStyle = "#1a1a2e";
                ctx.fill();

                // Border
                ctx.strokeStyle = "#4a9eff44";
                ctx.lineWidth = 1;
                ctx.stroke();

                // Result text
                ctx.fillStyle = "#4af0a0";
                ctx.font = "bold 18px monospace";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(formatted, widget_width / 2, y + H / 2+7.5);
                ctx.textAlign = "left";
                ctx.textBaseline = "alphabetic";
            };

            // Hook value widget callback for live update
            const hookWidgets = () => {
                const valueWidget = this.widgets?.find(w => w.name === "value");
                const unitWidget  = this.widgets?.find(w => w.name === "unit");

                const refresh = () => this.setDirtyCanvas(true, false);

                if (valueWidget) {
                    const orig = valueWidget.callback;
                    valueWidget.callback = function (...args) {
                        orig?.apply(this, args);
                        refresh();
                    };
                }

                if (unitWidget) {
                    const orig = unitWidget.callback;
                    unitWidget.callback = function (...args) {
                        orig?.apply(this, args);
                        refresh();
                    };
                }
            };

            // Widgets may not all exist yet at onNodeCreated time
            setTimeout(hookWidgets, 0);

            return r;
        };
    },
});
