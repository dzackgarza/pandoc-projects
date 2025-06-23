import yaml
import json

with open("environments.yaml") as f:
    data = yaml.safe_load(f)

envs = data["environments"]
regex_template = data["environment_regex"]
block_body = data.get("block_body")

# Generate Grammar
patterns = []
for env in envs:
    patterns.append({
        "name": f"meta.fenced.div.{env['name']}.markdown",
        "begin": regex_template.replace("%ENV%", env["name"]),
        "end": "^:::$"
    })

grammar = {
    "scopeName": "dzg.pandoc.injection",
    "injectionSelector": "L:text.html.markdown",
    "patterns": patterns
}

with open("syntaxes/dzg-pandoc-injection.json", "w") as f:
    json.dump(grammar, f, indent=2)

# Generate Theme
tokenColors = []
for env in envs:
    tokenColors.append({
        "scope": f"meta.fenced.div.{env['name']}.markdown",
        "settings": {
            "foreground": env["color"],
            "fontStyle": "bold"
        }
    })

if block_body:
    tokenColors.append({
        "scope": block_body["scope"],
        "settings": {
            "background": block_body["background"]
        }
    })

theme = {
    "name": "Test Pandoc Highlight",
    "type": "dark",
    "colors": {},
    "tokenColors": tokenColors
}

with open("themes/test-color-theme.json", "w") as f:
    json.dump(theme, f, indent=2)

print("Generated syntaxes/dzg-pandoc-injection.json and themes/test-color-theme.json")

