import api from '@/utils/axios'
import type { Project, CreateProjectRequest, UpdateProjectRequest } from '@/types/project'

export async function fetchProjects(): Promise<Project[]> {
  const { data } = await api.get('/api/projects')
  return data.projects
}

export async function createProject(request: CreateProjectRequest): Promise<Project> {
  const { data } = await api.post('/api/projects', request)
  return data.project
}

export async function selectProject(projectId: string): Promise<void> {
  await api.post(`/api/projects/${projectId}/select`)
}

export async function closeProject(): Promise<void> {
  await api.post('/api/projects/close')
}

export async function updateProject(projectId: string, request: UpdateProjectRequest): Promise<Project> {
  const { data } = await api.put(`/api/projects/${projectId}`, request)
  return data.project
}

export async function saveProjectRoleTree(projectId: string, roleTree: any): Promise<void> {
  await api.post(`/api/role-tree?project_id=${projectId}`, roleTree)
}

export async function fetchProjectRoleTree(projectId: string): Promise<any> {
  const { data } = await api.get(`/api/role-tree?project_id=${projectId}`)
  return data
}

export async function getProjectUsers(projectId: string): Promise<any[]> {
  const { data } = await api.get(`/api/projects/${projectId}/users`)
  return data.users
}

export async function getProjectMembers(projectId: string): Promise<any[]> {
  const { data } = await api.get(`/api/projects/${projectId}/members`)
  return data
}

export async function addProjectMember(projectId: string, user_id: string, role: string = 'member'): Promise<any> {
  try {
    const { data } = await api.post(`/api/projects/${projectId}/members`, {
      user_id,
      role
    });
    return data;
  } catch (error) {
    console.error('Error adding project member:', error);
    throw error;
  }
}

export async function removeProjectMember(projectId: string, memberId: string): Promise<void> {
  try {
    await api.delete(`/api/projects/${projectId}/members/${memberId}`);
  } catch (error) {
    console.error('Error removing project member:', error);
    throw error;
  }
}

export async function getProject(projectId: string): Promise<Project> {
  const { data } = await api.get(`/api/projects/${projectId}`)
  return data.project
}

export async function getProjectSettings(projectId: string): Promise<any[]> {
  const { data } = await api.get(`/api/projects/${projectId}/settings`)
  return data.settings
}

export async function updateProjectSetting(projectId: string, settingKey: string, value: string): Promise<any> {
  const { data } = await api.patch(`/api/projects/${projectId}/settings/${settingKey}`, {
    value
  })
  return data
} 
