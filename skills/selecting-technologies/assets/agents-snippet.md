## Technology choices

Before adding a dependency, picking a runtime version or base image, or naming an
LLM model, read the manifests and deployment files and use what the project
already has when it covers the need. For anything new, check today's facts rather
than memory: last release date, end-of-life status, the provider's current model
list, and known advisories; then install it fresh and run the tests. Do not add a
new service (broker, cache, datastore) when the existing stack can do the job.
Sticky choices (datastore, framework, hosted service) get 2–4 candidates, an exit
path, and an ADR.
