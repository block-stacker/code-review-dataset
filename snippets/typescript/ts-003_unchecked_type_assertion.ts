/**
 * Decode sensor readings received over the network.
 *
 * This file contains a deliberate defect. See findings/typescript/ts-003.json.
 */

export interface Reading {
  sensorId: string;
  celsius: number;
}

/** Decode one reading from a request body. */
export function parseReading(body: string): Reading {
  return JSON.parse(body) as Reading;
}

/** Convert a decoded reading to Fahrenheit for display. */
export function toFahrenheit(reading: Reading): number {
  return reading.celsius * (9 / 5) + 32;
}
