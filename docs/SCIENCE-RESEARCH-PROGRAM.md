# Tim Dooley / Potato of Life — Science Research Program

**Updated:** 2026-09-09

This document turns the accumulated science work into a research programme rather than a loose collection of analogies.

## Rule zero

Every item belongs to one of five classes:

1. primary/project-attested Tim material;
2. conversation-developed Timic formalism;
3. later archive formalization;
4. established external mathematics/physics;
5. unresolved primary target.

External physics can strengthen vocabulary, identify mathematical structure, expose mistakes, or suggest tests. It does not independently verify Potatoverse theology.

---

## I. The central research object

The mature formal object is

```math
\mathfrak P=(\mathcal S,g,A,\mathcal D,\mathcal O,\mathcal I).
```

The working interpretation is:

- `S`: possible configurations / states / descriptions;
- `g`: geometry, metric or relational structure;
- `A`: Axis flow;
- `D`: Door transitions;
- `O`: observables;
- `I`: information / integration.

Recovered descendants include

```math
\partial_tX=F(X,g),
```

```math
\partial_sX=A(X,g),
```

```math
P=R\otimes B,
```

```math
H=R\cap B,
```

```math
D:X_{in}\rightarrow X_{out},
```

```math
X_{n+1}=F_{\lambda_n}(X_n),
```

```math
P(\omega)\propto e^{-\beta S(\omega)},
```

and

```math
\chi>0\Rightarrow\text{integration},
\qquad
\chi<0\Rightarrow\text{fragmentation}.
```

Several of these still require exact first-source recovery.

---

# II. Axis programme

Axis currently has at least five mathematically different candidates.

## Axis as vector field

```math
\frac{dX}{ds}=A(X).
```

## Axis as flow

```math
\Phi_{s+t}=\Phi_s\circ\Phi_t.
```

## Axis as fixed-point organizer

```math
A(X_*)=0.
```

## Axis as symmetry generator

```math
\mathcal L_\xi g=0.
```

## Axis as scale flow

```math
\frac{dg_i}{d\ln\mu}=\beta_i(g).
```

These are not automatically one thing.

### Required next object: invariant registry

For every claimed Axis transformation `T`, record

```text
Inv[T] = {quantities preserved by T}
```

Possible examples include orientation, graph connectivity, probability normalization, topological charge, causal ordering or role/function.

If nothing is invariant, the word **Axis** may be functioning only metaphorically on that layer.

---

# III. Door programme

A Door should be represented as more than a poetic threshold.

Define a Door contract:

```text
D = (
  input domain,
  guard / activation condition,
  transition map,
  output domain,
  preserved invariants,
  cost / dissipation,
  reversibility class
)
```

A hybrid-system version is

```math
G_k=\{X:h_k(X)=0\},
```

followed by

```math
X^+=D_k(X^-).
```

This should be tested against:

- phase boundaries;
- domain walls;
- event horizons;
- quantum channels;
- open-system interfaces;
- category-theoretic cospans;
- biological membranes;
- political/legal borders;
- project symbolic Door.

The differences matter as much as the similarities.

---

# IV. Spiral programme

The archive should no longer use **Spiral** as one undifferentiated word.

## Geometry

```math
r=a+b\theta
```

and

```math
r=r_0e^{b\theta}.
```

## Helical level change

```math
x=r\cos\theta,\quad
y=r\sin\theta,\quad
z=h\theta.
```

## Return maps

```math
x_{n+1}=P(x_n).
```

## Local spiral flow

Complex eigenvalues

```math
\lambda=\alpha\pm i\omega
```

produce rotation with growth or decay.

## Hopf transition

```math
\dot z=(\mu+i\omega)z-|z|^2z.
```

## Scale recurrence

RG limit cycles can obey

```math
g(\ln\mu+T)=g(\ln\mu).
```

This is a particularly important comparator because it expresses recurrence after changing scale.

### Required next object: return signature

Every project Return should be classified as

```text
R = (
  endpoint return,
  state return,
  phase return,
  topology return,
  scale return
)
```

A closed geometric loop may still carry different phase or holonomy.

---

# V. Closed-path memory

Three mathematical structures are especially useful.

## Berry phase

```math
\gamma=\oint A_B\cdot dR.
```

## Wilson loop

```math
W(C)=\operatorname{Tr}\,\mathcal P
\exp\left(i\oint_C A\right).
```

## Chern number

```math
C=\frac1{2\pi}\int_M\Omega.
```

Together they provide rigorous examples in which path, connection and global topology matter even when naive endpoint geometry looks unchanged.

This is a serious mathematical neighbor for **return is not reset**.

---

# VI. Local ↔ global programme

The spin/topology research already reached the Dirac operator.

```math
D=\gamma^i\nabla_i.
```

Its index is schematically

```math
\operatorname{index}(D)
=
\dim\ker D_+
-
\dim\ker D_-.
```

The Atiyah–Singer theorem links analytical data of elliptic operators to global topology.

The archive should therefore develop a precise local↔global vocabulary:

```text
local rule
→ differential operator
→ allowed modes
→ global invariant
→ consistency condition
```

This is much more rigorous than using “everything is connected” as an explanatory endpoint.

---

# VII. Standard Model completion programme

The archive already contains

```math
SU(3)_C\times SU(2)_L\times U(1)_Y
```

and

```math
Q=T_3+Y.
```

It also records one-generation chiral representations and anomaly-cancellation checks.

The next missing layer is **basis mixing**.

## CKM

```math
d'_i=(V_{CKM})_{ij}d_j.
```

## PMNS

```math
\nu_\alpha
=
\sum_iU_{\alpha i}\nu_i.
```

Oscillation phases involve

```math
\frac{\Delta m_{ij}^2L}{4E}.
```

This adds an important concept to Timic comparison:

> an interaction basis and a propagation basis can both be valid while not being identical.

This should be used as a disciplined basis-change analogy, not as spiritual proof.

---

# VIII. Chern–Simons / braid programme

A major unfinished branch is

```math
S_{CS}
=
\frac{k}{4\pi}
\int
\operatorname{Tr}
\left(A\wedge dA+\frac23A\wedge A\wedge A\right).
```

This connects naturally with

- knot invariants;
- Wilson loops;
- braid groups;
- anyons;
- topological quantum computation;
- boundaries.

The archive's existing sequence

```text
trajectory → topology → braid → quantum statistics
```

should be extended into a full topological-field-theory branch.

---

# IX. 11D programme

The symbolic 11D Potato must be distinguished from real eleven-dimensional theory.

The physical comparison has

```math
G_4=dC_3
```

and a schematic action

```math
S_{11}
\sim
\int\sqrt{-g}\left(R-\frac{1}{2\cdot4!}G_4^2\right)
-
\int C_3\wedge G_4\wedge G_4
+\cdots.
```

The research programme should separate:

```text
5D Kaluza-Klein        5 = 4 + 1
10D strings / CY3     10 = 4 + 6
11D M-theory / G2     11 = 4 + 7
```

Then add:

- M2 branes;
- M5 branes;
- wrapped cycles;
- calibrated geometry;
- flux compactification;
- moduli;
- effective potentials;
- Basu–Harvey / brane intersections.

The purpose is not to make everything a brane. It is to learn the real mathematics of extended objects and boundaries before drawing comparisons.

---

# X. Sun programme

The Sun is no longer only a symbolic upper circle.

## Stellar equilibrium

```math
\frac{dP}{dr}=-\frac{Gm(r)\rho(r)}{r^2},
```

```math
\frac{dm}{dr}=4\pi r^2\rho.
```

## Parker spiral

```math
B_r\propto r^{-2},
```

```math
\frac{B_\phi}{B_r}
\approx
-\frac{\Omega r\sin\theta}{v_{sw}}.
```

## Dynamo waves

```math
\mathbf s
=
\alpha\nabla\Omega\times\hat e_\phi.
```

A commonly discussed sign condition for equatorward migration is

```math
\alpha\frac{\partial\Omega}{\partial r}<0
```

under the associated assumptions.

This creates a legitimate scientific cluster:

```text
Sun
→ rotation
→ Axis
→ differential rotation
→ magnetic induction
→ polarity
→ wave
→ outward wind
→ spiral
```

This is one of the strongest external physics neighborhoods around Tim's Sun/Axis/Spiral material.

---

# XI. Celestial-orientation programme

Tim's thought archive includes North / Sirius / Dog Star / Axis material.

The science archive should create a standard celestial audit tuple:

```text
C = (
  object,
  epoch,
  RA,
  Dec,
  observer latitude/longitude,
  date/time,
  azimuth,
  altitude,
  proper motion,
  source
)
```

This makes statements such as “point to Sirius” testable as geometry rather than leaving them ambiguous.

Sirius itself is a nearby binary system with Sirius A and white-dwarf Sirius B. It is not the north celestial pole.

---

# XII. Precession programme

The ~26,000-year Eye motif has a real astronomical comparator.

```math
\Omega_p\approx\frac{2\pi}{T_p},
```

with Earth's axial precession period roughly 25.8 kyr.

The conceptual lesson is stronger than the number:

> an Axis can preserve its structural role while its orientation changes slowly through time.

This gives the archive a possible distinction between **Axis identity** and **Axis pointing direction**.

---

# XIII. Time-symmetry programme

The old advanced/retarded vocabulary must be recovered first.

External comparison families are:

### Wheeler–Feynman

```math
\Box G_{ret}=\delta,
\qquad
\Box G_{adv}=\delta.
```

### Two-State Vector Formalism

```math
i\partial_t|\psi\rangle=H|\psi\rangle,
```

```math
-i\partial_t\langle\phi|
=\langle\phi|H.
```

### Schwinger–Keldysh

Forward and backward branches of a closed time contour used in non-equilibrium quantum theory.

### Transactional interpretation

Offer/confirmation-wave interpretation influenced by advanced/retarded mathematics.

None should be declared the source of Red/Blue until an actual Tim primary source is found.

---

# XIV. Field of Life programme

The 2024 book stratum already used Field of Life language.

If retained as metaphor, no additional physics claim is required.

If promoted as physics, the minimum object is something like

```math
\mathcal L[\phi]
=\frac12\partial_\mu\phi\partial^\mu\phi
-\frac12m^2\phi^2
-V(\phi)
+\mathcal L_{coupling}.
```

Then specify:

- field type;
- domain;
- units;
- symmetry;
- coupling;
- equation of motion;
- source;
- detector/observable;
- prediction differing from known physics.

The same rule applies to Starchforce.

---

# XV. Archive architecture

The Science wing should be treated as four nested layers:

```text
PRIMARY ARCHAEOLOGY
    ↓
RECOVERED TIM FORMALISMS
    ↓
EXTERNAL MATHEMATICAL NEIGHBORS
    ↓
TESTABLE ARCHIVE EXTENSIONS
```

The canonical science root is:

`knowledge/science/science-master-index.json`

The strongest current recovery records include:

- `great-book-2024-science-archaeology.json`
- `axis-11d-sun-spiral-time-symmetry-recovery.json`
- `quantum-atom-particle-recovery.json`
- `missed-hard-science-strata.json`
- `equation-ledger.json`
- `equation-ledger-wave-002.json`

The main external-strengthening files include:

- `deeper-physics-connections.json`
- `contextual-strengthening-atlas.json`
- `advanced-physics-expansion-wave-003.json`
- `quantum-standard-model-astronomy-atlas.json`

---

# XVI. Most important unresolved originals

1. Exact April 21, 2025 Spiral Equation.
2. Earliest Tim Axis equation.
3. Original `P=R⊗B` source.
4. Original `H=R∩B` source.
5. Definition of `χ`.
6. Original Red/Blue advanced-retarded mapping.
7. Any Tim Wheeler–Feynman / Aharonov / Cramer reference.
8. Original qutrit/qubit Door model.
9. 11D Potato coordinate meaning.
10. 115,000-mile torus calculation.
11. Sun-face geometry.
12. Sirius pointing geometry.
13. Precession Eye calculation.
14. Starchforce action/coupling.
15. 100,000-hour Spiral scaling relation.

Those are not blanks to fill imaginatively. They are archaeological targets.

---

# XVII. New research principle

The project should evaluate every deep analogy with the sequence

```text
ORIGINAL TIM STATEMENT
→ exact date/source
→ minimal formal object
→ mathematical family
→ strongest external theory
→ precise similarity
→ precise difference
→ missing variables
→ falsifier / counterexample
→ revised model
```

That sequence is how the archive becomes larger **and** more reliable at the same time.
