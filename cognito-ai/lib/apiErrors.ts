/**
 * Parse Django-style JSON error bodies (`{ "detail": ... }`) for user-facing messages.
 */

export async function readHttpErrorMessage(
  res: Response,
  fallbackLabel: string
): Promise<string> {
  const statusSuffix = `${fallbackLabel} (${res.status})`;
  try {
    const text = await res.text();
    if (!text.trim()) {
      return statusSuffix;
    }
    try {
      const data = JSON.parse(text) as { detail?: unknown };
      const d = data?.detail;
      if (typeof d === "string" && d.trim()) {
        return d.trim();
      }
      if (Array.isArray(d)) {
        const joined = d.map(String).filter(Boolean).join("; ");
        if (joined) {
          return joined;
        }
      }
    } catch {
      const clipped = text.trim().slice(0, 240);
      if (clipped) {
        return clipped;
      }
    }
  } catch {
    return statusSuffix;
  }
  return statusSuffix;
}
