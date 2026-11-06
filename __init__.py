"""Standalone text nodes for ComfyUI."""

from .nodes import TextInput, TextDisplay, TextPlaceholderReplace, JsonPromptTemplate

NODE_CLASS_MAPPINGS = {
    "TextEditInput": TextInput,
    "TextEditDisplay": TextDisplay,
    "TextEditPlaceholderReplace": TextPlaceholderReplace,
    "TextEditJsonPromptTemplate": JsonPromptTemplate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextEditInput": "Text Input",
    "TextEditDisplay": "Text Display",
    "TextEditPlaceholderReplace": "Text Placeholder Replace",
    "TextEditJsonPromptTemplate": "JSON Prompt Template",
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
