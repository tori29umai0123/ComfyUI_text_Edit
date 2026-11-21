import { app } from "../../../scripts/app.js";

const NODE_NAME = "TextEditTextReplace";
const MAX_PAIRS = 64;

function pairInfo(input) {
    const match = /^(?:words\.)?(find_word|replace_word)(\d+)$/.exec(input?.name || "");
    return match ? { kind: match[1], number: Number(match[2]) } : null;
}

function syncReplaceInputs(node) {
    const connectedFinds = (node.inputs || [])
        .map(input => ({ input, info: pairInfo(input) }))
        .filter(({ input, info }) => info?.kind === "find_word"
            && input.link !== null && input.link !== undefined)
        .map(({ info }) => info.number);
    const wantedPairs = Math.min(
        MAX_PAIRS,
        Math.max(1, ...connectedFinds.map(number => number + 1)),
    );

    for (let index = (node.inputs?.length || 0) - 1; index >= 0; index--) {
        const info = pairInfo(node.inputs[index]);
        if (!info) continue;
        const canonicalName = `words.${info.kind}${info.number}`;
        if (info.number > wantedPairs || node.inputs[index].name !== canonicalName) {
            node.removeInput(index);
        }
    }

    const existing = new Set((node.inputs || []).map(input => input.name));
    for (let number = 1; number <= wantedPairs; number++) {
        for (const kind of ["find_word", "replace_word"]) {
            const label = `${kind}${number}`;
            const name = `words.${label}`;
            if (!existing.has(name)) {
                node.addInput(name, "STRING", { shape: 7, optional: true, label });
                existing.add(name);
            }
        }
    }

    const minimum = node.computeSize();
    node.setSize([Math.max(node.size[0], minimum[0], 360), Math.max(node.size[1], minimum[1])]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "TextEdit.TextReplace",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_NAME) return;

        const created = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = created?.apply(this, arguments);
            requestAnimationFrame(() => syncReplaceInputs(this));
            return result;
        };

        const configured = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = configured?.apply(this, arguments);
            requestAnimationFrame(() => syncReplaceInputs(this));
            return result;
        };

        const connectionsChanged = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function () {
            const result = connectionsChanged?.apply(this, arguments);
            requestAnimationFrame(() => syncReplaceInputs(this));
            return result;
        };
    },
});
