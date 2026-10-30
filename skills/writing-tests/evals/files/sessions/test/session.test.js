import { test } from "node:test";
import assert from "node:assert/strict";
import { SessionStore } from "../src/session.js";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

test("returns the session before it expires", () => {
  const store = new SessionStore(1000);
  const id = store.create("u1");
  assert.equal(store.get(id).userId, "u1");
});

test("expires the session after the ttl", async () => {
  const store = new SessionStore(50);
  const id = store.create("u1");
  await sleep(50);
  assert.equal(store.get(id), null);
});
