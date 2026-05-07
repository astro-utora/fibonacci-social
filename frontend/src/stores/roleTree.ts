import { 
  createStore, 
  createEvent, 
  createEffect, 
  sample, 
  combine, 
  Store, 
  Event, 
  Effect 
} from 'effector'
import type { SubRole } from '@/types'
import * as roleTreeService from '@/services/roleTree'

// Effects
export const loadRoleTreeFx = createEffect<{ projectId?: string } | void, { roots: SubRole[] } | { root?: SubRole }>()
export const saveRoleTreeFx = createEffect<
  { roots: SubRole[]; projectId?: string } | { root: SubRole; projectId?: string },
  { roots: SubRole[] } | { root: SubRole }
>()

// Events
export const setSelectedRolePath = createEvent<string[]>()
export const expandRole = createEvent<string[]>()
export const collapseRole = createEvent<string[]>()
export const clearSelection = createEvent()
export const updateExpandedPaths = createEvent<string[][]>()
export const resetRoleTree = createEvent()

// Add new events and helpers
export const selectAndCollapseOthers = createEvent<{
  role: SubRole
  path: string[]
}>()

// Stores
export const $roleTree = createStore<SubRole[] | null>(null)
  .on(loadRoleTreeFx.doneData, (_, payload) => {
    // Handle both response formats: { root: ... } and { roots: [...] }
    if (payload.roots && Array.isArray(payload.roots)) {
      return payload.roots;
    } else if (payload.root) {
      return [payload.root];
    }
    return null;
  })
  .on(saveRoleTreeFx.doneData, (_, payload) => {
    // Handle both response formats: { root: ... } and { roots: [...] }
    if (payload.roots && Array.isArray(payload.roots)) {
      return payload.roots;
    } else if (payload.root) {
      return [payload.root];
    }
    return null;
  })
  .reset(resetRoleTree)

export const $roleTreeLoading = createStore<boolean>(false)
  .on(loadRoleTreeFx.pending, (_, pending) => pending)
  .on(saveRoleTreeFx.pending, (_, pending) => pending)

export const $roleTreeError = createStore<string | null>(null)
  .on(loadRoleTreeFx.failData, (_, error: Error) => error.message)
  .on(saveRoleTreeFx.failData, (_, error: Error) => error.message)
  .reset(loadRoleTreeFx)
  .reset(saveRoleTreeFx)

export const $selectedRolePath = createStore<string[]>([])
  .on(setSelectedRolePath, (_, path) => path)
  .reset(clearSelection)

export const $expandedRolePaths = createStore<string[][]>([])
  .on(expandRole, (state, path) => [...state, path])
  .on(collapseRole, (state, path) => 
    state.filter(existingPath => !pathsEqual(existingPath, path))
  )
  .on(updateExpandedPaths, (_, paths) => paths)
  .reset(clearSelection)

// Connect effects to API
loadRoleTreeFx.use(roleTreeService.fetchRoleTree)
saveRoleTreeFx.use(roleTreeService.saveRoleTree)

// Auto-collapse other paths when selecting a new role
sample({
  source: setSelectedRolePath,
  fn: ({ path }: { path: string[] }) => {
    // Generate all ancestor paths for the selected role
    return path.reduce((acc: string[][], _, index) => {
      acc.push(path.slice(0, index + 1))
      return acc
    }, [])
  },
  target: $expandedRolePaths
})

// Helper functions
function pathsEqual(a: string[], b: string[]) {
  if (a.length !== b.length) return false
  return a.every((val, i) => val === b[i])
}

function findRoleByPath(tree: SubRole | null, path: string[]): SubRole | null {
  if (!tree || path.length === 0) return null
  
  let currentRole = tree
  for (const roleName of path) {
    const subrole = currentRole.subroles.find(r => r.role === roleName)
    if (!subrole) return null
    currentRole = subrole
  }
  return currentRole
}

// Computed stores
export const $selectedRole = createStore<SubRole | null>(null)

sample({
  source: { tree: $roleTree, path: $selectedRolePath },
  fn: ({ tree, path }: { tree: SubRole | null; path: string[] }) => findRoleByPath(tree, path),
  target: $selectedRole
})

// Helper to create a path-based store
function createPathStore(defaultValue: boolean) {
  return (path: string[]) => createStore<boolean>(defaultValue)
    .on(expandRole, (state, expandPath) => 
      pathsEqual(expandPath, path) ? true : state
    )
    .on(collapseRole, (state, collapsePath) => 
      pathsEqual(collapsePath, path) ? false : state
    )
}

export const $isRoleExpanded = createPathStore(false)
export const $isRoleSelected = createPathStore(false)

// Add a new computed store for role status
export const $roleStatus = (path: string[]) => 
  combine(
    $selectedRole,
    $isRoleExpanded(path),
    $isRoleSelected(path),
    (selectedRole: SubRole | null, isExpanded: boolean, isSelected: boolean) => ({
      isSelected,
      isExpanded,
      hasFillout: selectedRole?.filloutId != null,
      hasSubroles: (selectedRole?.subroles.length ?? 0) > 0
    })
  )

function isAncestorPath(path1: string[], path2: string[]): boolean {
  if (path1.length > path2.length) return false
  return path1.every((role, index) => role === path2[index])
}

// Update selection behavior
sample({
  source: selectAndCollapseOthers,
  fn: ({ role, path }: { role: SubRole; path: string[] }) => {
    const ancestorPaths = path.reduce((acc: string[][], _, index) => {
      acc.push(path.slice(0, index + 1))
      return acc
    }, [])
    
    return { role, path, ancestorPaths }
  },
  target: [
    setSelectedRolePath.prepend(({ role, path }) => path),
    updateExpandedPaths.prepend(({ ancestorPaths }) => ancestorPaths)
  ]
}) 