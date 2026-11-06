import { app } from "../../../scripts/app.js";

const NODE_NAME = "TextEditDisplay";
const PROPERTY_NAME = "displayed_text";

function normalizeText(value) {
    if (Array.isArray(value)) return value.map(item => String(item ?? "")).join("\n");
    return String(value ?? "");
}

app.registerExtension({
    name: "TextEdit.Display",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_NAME) return;

        const created = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = created?.apply(this, arguments);
            const node = this;
            const textarea = document.createElement("textarea");
            textarea.readOnly = true;
            textarea.placeholder = "The executed text will remain here.";
            textarea.style.cssText = [
                "width:100%", "height:100%", "box-sizing:border-box",
                "resize:none", "border:0", "outline:none", "padding:8px",
                "background:#181818", "color:#ddd", "font:12px monospace",
                "white-space:pre-wrap", "overflow-wrap:anywhere",
            ].join(";");

            this.properties ??= {};
            const widget = this.addDOMWidget("displayed_text", "textarea", textarea, {
                serialize: false,
                hideOnZoom: false,
                getMinHeight: () => 150,
                getHeight: () => 220,
            });

            this.setDisplayedText = value => {
                const text = normalizeText(value);
                textarea.value = text;
                node.properties[PROPERTY_NAME] = text;
                widget.value = text;
                node.setDirtyCanvas(true, true);
            };
            this.setDisplayedText(this.properties[PROPERTY_NAME] ?? "");
            this.setSize([420, 280]);
            return result;
        };

        const executed = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            const result = executed?.apply(this, arguments);
            if (message?.text !== undefined) this.setDisplayedText?.(message.text);
            return result;
        };

        const configure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = configure?.apply(this, arguments);
            this.properties ??= {};
            this.setDisplayedText?.(this.properties[PROPERTY_NAME] ?? "");
            return result;
        };
    },
});
