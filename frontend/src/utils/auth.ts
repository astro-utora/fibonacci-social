export const loginWithTelegram = (invitationId?: string) => {
  console.group('Telegram Login Flow')
  console.log('Initializing Telegram login process')
  
  const width = 550
  const height = 470
  const left = window.innerWidth / 2 - width / 2
  const top = window.innerHeight / 2 - height / 2
  
//   const host = window.location.origin
  const host = "https://stas-k.org"
  // Build return URL with invitation parameter only
  const returnUrl = new URL('/telegram-callback', host)
  if (invitationId != null) {
    returnUrl.searchParams.set('invitation', invitationId)
  }
  
  const loginUrl = `https://oauth.telegram.org/auth?` +
    new URLSearchParams({
    //   bot_id: "7739202584",
      bot_id: "6205744531",
      origin: host,
      request_access: 'write',
      return_to: returnUrl.toString(),
      embed: '0'
    }).toString()
  
  console.log('Generated login URL:', loginUrl)
  
  // Open in same window instead of popup
  window.location.href = loginUrl
} 