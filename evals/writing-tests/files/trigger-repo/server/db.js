const orders = Array.from({ length: 95 }, (_, i) => ({ id: i + 1, total: (i + 1) * 100 }));
module.exports = { allOrders: async () => orders };
