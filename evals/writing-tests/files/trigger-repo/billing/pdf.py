def render_invoice(invoice: dict) -> str:
    lines = [f"INVOICE {invoice['number']}", f"Customer: {invoice['customer']}"]
    for item in invoice["items"]:
        lines.append(f"{item['name']:<30}{item['qty']:>4}{item['price'] / 100:>10.2f}")
    total = sum(i["qty"] * i["price"] for i in invoice["items"])
    lines.append(f"{'TOTAL':<34}{total / 100:>10.2f}")
    return "\n".join(lines)
