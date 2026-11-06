# ComfyUI_text_Edit

[日本語](README.ja.md) | English

A small, standalone set of text nodes for ComfyUI, extracted from ComfyUISAM3DPose. It requires no model downloads or additional Python packages.

## Installation

1. Download and extract the release ZIP.
2. Put the `ComfyUI_text_Edit` folder directly under `ComfyUI/custom_nodes/` so that `ComfyUI/custom_nodes/ComfyUI_text_Edit/__init__.py` exists.
3. Restart ComfyUI. Find the nodes under **Text Edit**.

Do not place the ZIP itself in `custom_nodes`, or nest the folder inside another `ComfyUI_text_Edit` folder.

## Nodes

| Node | What it does |
| --- | --- |
| **Text Input** | Outputs the multiline text you type. Dynamic prompt expansion is disabled, so brackets and other special characters remain literal. |
| **Text Display** | Shows the incoming string in a read-only area after execution. The displayed text is saved with the workflow. |
| **Text Placeholder Replace** | Replaces literal `[text1]` through `[text16]` in `base_text` with connected strings. Set `input_count` to show the corresponding input sockets. An unconnected placeholder stays unchanged; an empty connected string removes it. |
| **JSON Prompt Template** | Inserts JSON values into a multiline template. Use `{{subject}}` for a top-level key, or `{{/person/name}}` and `{{/items/0}}` for nested values. An empty template outputs indented JSON. |

For example, with `base_text` set to `Hello, [text1]!` and `text1` connected to `world`, **Text Placeholder Replace** outputs `Hello, world!`.

Load [workflows/json_to_edit_prompt.json](workflows/json_to_edit_prompt.json) in ComfyUI for an example that turns the sample `subject`/`outfit`/`composition` JSON into a structured edit prompt. Edit the template to match other JSON schemas. Missing fields raise an error showing the field path; strings are inserted as plain text and other JSON values use JSON notation.

JSON input may be plain text or enclosed in a ` ```json ` code fence. The fence is ignored before parsing.

## Compatibility

The nodes use their own IDs (`TextEditInput`, `TextEditDisplay`, `TextEditPlaceholderReplace`, and `TextEditJsonPromptTemplate`). You can install this package alongside ComfyUISAM3DPose. Workflows containing the original `SAM3DPoseto...` node IDs still need ComfyUISAM3DPose; this package does not automatically replace those IDs.

## Verification and license

Run `python -B tests/test_nodes.py` from this folder using ComfyUI's Python environment to check the Python node behavior. The frontend scripts live in `web/js/` and are loaded by ComfyUI when it starts. Licensed under the [MIT License](LICENSE).
