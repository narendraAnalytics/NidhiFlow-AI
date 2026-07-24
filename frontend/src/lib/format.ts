export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

/** Live-formats a numeric input value with Indian-style digit grouping, e.g. "400000" -> "4,00,000". */
export function formatAmountInput(raw: string): string {
  const cleaned = raw.replace(/[^\d.]/g, "");
  const dotIndex = cleaned.indexOf(".");
  const intPart = dotIndex === -1 ? cleaned : cleaned.slice(0, dotIndex);
  const decPart = dotIndex === -1 ? "" : cleaned.slice(dotIndex + 1, dotIndex + 3);
  const digitsOnly = intPart.replace(/^0+(?=\d)/, "");
  const formattedInt = digitsOnly
    ? new Intl.NumberFormat("en-IN").format(Number(digitsOnly))
    : dotIndex !== -1
      ? "0"
      : "";
  return dotIndex === -1 ? formattedInt : `${formattedInt}.${decPart}`;
}

/** Reverses formatAmountInput for parsing before submit. */
export function parseAmountInput(value: string): number {
  return Number(value.replace(/,/g, ""));
}
