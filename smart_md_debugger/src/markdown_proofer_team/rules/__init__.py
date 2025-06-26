# Initializes the rules package for the Markdown Proofer.
# This package will contain individual linting rule modules.

from .text_character_validation import RULES as text_character_validation_rules
from .math_validation import RULES as math_validation_rules

# Combine all rules from different modules if necessary
ALL_RULES = []
ALL_RULES.extend(text_character_validation_rules)
ALL_RULES.extend(math_validation_rules)

# Each rule module should define functions that take tokens, lines, and an error callback.
