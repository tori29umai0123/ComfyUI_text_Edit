import { app } from "../../../scripts/app.js";

const NODE_NAME = "TextEditTextConcatenate";
const MAX_INPUTS = 64;

function textNumber(input) {
    const match = /^(?:texts\.)?text(\d+)$/.exec(input?.name || "");
    return match ? Number(match[1]) : null;
}

function syncTextInputs(node) {
    const connected = (node.inputs || [])
        .filter(input => textNumber(input) !== null
            && input.link !== null && input.link !== undefined)
        .map(textNumber);
    const wanted = Math.min(MAX_INPUTS, Math.max(1, ...connected.map(number => number + 1)));

    for (let index = (node.inputs?.length || 0) - 1; index >= 0; index--) {
        const number = textNumber(node.inputs[index]);
        if (number === null) continue;
        if (number > wanted || node.inputs[index].name !== `texts.text${number}`) {
            node.removeInput(index);
        }
    }

    const existing = new Set((node.inputs || []).map(input => input.name));
    for (let number = 1; number <= wanted; number++) {
        const label = `text${number}`;
        const name = `texts.${label}`;
        if (!existing.has(name)) {
            node.addInput(name, "STRING", { shape: 7, optional: true, label });
            existing.add(name);
        }
    }

    const minimum = node.computeSize();
    node.setSize([Math.max(node.size[0], minimum[0], 360), Math.max(node.size[1], minimum[1])]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "TextEdit.TextConcatenate",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_NAME) return;

        const created = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = created?.apply(this, arguments);
            requestAnimationFrame(() => syncTextInputs(this));
            return result;
        };

        const configured = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = configured?.apply(this, arguments);
            requestAnimationFrame(() => syncTextInputs(this));
            return result;
        };

        const connectionsChanged = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function () {
            const result = connectionsChanged?.apply(this, arguments);
            requestAnimationFrame(() => syncTextInputs(this));
            return result;
        };
    },
});
