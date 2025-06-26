# Linter Test: Clean File

This file should pass all current linter checks without any warnings.

## Text and Basic Markdown
This is a paragraph with some **bold** and _italic_ text.
It also includes `inline_code`.

A list:
- Item 1
- Item 2
  - Sub-item 2.1

```
A code block.
No LaTeX commands here that should be misinterpreted.
```

## Correct LaTeX Math
Inline math: $x = a+b$.
Display math:
\[ \sum_{i=0}^{n} x_i = x_0 + x_1 + \dots + x_n \]
Parenthesis math: \( y = \alpha + \beta \).
Double dollar math:
$$ \mathcal{L} = \int L(q, \dot{q}, t) dt $$
Escaped dollar: This costs \$10. No math here.
Escaped parenthesis: This is not math \\( text \\).
Escaped bracket: Nor is this \\\[ text \\].

## Correct LaTeX Environments
\begin{itemize}
  \item Item A
  \item Item B
\end{itemize}

\begin{equation} \label{eq:example}
E = mc^2
\end{equation}

Nested environments:
\begin{enumerate}
  \item First item.
    \begin{itemize}
      \item Sub-bullet.
    \end{itemize}
  \item Second item.
\end{enumerate}

## Correct LaTeX Commands
$\sqrt{x}$
$\sqrt{x_1}$
$\sqrt{x^{2}}$
$\textbf{Bold Text}$
$\textit{Italic Text}$
$\emph{Emphasized Text}$
$x_{ab}$
$y^{cd}$
$z_{a_b}$
$w^{c^d}$
$\frac{a}{b}$
$\frac{10}{200}$
$\alpha_{ij}$
$\beta^{kl}$
$\Gamma_x^y$
This is text with a literal backslash \ and that's fine.
This has a backslash before space: \ then text.
