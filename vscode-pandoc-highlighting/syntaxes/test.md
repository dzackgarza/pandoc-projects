## Bilinear/Quadratic Modules and Lattices

From here onward, $L$ will be a projective (hence free) $\ZZ$-module of finite rank $n$.

::: {.definition title="Bilinear modules/forms"} Let $L$ be a $\ZZ$-module. A **bilinear form**
$\beta$ on $L$ is a morphism

\begin{align*} \beta \in \Hom*\ZZ( L \tensor*\ZZ L, &\ZZ) v\tensor w &\mapsto \beta(v, w)
,\end{align*}

which can be regarded as an element of
$\Sym^2_\ZZ(L\dual) \subseteq L\dual \tensor_\ZZ L\dual \cong (L\tensor_\ZZ L)\dual$, the subspace
of symmetric 2-tensors. We often omit $\beta$ from the notation and simply write $vw$ or $v\cdot w$
for $\beta(v, w)$. We refer to a general pair $(L, \beta)$ as a **bilinear $\ZZ$-module**.

More generally, we may allow bilinear forms to be $\QQ$-valued, in which case we say $\beta$ is
**integral** if its image $\beta(L, L)$ is contained in $\ZZ$. :::

::: {.definition title="Symmetric/skew-symmetric bilinear forms"} A bilinear form
$\beta: L\tensor_\ZZ L\to \QQ$ is **$\eps$-symmetric** for $\varepsilon \in \QQ$ if \[ \beta(a, b) =
\eps \beta(b, a). \]

1. If $\eps = 1$, we say $\beta$ is **symmetric**.
2. If $\eps = -1$ we say $\beta$ is **skew-symmetric**.
3. $\beta$ is **alternating** if $\beta(a,a) = 0$ for all $a\in L$.

We note that over $\ZZ$, (1) and (3) are equivalent. :::

::: remark Note that any bilinear form $\omega$ gives rise to a symmetric form defined by
$\beta \da {1\over 2}(\omega^t + \omega)$, where $\omega^t(a,b) \da \omega(b,a)$. If $\omega$ is
skew-symmetric, then the associated symmetric form is zero. :::

::: {.definition title="Quadratic modules/forms"} A **quadratic form** on $L$ is a morphism of sets
$q: L\to \QQ$ such tha

- $q(\lambda . v) = \lambda^2 .q(v)\in \QQ$ for all $v\in L$ and all $\lambda \in \QQ$, and
- Its **polar form**

    \begin{align*} \beta*q: L \tensor*\ZZ L &\to \QQ (v, w) &\mapsto \beta_q(v,w)\da q(v + w) -
    q(v) - q(w) \end{align*}

    is a symmetric bilinear form on $L$.

We similarly say $q$ is **integral** if $q(L) \subseteq \ZZ$, and refer to the pair $(L, q)$ as a
**quadratic $\ZZ$-module**. :::

::: remark :::

::: {.definition title="Lattices"} A **lattice** is a pair $(L, \beta)$ where $L$ is a free
$\ZZ$-module of finite rank and $\beta$ is a (possibly $\QQ$-valued) nondegenerate symmetric
bilinear form. We often require $\beta$ to be integral, bu occasionally also refer to modules with
$\QQ$-valued forms as lattices by abuse of language.

Similarly, we refer to a pair $(L, q)$ as a **quadratic lattice** if $q$ is a nondegenerate
quadratic form, again possibly $\QQ$-valued, which is often required to be integral. :::

::: {.definition title="Even/odd lattices"} If $(L,\beta)$ is a lattice, we say $L$ is **even** if
$\beta(v,v) \in 2\ZZ$ for all $v\in L$, and is **odd** otherwise. :::

::: {.lemma title="Correspondence between bilinear and quadratic forms"} We write $\Bil_\ZZ(L)$ for
the set of **all** (not necessarily symmetric) bilinear forms on a fixed $\ZZ$-module $L$, and
$\Sym\Bil_\ZZ(L)$ for the *symmetric* bilinear forms on $L$. Analogously, we write $\Quad_\ZZ(L)$ or
simply $\Quad_\ZZ(L)$ for the set of all quadratic forms on $L$, and make similar definitions over
$\QQ$.

Note that every $\QQ$-valued bilinear module $(L, \beta)$ (no necessarily symmetric) determines a
$\QQ$-valued quadratic module $(L, q_\beta)$

\begin{align*} q*\beta: L &\to \QQ v &\mapsto q*\beta(v) \da \beta(v,v) ,\end{align*}

which only depends on the symmetric part of $\beta$, given by ${1\over 2}(\beta^t + \beta)$.
Conversely, every $\QQ$-valued quadratic module $(L, q)$ determines a *symmetric* module
$(L, \beta_q)$ where

\begin{align*} \beta*q: L\tensor*\ZZ L &\to \QQ v \tensor w &\mapsto \beta_q(v) \da q(v + w) -
q(v) - q(w) \end{align*}

is the polar form of $q$. These associations define maps

\begin{align*} \Bil*\QQ(L) &\to \Quad*\QQ(L) \to \Sym\Bil*\QQ(L) \subseteq \Bil*\QQ(L) \beta
&\mapsto q\_\beta &\qquad\qquad\qquad\qquad q \mapsto \beta_q .\end{align*}

It is a well-known fact of linear algebra that the map $\beta\mapsto q_\beta$ is surjective, and
thus every $\QQ$-valued quadratic form $q$ can be written as the quadratic form $\beta(v,v)$
associated to a bilinear form $\beta$, while the lift of $q$ to $\beta$ need not be unique. Upon
restriction to *symmetric* bilinear forms, however, this becomes a bijection, and this is a fact
which generalizes to fields of characteristic $p\neq 2$. Integrally, the situation is more
challenging, but we obtain a similar bijection after a further restriction to *even* forms: :::

::: lemma Let $\Sym\Bil^{\mathrm{ev}}_\ZZ(L)$ be the subspace of **even** $\ZZ$-valued symmetric
bilinear forms on a fixed $\ZZ$-module $L$, and $\Quad_\ZZ(L)$ the space of quadratic forms. Then
there is a bijection

\begin{align*} \Sym\Bil^{\mathrm{ev}}*\ZZ(L) &\mapstofrom \Quad*\ZZ(L) \beta &\mapsto {1\over
2}q\_\beta \beta_q &\mapsfrom q \end{align*}

In other words, the polar form of every integral symmetric form is even, and every *even* symmetric
integral form $\beta$ is the polar form of an integral quadratic form, namely
$q(v) \da {1\over 2}\beta(v,v)$. Moreover, if $q$ is any quadratic form, then ${1\over 2}\beta_q$
uniquely recovers $q$. :::

::: proof Note that for any integral $q$, the polar form is always even: \[ \beta_q(v,v) \da
q(v+v) - q(v) - q(v) = 4q(v)-2q(v) = 2q(v) \in 2\ZZ . \]

Moreover, if $\beta$ is even, then ${1\over 2}q_\beta$ is integral, so both maps are well-defined.

We first consider the composite
$\beta \mapsto {1\over 2}q_\beta \mapsto \beta_{{1\over 2} q_\beta}$:

\begin{align*} \beta*{{1\over 2}q*\beta}(v, w) &\da {1\over 2}q*{\beta}(v+w) - {1\over
2}q*{\beta}(v) - {1\over 2}q\_{\beta}(w) &= {1\over 2} \qty{\beta(v,v) + \beta(v,w) + \beta(w, v) +
\beta(w,w) - \beta(v,v) - \beta(w,w)} &= {1\over 2}\qty{\beta(v,w) + \beta(w, v) } &= \beta(v, w)
\end{align*}

We then consider the composite $q\mapsto \beta_{q} \mapsto {1\over 2}q_{\beta_q}$;

\begin{align*} {1\over 2}q\_{\beta_q}(v) &\da {1\over 2}\beta_q(v,v) &\da {1\over 2}\qty{ q(v + v) -
q(v) - q(v) } &= {1\over 2}\qty{ q(2v) - 2q(v) } &= {1\over 2}\qty{ 4q(v) - 2q(v) } &= {1\over
2}\qty{ 2q(v)} &= q(v) \end{align*}

Thus these maps are mutually inverse. :::

::: remark It is worth noting that some sources instead use the correspondence
$\beta \mapsto q_\beta$ and $q\mapsto {1\over 2}\beta_q$. Over $\QQ$, this is an equivalent
formulation since $2$ is invertible, but over $\ZZ$ one loses the bijection with even lattices by
using this convention. :::

::: {.definition title="Gram matrices"} Let $(L, \beta)$ be a bilinear module. Choosing a basis
$B_L = (e_i)_{1\leq i\leq n}$, for any $v,w\in L$ one can write $v = \sum_j a_j e_j$ and
$w= \sum_j b_j e_j$ for some coefficients $a_j, b_j \in \ZZ$. Using bilinearity, one can then write

\[ \beta(v, w) = \beta\qty{ \sum*j a_j e_j, \sum_j b_j e_j} = \sum*{i, j} a*i b_j \cdot \beta(e_i,
e_j) \da v^t G*\beta w \]

for some (not necessarily unique) matrix
$G_\beta \da (\beta(e_i, e_j))_{i,j} \in \Mat_{n\times n}(\QQ)$, which we refer to as the **Gram
matrix of $\beta$**.

Similarly, if $(L, q)$ is a quadratic module, one can write

\[ q(v) = q\qty{ \sum*j a_j e_j} = \sum*{i, j} a*i a_j \cdot (G_q)*{i, j} = v^t G_q v \]

for some (not necessarily unique) matrix $G_q \in \Mat_{n\times n}(\QQ)$, which we similarly refer
to as the **Gram matrix of $q$**. Writing the associated bilinear form of $q$ as
$\beta_q(x,y) = q(x+y) - q(x) - q(y)$, we can take $G_q$ to be the upper triangular matrix:

\[ (G*q)*{i,j} = \begin{cases} q(e_i) & \text{if } i = j \beta_q(e_i, e_j) & \text{if } i < j 0 &
\text{if } i > j \end{cases} \]\]

In other words, $G_q$ is the upper triangular matrix with diagonal entries $q(e_i)$ and upper
triangular entries $\beta_q(e_i, e_j)$ for $i < j$. :::

::: remark Many properties of bilinear forms can be checked at the level of their Gram matrices. For
example,

1. $\beta$ is symmetric if $G_\beta^t = G_\beta$,
2. $\beta$ is skew-symmetric if $G_\beta^t = -G_\beta$, and
3. $\beta$ is alternating if $\diag(G_\beta) = (0, 0,\cdots, 0)$ and $G_\beta^t = -G_\beta$.

Moreover, if $(L, \beta)$ is a lattice, it is even if and only if $G_\beta$ has integral entries and
its diagonal entries are all even. The following are the key properties and conventions we will use:

1. The bilinear form can be recovered as $\beta(v,w) = v^t G_\beta w$.
2. The quadratic form can be recovered as $q(v) = v^t G_q v$.
3. The relation between the two Gram matrices is $G_{\beta_q} = G_q + G_q^t$.
4. For even lattices, $G_\beta$ is integral with even diagonal entries.
5. The Hessian matrix $H(q) = (\frac{\partial^2 q}{\partial x_i \partial x_j})$ satisfies
   $H(q) = 2G_{q,\mathrm{sym} }$ where $G_{q,\mathrm{sym} } = \frac{1}{2}(G_q + G_q^t)$ is the
   symmetric part of $G_q$.

We will typically use the upper triangular form $G_q$ for quadratic forms to ensure integrality and
avoid denominators in calculations. :::

::: example Consider the $\ZZ$-valued quadratic form on $\ZZ^3$ defined by

\[ q(x,y,z) = ax^2 + by^2 + cz^2 + dyz + exz + fxy, \qquad a,\cdots,f\in \ZZ . \]

Using the Hessian, one obtains the symmetric (but non-integral) matrix

\[ G*{q, H} = \frac{1}{2}H(q(x,y,z)) = \begin{pmatrix} a & \frac{1}{2}f & \frac{1}{2}e \frac{1}{2} f
& b & \frac{1}{2}d \frac{1}{2}e & \frac{1}{2}d & c \end{pmatrix} \in \Mat*{3\times 3}(\QQ) , \]

and verify that if $v = \tv{x,y,z}\in \ZZ^3$ then $v^t G_{q, H} v = q(x,y,z)$. However, one can also
take \[ G*q = \begin{pmatrix} a & f & e 0 & b & d 0 & 0 & c \end{pmatrix} \in \Mat*{3\times 3}(\ZZ)
, \]

which is now integral and similarly satisfies $v^t G_{q} v = q(x,y,z)$. One can check directly that
$G_{q, H} = \frac{1}{2}(G_q + G_q^t)$. Letting $\beta_q$ be the polar form of $q$, either of the
above matrices can be used to obtain the (integral) Gram matrix of $\beta_q$:

\[ G*{\beta_q} = \begin{pmatrix} 2a & f & e f & 2b & d e & d & 2c \end{pmatrix} = G*{q, H} + G*{q,
H}^t = G_q + G_q^ \in \Mat*{3\times 3}(\ZZ) . \] :::

::: {.definition title="Orthogonal direct sums"} Let $(L, \beta_L)$ and $(M, \beta_M)$ be integral
lattices. We define their **orthogonal direct sum** as the lattice $(L \oplus M, \beta_{L\oplus M})$
where $L\oplus M$ is their direct sum as $\ZZ$-modules, and the bilinear form is given by

\begin{align*} \beta*L \oplus \beta_M: (L\oplus M)\tensor*\ZZ (L\oplus M) &\to \ZZ (\ell_1 + m_1,
\ell_2 + m_2) &\mapsto \beta_L(\ell_1, \ell_2) + \beta_M(m_1, m_2) .\end{align*}

We write $L^{\oplus n}$ for the $n$-fold direct sum $\bigoplus_{i=1}^n L$.

Similarly, if $(L, q_L)$ and $(M, q_M)$ are integral quadratic lattices, we define their direct sum
as $(L\oplus M, q_L \oplus q_M)$ where

\begin{align*} q_L \oplus q_M: L \oplus M &\to \ZZ \ell + m &\mapsto q_L(\ell) + q_M(m) \end{align*}
:::

::: remark In any fixed basis, the Gram matrix for a direct sum can be realized as the block sum of
the respective Gram matrices, i.e.

\[ G*{\beta_L \oplus \beta_M} = \left[\begin{array}{@{}c|c@{}} G*{\beta*L} & 0 \hline 0 &
G*{\beta*M} \end{array}\right] , \qquad G*{q*L \oplus q_M} = \left[\begin{array}{@{}c|c@{}} G*{q*L}
& 0 \hline 0 & G*{q_M} \end{array}\right] . \]

In particular, this means that if $L = S \oplus T$ can be expressed as a direct sum of lattices,
then $\beta(s, t) = 0$ whenever $s\in S$ and $t\in T$. :::

::: {.definition title="Indecomposable lattices"} Let $(L, \beta)$ be a lattice. We note that since
$L$ is a free $\ZZ$-module, it is always completely decomposable as a $\ZZ$-module into rank one
$\ZZ$-modules. However, if $L$ can not be written as an orthogonal direct sum $L = S \oplus T$ of
*lattices* for two sublattices $S, T\leq L$, we say that the lattice $L$ is **indecomposable**. :::

::: {.example title="Rank 1 and diagonal lattices "} For $a\in \ZZ$ we define $\gens{a}$ to be the
lattice corresponding to the bilinear form $\beta(x, y) = axy$ for $x,y \in \ZZ$, which has a
$1\times 1$ Gram matrix $G_{\gens a} = [a]$. The corresponding quadratic form is $q_\beta(x) = ax^2$
for $x\in \ZZ$, yielding a quadratic lattice that we write as $\sqgens{a}$ which has the Gram matrix
$G_{\beta_q} = [a]$.

More generally, for $a_1, \cdots, a_n\in \ZZ$, we define the "diagonal" lattice
$\gens{a_1, \cdots, a_n} \da \gens{a_1} \oplus \cdots \oplus \gens{a_n}$ which corresponds to the
form

\[ \beta(x, y) = \sum*{i=1}^n a_i x_i y_i \qquad (x,y\in \ZZ^n) , \qquad G*\beta = \begin{pmatrix}
a_1 & & & & a_2 & & & & \ddots & & & & a_n \end{pmatrix} .\]

The corresponding quadratic form is

\[ q*\beta(x) = \sum*{i=1}^n a*i x_i^2 \qquad (x\in \ZZ^n) , \qquad G*{q\_\beta} = \begin{pmatrix}
a_1 & & & & a_2 & & & & \ddots & & & & a_n \end{pmatrix} ,\]

and we write this quadratic lattice as
$\sqgens{a_1, \cdots, a_n} \da \sqgens{a_1} \oplus \cdots \oplus \sqgens{a_n}$. We note that with
our current conventions, the matrices $G_\beta$ and $G_{q_\beta}$ will always coincide. :::

::: {.example title="Rank 2 bilinear and quadratic forms"} For the following examples, let
$L = \ZZ^2$ and fix a standard basis.

1. The map

    \begin{align*} \beta: \ZZ^2 \tensor\_\ZZ \ZZ^2 &\to \ZZ \qty{ \cvec{x_1}{y_1}, \cvec{x_2}{y_2} }
    &\mapsto a x_1 x_2 + b y_1 y_2 \end{align*}

    is a symmetric bilinear form with Gram matrix $G_\beta = \matt a 0 0 b$. It coincides with the
    standard do product when $a=b=1$. The associated lattice $(L, \beta)$ is decomposable and equal
    to $\gens{a, b}$. The associated quadratic form is

    \begin{align*} q\_\beta: \ZZ^2 &\to \ZZ \cvec x y & \mapsto ax^2 + by^2 \end{align*}

    with Gram matrix $G_{q_\beta} = G_\beta$, yielding the quadratic lattice $\gens{a, b}$.

2. The map

    \begin{align*} \beta: \ZZ^2 \tensor\_\ZZ \ZZ^2 &\to \ZZ \qty{ \cvec{x_1}{y_1}, \cvec{x_2}{y_2}}
    &\mapsto x_1 y_2 - x_2 y_1 \end{align*}

    is an alternating, skew-symmetric form with Gram matrix $G_{\beta} = \matt{0}{1}{-1}{0}$. The
    associated symmetric form is defined by $G_\beta^t + G_\beta$, which is the zero matrix, and
    thus the associated (symmetric) lattice and quadratic lattice are both zero.

3. The map

    \begin{align*} q: \ZZ^2 &\to \ZZ \cvec x y &\mapsto ax^2 + bxy + cy^2 \end{align*}

    is a binary quadratic form with possible Gram matrices \[ G*{q, H} = \matt{a}{b\over 2}{b\over
    2}{c} \in \Mat*{2\times 2}(\QQ) , \qquad G*q = \matt{a}{b}{0}{c} \in \Mat*{2\times 2}(\ZZ) . \]

    Its polar form $\beta_q$ has Gram matrix

    \[ G\_{\beta_q} = G_q + G_q^t = \matt{2a}{b}{b}{2c} \]

    and represents the symmetric form

    \begin{align*} \beta*q: \ZZ^2 \tensor*\ZZ \ZZ^2 &\to \ZZ \qty{\cvec{x_1}{y_1}, \cvec{Ax_2}{y_2}
    } &\mapsto 2a x_1 x_2 + bx_2 y_1 + bx_1 y_2 + 2cy_1 y_2 \end{align*}

    The associated lattice $(L, \beta_q)$ is rank 2 and generally indecomposable. \begin{align*}
    \beta*q: \ZZ^2 \tensor*\ZZ \ZZ^2 &\to \ZZ \qty{\cvec{x_1}{y_1}, \cvec{x_2}{y_2} } &\mapsto 2a
    x_1 x_2 + bx_2 y_1 + bx_1 y_2 + 2cy_1 y_2 \end{align*}

        The associated lattice $(L, \beta_q)$ is rank 2
        and generally indecomposable.

    :::

::: {.definition title="Definite forms"} We say a lattice $(L, \beta)$

- **positive definite** if $\beta(v, v) > 0$,
- **positive semidefinite** if $\beta(v, v) \geq 0$,
- **negative definite** if $\beta(v, v) < 0$, or
- **positive semidefinite** if $\beta(v, v) \leq 0$

for all nonzero $v\in L$. We say a lattice is **indefinite** if it is neither positive nor negative
semidefinite. :::

::: {.remark title="Criteria for definiteness"} A symmetric matrix $A \in \Mat_{n\times n}(\QQ)$ is
positive definite if and only if any of the following equivalent conditions hold:

- $A$ can be diagonalized over $\RR$ where each diagonal entry is positive,
- All eigenvalues of $A$ are real and positive, or
- All of the leading principal minors of $A$ are positive.

Similar criteria can be used to check if $A$ is positive semidefinite and negative (semi)definite.
We most often apply these criteria to Gram matrices $A \da G_\beta$ for a lattice $(L, \beta)$ or
$A \da G_{q, H}$ for a quadratic lattice $(L, q)$. :::

::: {.definition title="Extensions of bilinear forms"} Let $(L, \beta)$ be a lattice and let $S$ be
any $\ZZ$-algebra. Then there is naturally a pair $(L_S, \beta_S)$ where $L_S \da L\tensor_\ZZ S$ is
an $S$-module whose bilinear form $\beta_S$ takes values in $\ZZ \tensor_\ZZ S \cong S$. It is
defined by \begin{align*} \beta*S: L_S \tensor_S L_S &\to \ZZ\tensor*\ZZ S = S (v_1 \tensor s_1, v_2
\tensor s_2) &\mapsto \beta(v_1, v_2) \tensor s_1 s_2 = s_1s_2 \cdot \beta(v_1, v_2) \end{align*}
where $s_1s_2$ is the multiplication in $S$. When there is no danger of confusion, we write this as
\[ \beta_S( s_1v_1, s_2 v_2) \da s_1 s_2 \cdot \beta(v_1, v_2) \qquad s_i\in S, v_i\in L .\] The
action of $S$ on $L_S$ is defined by \[ s_1.(v\tensor s_2) \da v\tensor (s_1s_2) .\] We will most
frequently apply this to $S \da \QQ, \RR, \CC, \FF_p$, and $\ZZpadic$. :::

::: {.remark title="On complex extensions"} \label{rmk:complex_extensions_of_bilinear_forms}

Note that over $S=\CC$, the extended lattice $L_\CC$ carries both a **bilinear** extension
$\beta_\CC$ and a **sesquilinear** extension $H_\CC^\beta$. These are defined by

\begin{align*} \beta*\CC: L*\CC \tensor*\CC L*\CC &\to \CC (z*1 \tensor v_1, z_2 \tensor v_2)
&\mapsto z_1z_2 \cdot \beta(v_1, v_2) H^\beta: L*\CC \tensor*\CC L*\CC &\to \CC (z_1 \tensor v_1,
z_2 \tensor v_2) &\mapsto z_1\overline{z_2} \cdot \beta(v_1, v_2) \end{align*}

where we've used the canonical complex conjugation on the complexification $L_\CC$ defined by
$\overline{z\tensor v} \da \overline{z}\tensor v$. These two extensions are related by
$H^\beta(v, w) \da \beta_\CC(v, \overline{w})$ for $v,w\in L_\CC$.

To carry out explicit computations, one can use the decomposition $L_\CC \cong L_\RR + iL_\RR$ to
write every element $v\in L_\CC$ as $v = x + iy$ where $x,y\in L_\RR$ and conjugation acts by
$\bar{x+iy} \da x-iy$. We then have

\begin{align*} \beta*\CC(x_1 + iy_1, x_2 + iy_2) &= \beta*\RR(x*1, x_2) - \beta*\RR(y*1, y_2) +
i\qty{\beta*\RR(y*1, x_2) + \beta*\RR(x*1, y_2)} H*\CC^\beta(x*1 + iy_1, {x_2 + iy_2}) &=
\beta*\RR(x*1, x_2) + \beta*\RR(y*1, y_2) + i\qty{\beta*\RR(y*1, x_2) - \beta*\RR(x_1, y_2)}
\end{align*}

:::
