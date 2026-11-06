import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1]))
spec = importlib.util.spec_from_file_location(
    "text_edit", ROOT / "__init__.py", submodule_search_locations=[str(ROOT)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TextNodesTests(unittest.TestCase):
    def test_registration_and_input(self):
        nodes = module.NODE_CLASS_MAPPINGS
        self.assertEqual(set(nodes), {
            "TextEditInput", "TextEditDisplay", "TextEditPlaceholderReplace",
            "TextEditJsonPromptTemplate"})
        self.assertEqual(nodes["TextEditInput"]().run("日本語\n[abc]"), ("日本語\n[abc]",))
        self.assertFalse(nodes["TextEditInput"].INPUT_TYPES()
                         ["required"]["text"][1]["dynamicPrompts"])

    def test_display(self):
        result = module.NODE_CLASS_MAPPINGS["TextEditDisplay"]().run("a\nb")
        self.assertEqual(result["ui"]["text"], ["a\nb"])
        self.assertEqual(result["result"], ())

    def test_placeholder_replacement(self):
        node = module.NODE_CLASS_MAPPINGS["TextEditPlaceholderReplace"]()
        self.assertEqual(node.run("A[text1]B[text2]", 2, text1="x"),
                         ("AxB[text2]",))
        self.assertEqual(node.run("A[text1]B", 1, text1=""), ("AB",))

    def test_json_prompt_template(self):
        node = module.NODE_CLASS_MAPPINGS["TextEditJsonPromptTemplate"]
        source = '{"subject":"pink hair","details":{"outfit":"red tunic"},"items":["first",2],"active":true}'
        template = "subject: {{subject}}\noutfit: {{/details/outfit}}\nitem: {{/items/0}}\nactive: {{/active}}"
        self.assertEqual(node.execute(source, template)[0],
                         "subject: pink hair\noutfit: red tunic\nitem: first\nactive: true")
        self.assertIn('"subject": "pink hair"', node.execute(source, "")[0])
        with self.assertRaisesRegex(ValueError, "JSON field not found: /missing"):
            node.execute(source, "{{/missing}}")

    def test_json_prompt_template_ignores_code_fence(self):
        node = module.NODE_CLASS_MAPPINGS["TextEditJsonPromptTemplate"]
        source = '{"subject":"pink hair","appearance":"pink dress"}'
        self.assertEqual(node.execute("```json\n" + source + "\n```", "{{appearance}}")[0],
                         "pink dress")
        self.assertEqual(node.execute("  ```JSON\r\n" + source + "\r\n```  ", "{{subject}}")[0],
                         "pink hair")
        self.assertEqual(node.execute("```\n" + source + "\n```", "{{subject}}")[0],
                         "pink hair")

    def test_json_prompt_template_ignores_glm_box(self):
        node = module.NODE_CLASS_MAPPINGS["TextEditJsonPromptTemplate"]
        source = '{"subject":"white hair","appearance":"black jacket"}'
        boxed = "<|begin_of_box|>" + source + "<|end_of_box|>"
        self.assertEqual(node.execute(boxed, "{{subject}}")[0], "white hair")
        self.assertEqual(json.loads(node.execute(" \n" + boxed + " \n", "")[0]), json.loads(source))

    def test_sample_workflow(self):
        workflow = json.loads((ROOT / "workflows" / "json_to_edit_prompt.json").read_text(encoding="utf-8"))
        source, template, display = workflow["nodes"]
        self.assertEqual([node["type"] for node in workflow["nodes"]],
                         ["TextEditInput", "TextEditJsonPromptTemplate", "TextEditDisplay"])
        self.assertEqual(workflow["links"],
                         [[1, source["id"], 0, template["id"], 0, "STRING"],
                          [2, template["id"], 0, display["id"], 0, "STRING"]])
        output = module.NODE_CLASS_MAPPINGS["TextEditJsonPromptTemplate"].execute(
            source["widgets_values"][0], template["widgets_values"][0])[0]
        self.assertIn("subject_definitions:", output)
        self.assertIn("short, spiky pink hair", output)
        self.assertIn("non_diegetic_music:\nN/A", output)


if __name__ == "__main__":
    unittest.main()
