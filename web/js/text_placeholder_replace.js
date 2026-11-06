import { app } from "../../../scripts/app.js";

const NODE_NAME = "TextEditPlaceholderReplace";
const MAX_INPUTS = 16;

function replacementNumber(input) {
    const match = /^text(\d+)$/.exec(input?.name || "");
    return match ? Number(match[1]) : null;
}

function syncReplacementInputs(node) {
    const countWidget = node.widgets?.find(widget => widget.name === "input_count");
    if (!countWidget) return;
    const count = Math.max(1, Math.min(MAX_INPUTS, Math.trunc(Number(countWidget.value) || 1)));

    for (let index = (node.inputs?.length || 0) - 1; index >= 0; index--) {
        const number = replacementNumber(node.inputs[index]);
        if (number !== null && number > count) node.removeInput(index);
    }
    const existing = new Set((node.inputs || []).map(replacementNumber).filter(Number.isFinite));
    for (let index = 1; index <= count; index++) {
        if (!existing.has(index)) {
            node.addInput(`text${index}`, "STRING", { shape: 7, optional: true });
        }
    }
    const minimum = node.computeSize();
    node.setSize([Math.max(node.size[0], minimum[0], 360), Math.max(node.size[1], minimum[1])]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "TextEdit.PlaceholderReplace",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_NAME) return;

        const created = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = created?.apply(this, arguments);
            const countWidget = this.widgets?.find(widget => widget.name === "input_count");
            if (countWidget && !countWidget.textEditDynamicInputs) {
                const callback = countWidget.callback;
                countWidget.callback = value => {
                    callback?.call(countWidget, value);
                    countWidget.value = Math.max(1, Math.min(MAX_INPUTS, Math.trunc(Number(value) || 1)));
                    syncReplacementInputs(this);
                };
                countWidget.textEditDynamicInputs = true;
            }
            requestAnimationFrame(() => syncReplacementInputs(this));
            return result;
        };

        const configured = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = configured?.apply(this, arguments);
            requestAnimationFrame(() => syncReplacementInputs(this));
            return result;
        };
    },
});
