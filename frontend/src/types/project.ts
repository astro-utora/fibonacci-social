export interface Project {
  id: string;
  project_name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  allow_guests: boolean;
}

export interface CreateProjectRequest {
  project_name: string;
  description?: string;
  allow_guests?: boolean;
}

export interface UpdateProjectRequest {
  project_name?: string;
  description?: string;
  allow_guests?: boolean;
}

export interface ProjectMember {
  id: string;
  project_id: string;
  user_id: string;
  role: string;
  created_at: string;
  user_name?: string;
  email?: string;
}

export interface ProjectUser {
  id: string;
  name: string;
  email?: string;
  role: string;
  last_active: string;
} 