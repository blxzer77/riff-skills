import { randomUUID } from "node:crypto";

export class SessionStore {
  constructor(ttlMs) {
    this.ttlMs = ttlMs;
    this.sessions = new Map();
  }

  create(userId) {
    const id = randomUUID();
    this.sessions.set(id, { userId, createdAt: Date.now() });
    return id;
  }

  get(id) {
    const session = this.sessions.get(id);
    if (!session) return null;
    if (Date.now() - session.createdAt > this.ttlMs) {
      this.sessions.delete(id);
      return null;
    }
    return session;
  }
}
