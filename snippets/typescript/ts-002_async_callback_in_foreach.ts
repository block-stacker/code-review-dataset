/**
 * Flush pending orders to storage.
 *
 * This file contains a deliberate defect. See findings/typescript/ts-002.json.
 */

export interface Order {
  id: string;
}

/** Write every order, resolving once all of them have been persisted. */
export async function flushOrders(
  orders: Order[],
  save: (order: Order) => Promise<void>,
): Promise<number> {
  let written = 0;
  orders.forEach(async (order) => {
    await save(order);
    written += 1;
  });
  return written;
}
