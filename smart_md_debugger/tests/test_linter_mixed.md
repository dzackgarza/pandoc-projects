# Linter Test: Mixed Issues

This file contains a mix of various linting errors.

## Backtick Issues
This is `` `\badmacro` ``. And here is `\another_one_x_y`.

## Math Delimiter Issues
An unclosed dollar $ sign.
Mismatched paren \( a+b ].
An extra display closer: $$
Unclosed display: \[ \sum_i x_i

## Environment Issues
\begin{foo}
  This environment is not closed.
And this one has a mismatched end:
\begin{align}
  x=1
\end{equation}

## Command Issues
$f_x_y$ is a double subscript.
$\sqrt longarg$ needs braces.
$\textbf text here$ also.

## Combination
`\begin{array}` $x_1_1$ \( \textit unbraced text \)
\begin{itemize}
  \item $ unclosed item
\end{array}
$y^a^b$
`\sqrt{abc}` (backticked but content is fine)
