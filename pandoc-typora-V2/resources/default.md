# Markdown Torture Test (Pandoc Flavored)

This document tests various Markdown features, with an emphasis on Pandoc's extensions.

## 1. Headers
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6

## 2. Paragraphs and Line Breaks

This is a normal paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
This line should be part of the same paragraph.

This line should be a new paragraph (after a blank line).

Line with
two spaces at the end for a hard line break.

## 3. Emphasis

*This text will be italic*
_This will also be italic_

**This text will be bold**
__This will also be bold__

***This text will be bold and italic***
___This will also be bold and italic___

~~This text will be strikethrough.~~

## 4. Blockquotes

> This is a blockquote.
> It can span multiple lines.
> > And can be nested.
> Back to the first level.

## 5. Lists

### Unordered Lists
* Item 1
* Item 2
  * Sub-item 2.1
  * Sub-item 2.2
    * Sub-sub-item 2.2.1
+ Item 3 (using +)
- Item 4 (using -)

### Ordered Lists
1. First item
2. Second item
   1. Nested ordered item
   2. Another nested item
3. Third item
   * Unordered sub-list.
99. An item with a specific number.

### Definition Lists (Pandoc Extension)
Term 1
: Definition 1
: Definition 1a

Term 2
: Definition 2 with a [link](http://example.com).
: And multiple lines.

## 6. Code Blocks

### Inline Code
This is `inline code`. Variable is `my_var_123`.

### Fenced Code Blocks (Pandoc)
```
This is a simple fenced code block.
No language specified.
```

```python
# This is a Python code block
def greet(name):
  print(f"Hello, {name}!")

greet("World")
```

```javascript
// This is a JavaScript code block
function sum(a, b) {
  return a + b;
}
console.log(sum(5, 10));
```

### Indented Code Blocks (Traditional Markdown)
    // This is an indented code block
    // (requires 4 spaces or 1 tab)
    for (i = 0; i < 5; i++) {
      console.log(i);
    }

## 7. Horizontal Rules

---
***
___

(Three or more hyphens, asterisks, or underscores)

## 8. Links

[This is an inline link to Example.com](http://example.com "Link title!")
[This link has no title](http://example.org)
<http://example.net> (Autolink)

Reference-style links:
[I'm a reference-style link][Arbitrary case-insensitive reference text]
[You can use numbers for reference-style link definitions][1]
Or leave it empty and use the [link text itself].

[Arbitrary case-insensitive reference text]: https://www.mozilla.org
[1]: http://slashdot.org
[link text itself]: http://www.reddit.com

## 9. Images

![Alt text for an image](https://via.placeholder.com/150/0000FF/808080?Text=BlueSquare "Optional title")

Reference-style image:
![alt text][logo]

[logo]: https://via.placeholder.com/100/FF0000/FFFFFF?Text=RedCircle "Red Circle Logo"

## 10. Tables (Pandoc Extension)

Simple table:

  Right     Left     Center     Default
-------     ------ ----------   -------
     12     12        12            12
    123     123       123          123
      1     1          1             1

Table with headers:

| Header 1 | Header 2 | Header 3 |
| :------- | :------: | -------: |
| Align L  | Center   | Align R  |
| Cell 1   | Cell 2   | Cell 3   |
| Long cell content that wraps | More | And more |

Pipe table:
| Fruit    | Price | Quantity |
|----------|-------|----------|
| Apple    | $1    | 5        |
| Orange   | $2    | 10       |

## 11. Footnotes (Pandoc Extension)

Here's a statement with a footnote.[^1] And another one.[^onemore]

[^1]: This is the first footnote. It can contain multiple paragraphs.

    And indented blocks.
[^onemore]: This is the second footnote.

Inline footnotes: ^[This is an inline footnote, which is concise.]

## 12. Fenced Divs and Spans (Pandoc Extension)

::: warning
This is a **warning** div. It should be stylable.
It can contain other Markdown elements like lists:
* Item A
* Item B
:::

This is a normal paragraph with a [special span]{.highlight style="color:red;"} inside it.

::: {.custom-class #custom-id key="value"}
This div has a custom class, ID, and attributes.
:::

## 13. Math (Pandoc Extension - requires MathJax/KaTeX in HTML)

Inline math: $E = mc^2$. The equation is $\sum_{i=1}^{n} x_i = y$.

Display math:
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$

```{.latex .numberLines startFrom="10"}
\begin{equation}
    x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \label{eq:quadratic}
\end{equation}
```
We can refer to equation \@eq:quadratic.

## 14. Raw HTML/TeX (Pandoc allows this)

<!-- HTML Comment -->
This is <font color="blue">blue text</font> using raw HTML.

```=html
<div style="border: 1px solid green; padding: 10px;">
  This is a raw HTML block.
</div>
```

```=latex
\textbf{This is raw LaTeX bold text.}
```

## 15. Special Characters & Escaping

Asterisks: \*literal asterisks\*
Backslashes: \\
Backticks: \`
Underscores: \_

## 16. Line Blocks (Pandoc Extension)

| Line blocks are useful for poetry or addresses.
| Each line begins with a pipe.
|   Indentation is preserved.
|     And can be significant.

## 17. Task Lists (Common Extension, Pandoc may need filter/specific syntax)

- [x] Completed task
- [ ] Incomplete task
- [ ] Another task
  - [x] Sub-task completed
  - [ ] Sub-task pending

## 18. Emoji (May require Pandoc filter or specific Unicode handling)

:smile: :book: :rocket: (This depends on Pandoc setup and output format)

## 19. Strikethrough with tildes
~~This is strikethrough text using two tildes.~~

## 20. Subscript and Superscript (Pandoc Extension)
H~2~O is water.
2^10^ is 1024.

## 21. Non-breaking space
This sentence has a non-breaking\ space. (This is a Pandoc feature when outputting to LaTeX/PDF, may not be visible in HTML preview directly from Markdown source but good to test parsing)

---
End of Torture Test
---
