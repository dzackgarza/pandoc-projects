# Linter Test: Common LaTeX Command Issues

This file tests for issues like double scripts and missing braces.

## Double Scripts - Expect Warnings
$x_a_b$
$y^c^d$
$z__1$
$M^\alpha^\beta$
$N_{ij}_{kl}$
$P^{ab}^{cd}$

## Double Scripts - Correct Usage (No Warnings Expected)
$x_{a_b}$
$y^{c^d}$
$x_{a_{b}}$
$y^{c^{d}}$
$M_{\alpha\beta}$
$N^{ijk}$
$P_{longsubscript}$
$Q^{longsuperscript}$
$R_a^{b_c}$ (mixed is fine by this check)

## Missing Braces for Commands - Expect Warnings
$\sqrt xy$
$\sqrt \alpha_1$
$\sqrt 100$
$\textbf long text$
$\textit two words$
$\texttt code phrase$
$\mathbf math symbols$
$\emph emphasized text$

## Missing Braces for Commands - Correct Usage (No Warnings Expected)
$\sqrt x$
$\sqrt{\alpha_1}$
$\sqrt{100}$
$\textbf{A}$
$\textbf{long text in braces}$
$\textit{i}$
$\textit{italic phrase in braces}$
$\texttt{code}$
$\mathbf{M}$
$\emph{emphasized}$
$\emph{word}$
$\sqrt{x_y}$
$\sqrt{\frac{a}{b}}$

## Specific \frac checks (currently disabled in linter, for future)
% $\frac 12$ % Should warn -> \frac{1}{2}
% $\frac ab$ % Fine
% $\frac{a}{b}$ % Fine
% $\frac \alpha\beta$ % Should warn -> \frac{\alpha}{\beta}
% $\frac{long}{short}$ % Should warn
