declare module 'vitest' {
  export const describe: Function
  export const it: Function
  export const expect: Function
  export const beforeEach: Function
  export const vi: {
    mock: Function
    fn: Function
  }
  interface Vi {
    mocked<T>(item: T): T
    clearAllMocks(): void
  }
}

declare module '@vue/test-utils' {
  export const mount: Function
}

declare module 'effector' {
  interface Store<State> {
    setState(state: State): void
  }
}

declare global {
  interface Storage {
    length: number
    key(index: number): string | null
    getItem(key: string): string | null
    setItem(key: string, value: string): void
    removeItem(key: string): void
    clear(): void
  }
} 