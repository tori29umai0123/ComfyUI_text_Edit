# Copyright (c) 2026 MinaM
# SPDX-License-Identifier: MIT
"""Text input, display, and literal placeholder replacement nodes."""

import json
import re

from comfy_api.latest import io


MAX_REPLACEMENTS = 16
JSON_FIELD = re.compile(r"\{\{([^{}\n]*)\}\}")


class TextInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"text": ("STRING", {
            "multiline": True,
            "dynamicPrompts": False,
            "default": "",
        })}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"
    CATEGORY = "Text Edit"
    DESCRIPTION = "Enter literal text without dynamic prompt expansion."

    def run(self, text=""):
        return (text,)


class TextDisplay:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"text": ("STRING", {"forceInput": True})}}

    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "Text Edit"
    OUTPUT_NODE = True
    DESCRIPTION = "Display incoming text or JSON without modifying it."

    def run(self, text):
        return {"ui": {"text": [str(text)]}, "result": ()}


class TextPlaceholderReplace:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_text": ("STRING", {"forceInput": True}),
                "input_count": ("INT", {"default": 1, "min": 1,
                                         "max": MAX_REPLACEMENTS, "step": 1}),
            },
            "optional": {
                f"text{index}": ("STRING", {"forceInput": True})
                for index in range(1, MAX_REPLACEMENTS + 1)
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"
    CATEGORY = "Text Edit"
    DESCRIPTION = "Replace literal [text1], [text2], ... placeholders with connected text."

    def run(self, base_text, input_count=1, **replacements):
        result = str(base_text)
        count = max(1, min(MAX_REPLACEMENTS, int(input_count)))
        for index in range(1, count + 1):
            name = f"text{index}"
            if name in replacements and replacements[name] is not None:
                result = result.replace(f"[{name}]", str(replacements[name]))
        return (result,)


class JsonPromptTemplate(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="TextEditJsonPromptTemplate",
            display_name="JSON Prompt Template",
            category="Text Edit",
            inputs=[
                io.String.Input("json_text", multiline=True, dynamic_prompts=False, force_input=True),
                io.String.Input("template", multiline=True, dynamic_prompts=False, default=""),
            ],
            outputs=[io.String.Output(display_name="text")],
        )

    @classmethod
    def execute(cls, json_text, template):
        fenced = re.fullmatch(r"\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n```[ \t]*\s*", json_text,
                              re.DOTALL | re.IGNORECASE)
        if fenced:
            json_text = fenced.group(1)
        boxed = re.fullmatch(r"\s*<\|begin_of_box\|>\s*(.*?)\s*<\|end_of_box\|>\s*", json_text,
                             re.DOTALL)
        if boxed:
            json_text = boxed.group(1)
        data = json.loads(json_text)
        if not template:
            return io.NodeOutput(json.dumps(data, ensure_ascii=False, indent=2))

        def replace(match):
            path = match.group(1).strip()
            parts = path.split("/")[1:] if path.startswith("/") else [path] if path else []
            value = data
            for part in parts:
                part = part.replace("~1", "/").replace("~0", "~")
                try:
                    value = value[int(part)] if isinstance(value, list) else value[part]
                except (KeyError, IndexError, TypeError, ValueError) as error:
                    raise ValueError(f"JSON field not found: {path}") from error
            return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)

        return io.NodeOutput(JSON_FIELD.sub(replace, template))
