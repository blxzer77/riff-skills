import { invoiceTotal } from "../../billing";

export async function chargeAll(userIds: number[]) {
  for (const id of userIds) console.log(id, await invoiceTotal(id));
}
