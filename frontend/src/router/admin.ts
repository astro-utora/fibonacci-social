import { RouteRecordRaw } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { requireAdmin } from './guards'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: AdminLayout,
    beforeEnter: requireAdmin,
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/DashboardView.vue')
      },
      {
        path: 'role-tree',
        name: 'RoleTreeEditor',
        component: () => import('@/views/admin/RoleTreeView.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'user-forms',
        name: 'UserForms',
        component: () => import('@/views/admin/UserFormsView.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'waiting-list',
        name: 'WaitingList',
        component: () => import('@/views/admin/WaitingListView.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/SettingsView.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  }
] 