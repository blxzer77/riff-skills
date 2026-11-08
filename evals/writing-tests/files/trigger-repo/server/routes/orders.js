const express = require("express");
const db = require("../db");

const router = express.Router();

router.get("/", async (_req, res) => {
  res.json(await db.allOrders());
});

module.exports = router;
