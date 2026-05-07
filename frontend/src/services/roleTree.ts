import type { SubRole } from '@/types'
import api from '@/utils/axios'

export function validateRoleTree(tree: SubRole): string | null {
  try {
    if (!tree.role?.trim()) {
      return 'Role name cannot be empty'
    }

    if (tree.filloutId != null && typeof tree.filloutId !== 'string') {
      return 'Fillout ID must be a string or undefined'
    }

    if (!Array.isArray(tree.subroles)) {
      return 'Subroles must be an array'
    }

    // Validate subroles recursively
    for (const subrole of tree.subroles) {
      const error = validateRoleTree(subrole)
      if (error) return error
    }

    return null
  } catch (e) {
    return 'Invalid role tree structure'
  }
}

interface RoleTreeParams {
  projectId?: string;
}

export async function fetchRoleTree(params?: RoleTreeParams) {
  const url = params?.projectId 
    ? `/api/projects/${params.projectId}/role-tree`
    : '/api/role-tree';
    
  const { data } = await api.get(url)
  return data
}

export async function saveRoleTree(payload: { root: SubRole } | { roots: SubRole[] }, params?: RoleTreeParams) {
  const url = params?.projectId 
    ? `/api/projects/${params.projectId}/role-tree`
    : '/api/role-tree';
    
  const { data } = await api.post(url, payload)
  return data
} 