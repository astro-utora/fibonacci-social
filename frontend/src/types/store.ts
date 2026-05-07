import type { Store } from 'effector'

export type StoreValue<T> = T extends Store<infer U> ? U : never 