## Module boundaries

- Use another module only through its public interface. Do not import its internal
  or private code, or read its tables; add a public function on the owning module if
  you need one.
- Do not create shared `utils` or `common` packages for convenience; put a helper in
  the module that owns the concept, or duplicate a few lines.
- Do not introduce import cycles between modules.
- Run the project's boundary checks before finishing a change that crosses modules.
- Prefer a module in the existing deployable over a new package or service unless an
  independent scaling, release, ownership, or isolation need is stated.
