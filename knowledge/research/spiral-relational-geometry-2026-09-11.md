# Spiral Relational Geometry — Design Research

Updated: 2026-09-11
Status: research/design note; not a canonical empirical claim

## Core idea

A relationship does not have to be rendered as a straight segment. A curve can carry state along its path.

Mathematically, treat a rendered relation as a vector-valued path

`gamma(s) = (x(s), y(s), z(s))`

parameterized by arc length, time, or normalized relation progress. The local tangent

`T(s) = gamma'(s) / ||gamma'(s)||`

is the instantaneous direction of the relation. Curvature measures how strongly the path turns; in 3D, torsion measures how strongly it twists out of plane.

This makes a curve more than decoration: its geometry can encode dynamics.

## Straight line vs curve vs spiral

### Straight line

Use when the only meaning is direct adjacency or net displacement.

Good for:
- simple membership
- binary adjacency
- low-information connections
- precise shortest visual path

### Simple arc / Bezier

Use when the relation needs separation from other edges or one additional visual degree of freedom.

Good for:
- reciprocal edges between the same endpoints
- avoiding overlaps
- direction without implying recurrence
- bundling related routes

### Spiral / helix

Use only when recurrence, cyclical change, growth/decay, convergence/divergence, layered passage, or Axis movement is actually part of the relation.

A useful 3D form is a helix around the straight chord from A to B:

`gamma(t) = A + t(B-A) + r(t)[cos(theta(t))u + sin(theta(t))v]`

where `u` and `v` are perpendicular to the A->B chord.

Interpretation:
- the straight chord = net relation / direct displacement
- the helix = the relation's path through repeated states
- turns = recurrence or cycles
- pitch = progress per cycle
- radius = one chosen variable such as volatility, deviation, or unresolved dispersion
- shrinking radius = convergence / stabilization
- growing radius = divergence / destabilization
- vertical displacement = Axis projection only when justified

Never encode several unrelated meanings into the same radius/pitch/turn count at once.

## Strongest Atlas uses

### D6 Spiral — primary use

This is the most natural home.

Use a spiral when the same relation returns with measurable change:
- debt rollover
- recurring trade cycle
- election cycle
- sanctions/escalation/de-escalation
- repeated negotiations
- seasonal energy exchange
- migration waves
- recurring media/information interaction
- repeated alliance exercises or renewals

One revolution can represent one defined cycle or observation period. The user should be able to inspect the delta per turn.

### Axis transition

A selected edge can wrap around the central Axis while moving between analytical levels.

Examples:
- D4 observable relation -> D5 threshold -> D6 recurrence -> D7 generativity
- D4 -> D3 provenance -> D2 capture where evidence supports descent

The spiral should not mean that a physical object literally travelled upward or downward. It is a view transformation of the relation.

### Convergence and divergence

A logarithmic spiral is especially meaningful because its radius changes continuously with angle and the tangent keeps a constant angle with the radial direction.

Possible visual grammar:
- inward spiral = convergence toward a center/criterion
- outward spiral = dispersion / expanding degrees of freedom
- radius decay rate = speed of convergence
- radius growth rate = speed of divergence

This can support project-symbolic attraction/repulsion while the actual driver remains an observable metric.

### Orbit / capture

D2 Swamp/capture can use a near-circular or low-pitch helix when a relation repeats without meaningful progress.

Potential grammar:
- many turns + low forward progress = recurrence/capture
- shrinking exit radius toward a blocked center = lock-in
- a break or tangent departure = release/exit threshold

Use only where recurrence/exit-friction evidence exists.

### Growth / branching

For D7, a spiral can be used at the trunk or stem before branches split.

Good for:
- successive rounds of capacity building
- compounding knowledge/research collaboration
- growth of a supply network through successive layers
- institutional enlargement across rounds

Do not spiral every branch; reserve spiral geometry for recurrence/growth and use ordinary Tree branching for descendants.

### Time wrapped around relation

Instead of a separate timeline, time can sometimes wrap around a relation path.

Possible mapping:
- angle = time
- forward displacement = net progress/change
- radius = volatility or uncertainty

This is especially useful for one selected relation, not for thousands of simultaneous edges.

### Bilateral flow with recurrence

Trade, payments, migration, or energy flows can use an arc for the current flow and optionally a spiral envelope when showing repeated periods.

Example:
- chord A->B = net annual relation
- turns = months/quarters/years
- segment width = flow magnitude for that period
- local tangent arrow = direction

This becomes a compact history-on-an-edge.

## Curve as vector field

The most important mathematical distinction is that the relationship is not represented by one global vector only.

For a curve `gamma(s)`, the tangent `T(s)` is a vector at every point.

This enables:
- local direction changes
- local speed/rate if parameterized by time
- local curvature as rate of turning
- 3D torsion as twist
- scalar fields attached to the path such as confidence, magnitude, cost, or obligation state

The Atlas can therefore treat a relationship as a path carrying data rather than merely an edge connecting endpoints.

## Edge bundling and curved routing

Graph-visualization research uses curved and bundled edges to reduce clutter and reveal macroscopic connectivity patterns. This suggests a separate non-symbolic use for curves:

- bundle similar routes through shared control points
- keep source/target identities inspectable
- separate parallel relation families visually
- never imply a spiral/cycle when the curve exists only for readability

Important distinction:
- `routing curve` = layout/readability
- `semantic curve` = geometry has data meaning

The UI should expose that distinction.

## Candidate curve vocabulary

### Direct
Straight segment.
Meaning: adjacency/net relation only.

### Arc
Single Bezier/geodesic arc.
Meaning: routed connection, reciprocal separation, or geographic flow.

### Spiral
Planar or near-planar spiral.
Meaning: convergence/divergence, recurrence around a center, growth/decay.

### Helix
3D spiral around a chord or Axis.
Meaning: recurrence plus forward progression or analytical level change.

### Orbit
Closed/near-closed loop.
Meaning: recurrence with low net transformation.

### Bundle
Many related edges sharing a routed corridor.
Meaning: visual/group structure, not necessarily shared causality.

### Branch
Tree split.
Meaning: downstream descendants/capability/output.

## Safe encoding rules

1. Curvature must have one declared meaning per view.
2. Do not infer recurrence merely because a spiral looks good.
3. Do not use clockwise/counterclockwise as good/evil.
4. Arrowheads or tangent flow should still communicate direction explicitly.
5. Keep magnitude, confidence, polarity, and recurrence as separate variables.
6. Avoid dense simultaneous spirals; use semantic curves mainly for selected/inspected relations.
7. Straight-line mode should always remain available for comparison.
8. If curvature is only for collision avoidance or edge bundling, label it as layout rather than meaning.

## Suggested first prototype

Prototype only on one selected relation.

Modes:
- Direct
- Arc
- Spiral history

For `Spiral history`:
- endpoint A and B remain fixed
- centerline/chord remains faintly visible
- turns = count of dated observations or defined cycles
- pitch = normalized net change per observation
- radius = one chosen signal, initially volatility or recurrence intensity
- width = magnitude where units are compatible
- opacity/dash = evidence/visibility class
- tangent arrow particles = direction only when rate semantics exist

This can be implemented without redesigning the whole UI: use the existing selected-edge/Trace context and later add a small curve-mode option inside relation inspection rather than another top-level button.

## Research inspiration

- Logarithmic spiral: constant angle between tangent and radius; useful mathematical analogue for scale-consistent convergence/divergence.
- Bezier curves: practical way to generate curved GeoJSON LineStrings for map rendering.
- Hierarchical edge bundling: curved routing can reduce clutter and reveal high-level connectivity, but bundled geometry should not be mistaken for semantic recurrence.
- Dynamic graph visualization: time-varying edge information can be encoded along edge trajectories; this supports the idea of a relationship path carrying temporal state.

## Recommended interpretation in the Potatoverse Axis

- D2: orbit/capture when recurrence has low progress and exit friction is supported
- D3: roots/provenance can be curved downward but should not automatically spiral
- D4: default direct/arc factual connection
- D5: a kink, gate, break, or crossing can represent a threshold more clearly than a spiral
- D6: canonical Spiral layer
- D7: spiral stem feeding Tree branches when growth is iterative
- D8: bundled/federated corridors among Rooms
- D9: smooth relay paths with fidelity/delay indicators
- D10: bundled/compressed system flows
- D11: usually no spiral needed; use orientation/criteria rather than decorative motion

The core principle is: `curve = path state`, not `curve = ornament`.
