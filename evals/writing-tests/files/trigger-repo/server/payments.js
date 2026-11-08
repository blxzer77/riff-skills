async function charge(cardToken, amount) {
  const card = await lookupCard(cardToken);
  if (card.expiry < new Date()) throw new Error("card expired");
  return { ok: amount > 0 };
}

async function lookupCard(token) {
  return { token, expiry: new Date(token.endsWith("x") ? "2020-01-01" : "2099-01-01") };
}

module.exports = { charge };
