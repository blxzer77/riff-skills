const express = require("express");
const { charge } = require("../payments");

const router = express.Router();

router.post("/", async (req, res) => {
  const result = await charge(req.body.cardToken, req.body.amount);
  res.redirect(result.ok ? "/thanks" : "/payment-declined");
});

module.exports = router;
