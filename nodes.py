# Copyright (c) 2026 MinaM
# SPDX-License-Identifier: MIT
"""Text input, display, and literal placeholder replacement nodes."""

import json
import re

from comfy_api.latest import io


MAX_REPLACEMENTS = 16
MAX_CONCAT_INPUTS = 64
MAX_TEXT_REPLACE_PAIRS = 64
JSON_FIELD = re.compile(r"\{\{([^{}\n]*)\}\}")
DELIMITER_ESCAPE = re.compile(
    r"\\(?:[\\nrtfv0]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})"
)


def _decode_delimiter(delimiter):
    """Decode common regular-expression-style escapes without altering Unicode text."""
    escapes = {
        r"\\": "\\", r"\n": "\n", r"\r": "\r", r"\t": "\t",
        r"\f": "\f", r"\v": "\v", r"\0": "\0",
    }

    def replace(match):
        value = match.group(0)
        if value in escapes:
            return escapes[value]
        return chr(int(value[2:], 16))

    return DELIMITER_ESCAPE.sub(replace, str(delimiter))


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


class TextToBool(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="TextEditTextToBool",
            display_name="Text to Bool",
            category="Text Edit",
            inputs=[io.String.Input("text", force_input=True)],
            outputs=[io.Boolean.Output(display_name="bool")],
        )

    @classmethod
    def execute(cls, text):
        return io.NodeOutput(bool(text))


class TextConcatenate(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="TextEditTextConcatenate",
            display_name="Text Concatenate",
            category="Text Edit",
            description="Join connected text inputs with a configurable delimiter.",
            inputs=[
                io.Autogrow.Input(
                    "texts",
                    template=io.Autogrow.TemplateNames(
                        io.String.Input("text"),
                        names=[f"text{index}" for index in range(1, MAX_CONCAT_INPUTS + 1)],
                        min=1,
                    ),
                ),
                io.String.Input("delimiter", multiline=False, dynamic_prompts=False, default=""),
                io.Boolean.Input("clean_whitespace", default=False),
            ],
            outputs=[io.String.Output(display_name="text")],
        )

    @classmethod
    def execute(cls, texts=None, delimiter="", clean_whitespace=False):
        texts = texts or {}
        values = [
            str(texts[name])
            for name in sorted(
                (name for name in texts if re.fullmatch(r"text\d+", name)),
                key=lambda name: int(name[4:]),
            )
            if texts[name] is not None
        ]
        if clean_whitespace:
            values = [re.sub(r"\s+", " ", value).strip() for value in values]
        return io.NodeOutput(_decode_delimiter(delimiter).join(values))


class TextReplace(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        names = []
        for index in range(1, MAX_TEXT_REPLACE_PAIRS + 1):
            names.extend((f"find_word{index}", f"replace_word{index}"))
        return io.Schema(
            node_id="TextEditTextReplace",
            display_name="Text Replace",
            category="Text Edit",
            description="Replace connected search terms in order using literal text matching.",
            inputs=[
                io.String.Input("base", force_input=True),
                io.Autogrow.Input(
                    "words",
                    template=io.Autogrow.TemplateNames(
                        io.String.Input("word"), names=names, min=2,
                    ),
                ),
            ],
            outputs=[io.String.Output(display_name="text")],
        )

    @classmethod
    def execute(cls, base, words=None):
        words = words or {}
        result = str(base)
        for index in range(1, MAX_TEXT_REPLACE_PAIRS + 1):
            find_word = words.get(f"find_word{index}")
            if find_word is None or str(find_word) == "":
                continue
            replace_word = words.get(f"replace_word{index}", "")
            replacement = "" if replace_word is None else str(replace_word)
            result = result.replace(str(find_word), replacement)
        return io.NodeOutput(result)


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
