export interface User {
  uuid: string;
  email: string;
  name?: string | null;
  location?: string | null;
  workplace?: string | null;
  birth_date?: string | null;
  goals?: string | null;
  education?: string | null;
  phone_number?: string | null;
  avatar_url?: string | null;
  credits?: number;
  referral_code?: string;
  created_at?: string;
}

export interface SubRole {
  role: string
  filloutId?: string
  subroles: SubRole[]
}

export interface ProfileData {
  name: string | null
  location: string | null
  workplace: string | null
  role: string | null
  birth_date: string | null
  goals: string | null
  education: string | null
  referral_code: string
  avatar_url: string | null
  willing_to_contribute?: boolean | null
  credits?: number
}
