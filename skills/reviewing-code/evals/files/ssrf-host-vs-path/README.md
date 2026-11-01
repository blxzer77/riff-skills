# chat-previews

Server-side helpers for a chat service. `payload` is the JSON body a logged-in chat
user sends; the server runs inside a VPC alongside internal services such as
`status.internal.example.com` and the cloud metadata endpoint. `http` is the
service's shared HTTP client.

`review.patch` is the pending change; `src/` has it applied.

PR description: "Add link previews for pasted URLs and a message delivery-status
lookup."
