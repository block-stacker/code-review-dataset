/**
 * Leaderboard helpers.
 *
 * This file contains a deliberate defect. See findings/typescript/ts-001.json.
 */

/** Return the `limit` highest scores, largest first. */
export function topScores(scores: number[], limit: number): number[] {
  return scores.sort().reverse().slice(0, limit);
}
