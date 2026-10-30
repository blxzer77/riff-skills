import express from "express";
import session from "express-session";

const app = express();

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, sameSite: "lax", maxAge: 7 * 24 * 3600 * 1000 },
}));

app.get("/me", (req, res) => res.json({ user: req.session.user ?? null }));

app.listen(3000);
