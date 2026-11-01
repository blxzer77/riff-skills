# shopfront

Order management for a small online shop. One deployable, two developers.

Modules live under `shop/`. Each module's public API is its `__init__.py`; code under
`<module>/internal/` is private to that module. The boundaries are declared in
`.importlinter` and checked in CI with `lint-imports`. Run tests with
`python3 -m unittest`.
