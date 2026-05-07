import { createStore, createEvent } from 'effector'

export interface Notification {
  message: string
  type: 'success' | 'error' | 'info'
  timeout?: number
}

export const showNotification = createEvent<Notification>()
export const hideNotification = createEvent()

export const $notification = createStore<Notification | null>(null)
  .on(showNotification, (_, notification) => notification)
  .on(hideNotification, () => null)

// Auto-hide notifications
showNotification.watch((notification) => {
  if (notification.timeout !== 0) {
    setTimeout(() => {
      hideNotification()
    }, notification.timeout || 3000)
  }
}) 