console.log("🔥 TOO-Pack category icon loader");

function replaceCategoryWithIcon() {
    // toutes les entrées du menu Add Node
    const categoryLabels = document.querySelectorAll(".litegraph .menu-entry");

    categoryLabels.forEach(label => {
        if (label.innerText?.startsWith("TOO-Pack")) {
            // évite double injection
            if (label.dataset.tooIconApplied) return;
            label.dataset.tooIconApplied = "true";

            // nettoie le texte
            label.innerHTML = "";

            // crée l’icône
            const img = document.createElement("img");
            img.src = "/extensions/Comfyui-TOO-Pack/icons/TOO-Pack.png";
            img.style.width = "18px";
            img.style.height = "18px";
            img.style.marginRight = "6px";
            img.style.verticalAlign = "middle";

            // texte optionnel
            const span = document.createElement("span");
            span.innerText = "TOO-Pack";

            label.appendChild(img);
            label.appendChild(span);
        }
    });
}

// ComfyUI recrée le menu souvent → polling
setInterval(replaceCategoryWithIcon, 500);
