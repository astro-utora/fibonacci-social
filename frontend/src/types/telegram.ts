export interface TelegramAuthData {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  photo_url?: string;  // Optional as per backend
  auth_date: number;
  hash: string;
  invitation_id?: string;  // Optional UUID string for invitation
} 