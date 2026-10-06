# World Map Functional Chain Explorer Design

## Goal
Make existing functional-chain records operational in the canonical World Map without adding another top-level menu.

## Interaction
Functional-chain tags in the selected-country card become buttons. Clicking one toggles that chain as the active contextual chain.

When active:
- participating countries receive a dedicated chain outline;
- the selected-country card shows the chain label, systems and short description;
- clicking the same chain again clears it;
- selecting another country does not silently clear the chain if that country belongs to it, but selecting a country outside it leaves the active chain visible as comparative context;
- the chain can always be cleared from its compact contextual strip.

## Visual ownership
- analytical scalar fill remains owned by the compositor;
- categorical overlap pattern remains owned by the compositor;
- country selection remains its existing outline/state;
- functional-chain context gets a distinct lower-priority outline layer using feature-state `atlasChainMatch`.

No country polygon fill is changed by chain exploration.

## Runtime ownership
Use the existing shared runtime:
- `chain(id)`
- `chainsForCountry(code)`

No new fetch path and no duplicate chain data.

## URL state
Persist the active chain as `chain=<id>`. Invalid or missing chain IDs resolve to no active chain.

## UI constraints
- no new permanent menu;
- no chain dropdown in the top bar;
- chain actions appear only where contextual chain information already appears;
- project/derived chain epistemic type and source note remain available in the compact chain context.

## Validation
A new validator must require:
- functional-chain tags carry stable chain IDs;
- explorer module uses shared runtime and feature-state;
- explorer owns a dedicated outline layer;
- URL `chain` persistence exists;
- bootstrap loads the explorer;
- no new top-level menu is introduced.
