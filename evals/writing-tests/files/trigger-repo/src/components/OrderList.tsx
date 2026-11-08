import { useState, useEffect, useMemo } from "react";
import { formatMoney } from "../../packages/utils/src/time";

export function OrderList({ orders }: { orders: { id: number; total: number }[] }) {
  return <ul>{orders.map((o) => <li key={o.id}>{o.total}</li>)}</ul>;
}
