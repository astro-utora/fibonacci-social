import { 
  createStore, 
  createEvent, 
  createEffect, 
  sample,
  combine
} from 'effector'
import * as projectService from '@/services/project'
import type { ProjectMember } from '@/types/project'

// Effects - async operations
export const fetchProjectMembersFx = createEffect<string, ProjectMember[]>(
  async (projectId) => {
    const members = await projectService.getProjectMembers(projectId)
    return members
  }
)

export const addProjectMemberFx = createEffect<
  { projectId: string; user_id: string; role: string },
  ProjectMember
>(async ({ projectId, user_id, role }) => {
  const response = await projectService.addProjectMember(projectId, user_id, role)
  return response
})

export const removeProjectMemberFx = createEffect<
  { projectId: string; memberId: string },
  void
>(async ({ projectId, memberId }) => {
  await projectService.removeProjectMember(projectId, memberId)
})

// Events
export const resetProjectMembers = createEvent()
export const setSelectedMember = createEvent<ProjectMember | null>()

// Stores
export const $projectMembers = createStore<ProjectMember[]>([])
  .on(fetchProjectMembersFx.doneData, (_, members) => members)
  .on(addProjectMemberFx.doneData, (state, newMember) => [...state, newMember])
  .on(removeProjectMemberFx.done, (state, { params }) => 
    state.filter(member => {
      const memberId = member.id || member.uuid;
      return memberId !== params.memberId;
    })
  )
  .reset(resetProjectMembers)

export const $projectMembersLoading = createStore<boolean>(false)
  .on(fetchProjectMembersFx.pending, (_, pending) => pending)

export const $addingMember = createStore<boolean>(false)
  .on(addProjectMemberFx.pending, (_, pending) => pending)

export const $removingMember = createStore<boolean>(false)
  .on(removeProjectMemberFx.pending, (_, pending) => pending)

export const $selectedMember = createStore<ProjectMember | null>(null)
  .on(setSelectedMember, (_, member) => member)
  .reset(resetProjectMembers)

export const $projectMembersError = createStore<string | null>(null)
  .on(fetchProjectMembersFx.failData, (_, error) => error.message)
  .on(addProjectMemberFx.failData, (_, error) => error.message)
  .on(removeProjectMemberFx.failData, (_, error) => error.message)
  .reset(fetchProjectMembersFx)
  .reset(addProjectMemberFx)
  .reset(removeProjectMemberFx)

// Computed stores
export const $memberCount = $projectMembers.map(members => members.length)

// Auto-reload members after adding or removing
sample({
  source: addProjectMemberFx.done,
  fn: ({ params }) => params.projectId,
  target: fetchProjectMembersFx
})

sample({
  source: removeProjectMemberFx.done,
  fn: ({ params }) => params.projectId,
  target: fetchProjectMembersFx
}) 