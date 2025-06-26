# Linter Test: Math Delimiters

This file tests various math delimiter scenarios.

## Correct Usage
$a+b=c$
\(x^2 - y^2\)
\[ \int_0^1 f(x) dx \]
$$ \oint E \cdot dA = \frac{Q_{enc}}{\epsilon_0} $$
$ dollar opener \( paren opener \) paren closer $ dollar closer
$ dollar opener \[ bracket opener \] bracket closer $ dollar closer
Escaped: \$100 and an escaped \\( and an escaped \\) and \\\[ and \\\] and \\\$\$

## Unclosed Delimiters
Unclosed dollar: $x+y
Unclosed parenthesis: \(z-1
Unclosed bracket: \[ \alpha \beta
Unclosed double dollar: $$ \gamma \delta

## Mismatched Delimiters
Mismatched 1: $x+y\)
Mismatched 2: \(x+y]$
Mismatched 3: \[x+y)$
Mismatched 4: $$x+y$

## Unmatched Closers (should be caught by stack logic or specific error)
Extra closer 1: x + y $
Extra closer 2: x + y \)
Extra closer 3: x + y \]
Extra closer 4: x + y $$

## Suspicious Mixing (these might be aggressive flags)
Mixed 1: $ \text{text} \( \text{math} \) \text{text} $
Mixed 2: \( \text{text} $ \text{math} $ \text{text} \)
Mixed 3: \[ \text{text} $ \text{math} $ \text{text} \]
Mixed 4: $$ \text{text} \( \text{math} \) \text{text} $$
Mixed 5: $ \alpha \[ \beta \] \gamma $
Mixed 6: \( \delta $$ \epsilon $$ \zeta \)
