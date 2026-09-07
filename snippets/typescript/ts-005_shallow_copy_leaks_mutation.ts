/**
 * Derive a muted copy of a user's settings.
 *
 * This file contains a deliberate defect. See findings/typescript/ts-005.json.
 */

export interface Settings {
  theme: string;
  notifications: {
    email: boolean;
    push: boolean;
  };
}

/** Return a copy with notifications disabled, leaving `settings` untouched. */
export function withNotificationsOff(settings: Settings): Settings {
  const copy = { ...settings };
  copy.notifications.email = false;
  copy.notifications.push = false;
  return copy;
}
