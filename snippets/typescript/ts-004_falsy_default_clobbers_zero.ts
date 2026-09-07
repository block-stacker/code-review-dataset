/**
 * Resolve caller-supplied retry options against defaults.
 *
 * This file contains a deliberate defect. See findings/typescript/ts-004.json.
 */

export interface RetryOptions {
  maxRetries?: number;
  label?: string;
}

export interface ResolvedOptions {
  maxRetries: number;
  label: string;
}

const DEFAULTS: ResolvedOptions = { maxRetries: 3, label: "job" };

/** Fill in any option the caller did not supply. */
export function resolveOptions(options: RetryOptions): ResolvedOptions {
  return {
    maxRetries: options.maxRetries || DEFAULTS.maxRetries,
    label: options.label || DEFAULTS.label,
  };
}
