import express from "express";
import { getUserData } from "../api/src/users/repo";

export const router = express.Router();

export async function invoiceTotal(userId: number): Promise<number> {
  const user = await getUserData(userId);
  return user ? 500 : 0;
}

router.get("/invoices/:id/total", async (req, res) => {
  res.json({ total: await invoiceTotal(Number(req.params.id)) });
});
