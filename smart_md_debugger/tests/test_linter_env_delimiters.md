# Linter Test: Environment Delimiters

This file tests `\begin{...}` and `\end{...}` environment pairings.

## Correct Usage
\begin{itemize}
  \item One
  \item Two
\end{itemize}

\begin{align*}
  a &= b \\
  c &= d
\end{align*}

Nested:
\begin{theorem}
  Statement.
  \begin{proof}
    Proof details.
  \end{proof}
\end{theorem}

## Unclosed Environments
Unclosed itemize:
\begin{itemize}
  \item A

Unclosed align:
\begin{align}
  x=1

## Mismatched \end Tags
Mismatched 1:
\begin{equation}
  y = mx+c
\end{itemize}

Mismatched 2 (nested):
\begin{outerA}
  \begin{innerA}
    Content
  \end{outerA}
\end{innerA}

## Unmatched \end (no corresponding \begin)
Orphaned end:
\end{document}

\end{foo}
