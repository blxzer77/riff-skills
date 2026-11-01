const express = require("express");
const checkout = require("./routes/checkout");
const orders = require("./routes/orders");

const app = express();
app.use(express.json());
app.use("/checkout", checkout);
app.use("/api/orders", orders);
module.exports = app;
