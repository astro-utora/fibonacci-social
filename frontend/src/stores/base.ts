import { 
  createStore as effectorCreateStore, 
  createEvent as effectorCreateEvent, 
  createEffect as effectorCreateEffect,
  Store,
  Event,
  Effect
} from 'effector'

export function createStore<T>(initialState: T): Store<T> {
  return effectorCreateStore<T>(initialState)
}

export function createEvent<T>(): Event<T> {
  return effectorCreateEvent<T>()
}

export function createEffect<Params, Done, Fail = Error>(): Effect<Params, Done, Fail> {
  return effectorCreateEffect<Params, Done, Fail>()
}

export function createBaseStore<T>(name: string) {
  const $data = createStore<T | null>(null)
  const $error = createStore<string | null>(null)
  const $isLoading = createStore(false)
  
  const setError = createEvent<string>()
  const clearError = createEvent()
  
  $error
    .on(setError, (_: any, error: any) => error)
    .reset(clearError)
  
  return {
    $data,
    $error,
    $isLoading,
    setError,
    clearError
  }
}

export function withErrorHandling<T>(effect: any) {
  effect.failData.watch((error: Error) => {
    console.error(`${effect.name} failed:`, error)
  })
  return effect
}

