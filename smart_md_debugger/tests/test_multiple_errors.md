# Multiple Errors Test

This document contains several errors.

First error: \undefinedLaTeXcommandHere

Some valid text in between.

Second error:
\begin{verbatim} % This is fine
Some verbatim text.
\end{verbatim}

\begin{tikzpicture} % TikZ might not be available or configured
  \draw (0,0) circle (1cm);
% \end{tikzpicture} % Let's make this an unclosed environment too for a second error point

Valid text after the TikZ attempt.

Another error: An invalid character sequence for PDF: �

Final piece of text.
