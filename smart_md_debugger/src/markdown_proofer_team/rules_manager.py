from typing import List, Callable, Any, Tuple

# LinterError format: (line_number: int, error_type: str, message: str, suggestion: str | None)
LinterError = Tuple[int, str, str, str | None]
# RuleFunction format: takes tokens, lines, and an error callback function
RuleFunction = Callable[[List[Any], List[str], Callable[..., None]], None]

class RulesManager:
    def __init__(self):
        """
        Manages the registration and application of linting rules.
        """
        self.rules: List[RuleFunction] = []

    def clear_rules(self):
        """Clears all registered rules."""
        self.rules = []
        # print("INFO: All rules cleared from RulesManager.") # Optional: for debugging tests

    def add_rule(self, rule_function: RuleFunction):
        """
        Adds a linting rule function to the manager.
        A rule function should accept:
        - tokens: The list of tokens from markdown-it-py.
        - lines: The list of lines from the original Markdown content.
        - error_callback: A function to call to report an error.
        """
        if not callable(rule_function):
            raise ValueError("Provided rule is not a callable function.")
        self.rules.append(rule_function)
        print(f"INFO: Rule '{getattr(rule_function, '__name__', 'anonymous_rule')}' added.")


    def apply_rules(self, tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
        """
        Applies all registered rules to the given tokens and lines.

        Args:
            tokens: List of tokens from markdown-it-py.
            lines: List of lines from the original Markdown content.
            error_callback: Function to be called by rules to report errors.
                          Expected signature: error_callback(line_number, error_type, message, suggestion, token=None, line_content="")
        """
        if not self.rules:
            print("WARN: No rules registered in RulesManager. No checks will be performed.")
            return

        print(f"DEBUG: RulesManager.apply_rules: Applying {len(self.rules)} rules. Tokens: {tokens}") # DEBUG

        for i, rule_func in enumerate(self.rules):
            print(f"DEBUG: RulesManager.apply_rules: Applying rule {i+1}/{len(self.rules)}: {getattr(rule_func, '__name__', 'anonymous_rule')}") # DEBUG
            try:
                rule_func(tokens, lines, error_callback)
            except Exception as e:
                # Report an error if a rule crashes, but continue with other rules.
                rule_name = getattr(rule_func, '__name__', 'anonymous_rule')
                error_callback(
                    line_number=0, # Or try to determine a relevant line if possible
                    error_type="RULE_EXECUTION_ERROR",
                    message=f"Error executing rule '{rule_name}': {e}",
                    suggestion="This indicates an issue with the linter's internal rule logic. Please report this."
                )
                print(f"ERROR: Exception in rule '{rule_name}': {e}")


if __name__ == '__main__':
    # Example of how RulesManager might be used (conceptual)

    # Dummy error callback for testing
    def dummy_error_reporter(line_number, error_type, message, suggestion, token=None, line_content=""):
        print(f"Error reported: L{line_number} - {error_type} - {message} - Suggestion: {suggestion}")

    # Dummy rule function
    def sample_rule_find_TODO(tokens, lines, error_callback):
        for i, line_content in enumerate(lines):
            if "TODO" in line_content:
                error_callback(
                    line_number=i + 1,
                    error_type="FOUND_TODO",
                    message="Found 'TODO' in line.",
                    suggestion="Address the TODO item.",
                    line_content=line_content
                )

    def sample_rule_check_token_text(tokens, lines, error_callback):
        for token in tokens:
            if token.type == "text" and "specific_text" in token.content:
                 error_callback(
                    line_number=token.map[0]+1 if token.map else 0,
                    error_type="FOUND_SPECIFIC_TEXT",
                    message=f"Found 'specific_text' in token: {token.content}",
                    suggestion="Review this text.",
                    token=token
                )

    manager = RulesManager()
    manager.add_rule(sample_rule_find_TODO)
    manager.add_rule(sample_rule_check_token_text)

    # Dummy data for applying rules
    dummy_tokens = [
        type('Token', (), {'type': 'text', 'content': 'This is a specific_text example.', 'map': [0,1]})(),
        type('Token', (), {'type': 'softbreak', 'map': [0,1]})(),
        type('Token', (), {'type': 'text', 'content': 'Another line with TODO here.', 'map': [1,2]})()
    ]
    dummy_lines = [
        "This is a specific_text example.",
        "Another line with TODO here."
    ]

    print("\n--- Applying rules ---")
    manager.apply_rules(dummy_tokens, dummy_lines, dummy_error_reporter)
    print("\nRulesManager basic setup seems functional.")
