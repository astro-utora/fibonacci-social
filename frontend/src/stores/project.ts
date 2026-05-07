import { 
  createStore, 
  createEvent, 
  createEffect, 
  sample 
} from 'effector'
import * as projectService from '@/services/project'
import type { SubRole } from '@/types'
import type { Project, CreateProjectRequest, UpdateProjectRequest } from '@/types/project'

// Effects
export const loadProjectsFx = createEffect<void, Project[]>(() => projectService.fetchProjects())
export const createProjectFx = createEffect<CreateProjectRequest, Project>(request => projectService.createProject(request))
export const updateProjectFx = createEffect<{id: string, data: UpdateProjectRequest}, Project>(params => projectService.updateProject(params.id, params.data))
export const selectProjectFx = createEffect<string, void>(id => projectService.selectProject(id))
export const closeProjectFx = createEffect<void, void>(() => projectService.closeProject())
export const loadProjectFx = createEffect<string, Project>()

// New effects for project role tree management
export const loadProjectRoleTreeFx = createEffect<string, { roots: SubRole[] } | { root: SubRole }>()
export const saveProjectRoleTreeFx = createEffect<
  { projectId: string; roots: SubRole[] } | { projectId: string; root: SubRole },
  { roots: SubRole[] } | { root: SubRole }
>()
export const resetProjectRoleTree = createEvent()

// Events
export const resetProjects = createEvent()
export const selectProject = createEvent<Project>()
export const closeProject = createEvent()
export const refreshProjects = createEvent()

// Stores
export const $projects = createStore<Project[]>([])
  .on(loadProjectsFx.doneData, (_, payload: Project[]) => payload)
  .on(createProjectFx.doneData, (state: Project[], payload: Project) => [...state, payload])
  .on(updateProjectFx.doneData, (state: Project[], updatedProject: Project) => 
    state.map(project => project.id === updatedProject.id ? updatedProject : project)
  )
  .reset(resetProjects)

export const $projectsLoading = createStore<boolean>(false)
  .on(loadProjectsFx.pending, (_, pending: boolean) => pending)
  .on(createProjectFx.pending, (_, pending: boolean) => pending)
  .on(updateProjectFx.pending, (_, pending: boolean) => pending)

export const $projectsError = createStore<string | null>(null)
  .on(loadProjectsFx.failData, (_, error: Error) => error.message)
  .on(createProjectFx.failData, (_, error: Error) => error.message)
  .on(updateProjectFx.failData, (_, error: Error) => error.message)
  .reset(loadProjectsFx)
  .reset(createProjectFx)
  .reset(updateProjectFx)

export const $activeProject = createStore<Project | null>(null)
  .on(selectProject, (_, project: Project) => project)
  .on(loadProjectFx.doneData, (_, project: Project) => project)
  .reset(closeProject)

export const $isProjectActive = createStore<boolean>(false)
  .on($activeProject, (_, project: Project | null) => project !== null)

// Project role tree store
export const $projectRoleTree = createStore<SubRole[] | null>(null)
  .on(loadProjectRoleTreeFx.doneData, (_, payload) => {
    // Handle both response formats: { root: ... } and { roots: [...] }
    if (payload.roots && Array.isArray(payload.roots)) {
      return payload.roots;
    } else if (payload.root) {
      return [payload.root];
    }
    return null;
  })
  .on(saveProjectRoleTreeFx.doneData, (_, payload) => {
    // Handle both response formats: { root: ... } and { roots: [...] }
    if (payload.roots && Array.isArray(payload.roots)) {
      return payload.roots;
    } else if (payload.root) {
      return [payload.root];
    }
    return null;
  })
  .reset(resetProjectRoleTree)

// Project role tree loading state
export const $projectRoleTreeLoading = createStore<boolean>(false)
  .on(loadProjectRoleTreeFx.pending, (_, pending: boolean) => pending)
  .on(saveProjectRoleTreeFx.pending, (_, pending: boolean) => pending)

// Project role tree error state
export const $projectRoleTreeError = createStore<string | null>(null)
  .on(loadProjectRoleTreeFx.failData, (_, error: Error) => error.message)
  .on(saveProjectRoleTreeFx.failData, (_, error: Error) => error.message)
  .reset(loadProjectRoleTreeFx)
  .reset(saveProjectRoleTreeFx)

// Wire up events
sample({
  source: closeProject,
  target: closeProjectFx
})

sample({
  source: selectProject,
  filter: (project: Project | null) => project !== null,
  fn: (project: Project) => project.id,
  target: selectProjectFx
})

// Connect refreshProjects event to loadProjectsFx
sample({
  source: refreshProjects,
  target: loadProjectsFx
})

// Automatically refresh projects after creation
sample({
  source: createProjectFx.done,
  target: refreshProjects
})

// Connect effects to API
loadProjectsFx.use(() => projectService.fetchProjects())
loadProjectFx.use(id => projectService.getProject(id))
loadProjectRoleTreeFx.use(projectId => projectService.fetchProjectRoleTree(projectId))
saveProjectRoleTreeFx.use(params => {
  if ('roots' in params) {
    return projectService.saveProjectRoleTree(params.projectId, { roots: params.roots });
  } else {
    return projectService.saveProjectRoleTree(params.projectId, { root: params.root });
  }
})

// When a project is selected, load its role tree
$activeProject.watch((project: Project | null) => {
  if (project) {
    loadProjectRoleTreeFx(project.id)
  } else {
    resetProjectRoleTree()
  }
})

// Automatically refresh projects after creation
sample({
  source: createProjectFx.done,
  target: refreshProjects
}) 