// @ts-ignore - Suppressing TS errors for Effector imports
import { createStore, createEvent } from 'effector'

// Create event to set the login email
export const setLoginEmail = createEvent<string>()

// Create store with empty string as initial value
export const $loginEmail = createStore<string>('')
  .on(setLoginEmail, (_: string, email: string) => email) 