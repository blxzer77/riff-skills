import Database from "better-sqlite3";

export const db = new Database("readwell.db");
db.exec("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT)");
