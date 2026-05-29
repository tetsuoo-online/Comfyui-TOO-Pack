import { app } from "../../scripts/app.js";

app.registerExtension({
  name: "Comfy.LoraGrid",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "LoRA Grid") return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onNodeCreated?.apply(this, arguments);
      this.picker_collapsed = true;
      this.buildPickerUI();
      return r;
    };

    // ── Widget picker ─────────────────────────────────────────────

    nodeType.prototype.startPicking = function (targetWidget) {
      const self = this;
      const canvas = app.canvas;
      const graph = app.graph;
      const originalCursor = document.body.style.cursor;
      document.body.style.cursor = "default";

      const overlay = document.createElement("div");
      overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:transparent;z-index:9997;pointer-events:none;";
      const instruction = document.createElement("div");
      instruction.style.cssText = "position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#4a9eff;color:#fff;padding:12px 24px;border-radius:40px;font-size:16px;font-weight:bold;box-shadow:0 4px 12px rgba(0,0,0,.3);z-index:9999;pointer-events:none;border:2px solid #fff;";
      instruction.textContent = "Click a node to pick a widget [ESC = cancel]";
      const crosshair = document.createElement("div");
      crosshair.style.cssText = "position:fixed;width:40px;height:40px;border-radius:50%;background:rgba(74,158,255,.2);border:2px solid #4a9eff;transform:translate(-50%,-50%);pointer-events:none;z-index:9998;";
      document.body.append(overlay, instruction, crosshair);

      let mouseX = 0, mouseY = 0;
      const onMove = (e) => { mouseX = e.clientX; mouseY = e.clientY; };
      const tick = () => {
        if (crosshair.parentNode) {
          crosshair.style.left = mouseX + "px";
          crosshair.style.top  = mouseY + "px";
          requestAnimationFrame(tick);
        }
      };
      document.addEventListener("mousemove", onMove);
      requestAnimationFrame(tick);

      const cleanup = () => {
        document.body.style.cursor = originalCursor;
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("keydown", onEsc);
        canvas.canvas.removeEventListener("click", onClick, true);
        [overlay, instruction, crosshair].forEach(el => el.parentNode?.removeChild(el));
      };

      const onClick = (e) => {
        if (e.button !== 0) return;
        e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
        const rect = canvas.canvas.getBoundingClientRect();
        const gx = (e.clientX - rect.left) / canvas.ds.scale - canvas.ds.offset[0];
        const gy = (e.clientY - rect.top)  / canvas.ds.scale - canvas.ds.offset[1];
        const nodes = (app.canvas.graph?._nodes) || graph._nodes || [];
        let found = null;
        for (let i = nodes.length - 1; i >= 0; i--) {
          const n = nodes[i];
          if (!n) continue;
          if (gx >= n.pos[0] && gx <= n.pos[0] + n.size[0] &&
              gy >= n.pos[1] && gy <= n.pos[1] + n.size[1]) { found = n; break; }
        }
        if (found && found.id !== self.id) {
          const sel = (found.widgets || []).filter(w =>
            w.type !== "button" && w.name &&
            !w.name.startsWith("▶") && !w.name.startsWith("▼"));
          if (sel.length) { cleanup(); self.showWidgetSelector(found, sel, targetWidget); return; }
        }
        cleanup();
      };

      const onEsc = (e) => { if (e.key === "Escape") cleanup(); };
      document.addEventListener("keydown", onEsc);
      setTimeout(() => canvas.canvas.addEventListener("click", onClick, true), 100);
    };

    nodeType.prototype.showWidgetSelector = function (sourceNode, widgets, targetWidget) {
      const bgOverlay = document.createElement("div");
      bgOverlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9999;";
      const popup = document.createElement("div");
      popup.style.cssText = "position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);background:#2a2a2a;border:2px solid #555;border-radius:8px;padding:20px;z-index:10000;min-width:300px;max-width:500px;max-height:600px;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,.5);";
      const title = document.createElement("div");
      title.textContent = `Pick widget from: ${sourceNode.title || sourceNode.type}`;
      title.style.cssText = "color:#fff;font-size:16px;font-weight:bold;margin-bottom:15px;border-bottom:1px solid #555;padding-bottom:10px;";
      popup.appendChild(title);
      const close = () => {
        bgOverlay.parentNode?.removeChild(bgOverlay);
        popup.parentNode?.removeChild(popup);
      };
      bgOverlay.onclick = close;
      widgets.forEach(w => {
        const item = document.createElement("div");
        item.textContent = `${w.name} (${w.type})`;
        item.style.cssText = "padding:10px;margin:5px 0;background:#3a3a3a;color:#fff;cursor:pointer;border-radius:4px;";
        item.onmouseover = () => item.style.background = "#4a4a4a";
        item.onmouseout  = () => item.style.background = "#3a3a3a";
        item.onclick = () => {
          targetWidget.value = w.value ?? "";
          if (targetWidget.inputEl) targetWidget.inputEl.value = targetWidget.value;
          if (targetWidget.callback) targetWidget.callback(targetWidget.value);
          this.setDirtyCanvas(true, true);
          close();
        };
        popup.appendChild(item);
      });
      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = "Cancel";
      cancelBtn.style.cssText = "margin-top:15px;padding:8px 20px;background:#555;color:#fff;border:none;border-radius:4px;cursor:pointer;width:100%;";
      cancelBtn.onclick = close;
      popup.appendChild(cancelBtn);
      document.body.append(bgOverlay, popup);
    };

    // ── UI Picker ─────────────────────────────────────────────────

    nodeType.prototype.buildPickerUI = function () {
      this.widgets = (this.widgets || []).filter(w => !w._loraCustom);

      const self = this;
      const add = (w) => { w._loraCustom = true; this.widgets.push(w); return w; };

      const arrow = self.picker_collapsed ? "▶" : "▼";
      add({
        name: `${arrow} LORA PICKER`, type: "button",
        computeSize: (w) => [w, 22],
        draw(ctx, node, widget_width, y, H) {
          ctx.fillStyle = "rgba(0,0,0,0.12)"; ctx.fillRect(0, y, widget_width, H);
          ctx.fillStyle = "#ffffff"; ctx.font = "bold 12px Arial";
          ctx.fillText(this.name, 6, y + H * 0.7);
        },
        callback: () => {
          self.picker_collapsed = !self.picker_collapsed;
          self.buildPickerUI();
          self.setDirtyCanvas(true, true);
        }
      });

      if (self.picker_collapsed) {
        const newSize = this.computeSize();
        this.setSize([Math.max((this.size || [300])[0], newSize[0], 300), newSize[1]]);
        return;
      }

      const pathW = add({
        name: "lora_path", type: "string", value: "",
        computeSize: (w) => [w, 20],
        callback: (v) => { pathW.value = v; }
      });

      add({
        name: "pick_lora", type: "button", serialize: false,
        computeSize: (w) => [w, 20],
        draw(ctx, node, widget_width, y, H) {
          ctx.fillStyle = "rgba(68,138,255,0.1)"; ctx.fillRect(2, y+1, widget_width-4, H-2);
          ctx.fillStyle = "#4a9eff"; ctx.font = "11px Arial"; ctx.textAlign = "center";
          ctx.fillText("🔗 Pick Widget", widget_width*0.5, y+H*0.65);
          ctx.textAlign = "left";
        },
        callback: () => self.startPicking(pathW)
      });

      const newSize = this.computeSize();
      this.setSize([Math.max((this.size || [300])[0], newSize[0], 300), newSize[1]]);
    };

    // ── Serialisation ─────────────────────────────────────────────

    nodeType.prototype.onSerialize = function (o) {
      o.picker_collapsed = this.picker_collapsed;
    };

    nodeType.prototype.onConfigure = function (o) {
      if (o.picker_collapsed !== undefined) this.picker_collapsed = o.picker_collapsed;
      this.buildPickerUI();
    };

  },
});
