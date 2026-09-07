/**
 * Parse configuration values supplied as delimited strings.
 *
 * This file contains a deliberate defect. See findings/typescript/ts-006.json.
 */

/** Parse a comma-separated list of port numbers. */
export function parsePorts(raw: string): number[] {
  return raw.split(",").map(parseInt);
}
