# Property-based testing

Instead of hand-picked examples, state a property that must hold for all inputs in
a range; the library generates inputs, and on failure shrinks to a minimal
counterexample. It finds edge cases nobody thought to write.

## Libraries (verified 2026-10-30; check the registry for current versions)

| Language | Library | Notes |
|---|---|---|
| Python | Hypothesis (6.x) | failing examples are saved and replayed; pin a case with `@example` |
| JS/TS | fast-check (4.x) | works with any runner; seeded, reports the seed to replay |
| Rust | proptest (1.x) | commit `proptest-regressions/` files so failures replay forever |

Use whichever the project already has. Otherwise add the one above as a dev
dependency.

## Properties worth testing

| Pattern | Example |
|---|---|
| Round-trip | `decode(encode(x)) == x`; parse ∘ format; serialize ∘ deserialize |
| Invariant | sort keeps length and elements; slug never exceeds max length and never ends with `-` |
| Idempotence | `normalize(normalize(x)) == normalize(x)`; applying a migration twice |
| Oracle / model | fast implementation agrees with a slow obviously-correct one, or with a simple in-memory model of a stateful system |
| Different paths, same result | `apply(a, then b) == apply(b, then a)` where order should not matter |
| Hard to compute, easy to check | a solver's answer satisfies the constraints |

(Taxonomy after Scott Wlaschin, "Choosing properties for property-based testing".)

## Rules

- Keep example tests for documented behaviors and known bugs; properties complement
  them.
- Generators should produce valid domain inputs. Compose small generators; a complex
  generator is a new place for bugs.
- A property that restates the implementation proves nothing. State what must be
  true, not how it is computed.
- When a property fails, add the shrunk counterexample as a permanent example test.
- Bound sizes and example counts so the suite stays fast.
