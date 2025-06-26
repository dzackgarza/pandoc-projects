# Linter Test: Backtick Escaping

This file tests the linter's detection of improperly backticked LaTeX.

## Issues Expected

Should find issue: `\sum`
Should find issue: `\alpha`_i
Should find issue: `\begin{equation}`
Should find issue: `\end{equation}`
This is `\Theta_{ij}^k` and should be flagged.

## No Issues Expected (Correct Usage)

This is inline code: `my_variable = 1;`
This is also fine: `\already_escaped_backslash_in_code`
A single backslash in code: `\`
`\ ` (backslash followed by space in code is fine as code)
Double backticks for code blocks: `` `verbatim` `` (though Pandoc might make this a code block, not inline code with literal double backticks)
`a \ b` (code with space separated backslash)
`verbatim with \ backslash`
`\begin{verbatim}` (This is fine if it's not in backticks)
```latex
\this_is_a_code_block_not_subject_to_inline_backtick_linting
\command
```

A correctly typeset formula: $\sum \alpha \Theta$
Or: \[ \begin{equation} \label{eq:1} \Theta \end{equation} \]
