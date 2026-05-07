import { createRouter, createWebHistory } from 'vue-router'
import { adminRoutes } from './admin'
import MainLayout from '@/layouts/MainLayout.vue'
import Home from '@/components/Home.vue'
import { requireAuth } from './guards'
import FillingUserProfile from '@/views/FillingUserProfile.vue'
import FilloutUserProfile from '@/views/FilloutUserProfile.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'Home',
          component: Home
        }
      ]
    },
    // {
    //   path: '/profile',
    //   component: FillingUserProfile
    // },
    {
      path: '/onboarding',
      component: FilloutUserProfile
    },
    {
      path: '/dashboard',
      component: MainLayout,
      beforeEnter: requireAuth,
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue')
        }
      ]
    },
    // Project settings route
    {
      path: '/project-settings/:id',
      component: MainLayout,
      beforeEnter: requireAuth,
      children: [
        {
          path: '',
          name: 'ProjectSettings',
          component: () => import('@/components/projects/ProjectSettings.vue')
        }
      ]
    },
    // Role tree editor route
    {
      path: '/roleTest',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'RoleTest',
          component: () => import('@/views/RoleTest.vue')
        }
      ]
    },
    // Admin routes
    ...adminRoutes,
    // Auth routes
    {
      path: '/verify-email',
      name: 'verify-email',
      component: () => import('@/components/EmailVerification.vue')
    },
    {
      path: '/test',
      name: 'test',
      component: MainLayout,
      beforeEnter: requireAuth,
      children: [
        {
          path: '',
          name: 'Test',
          component: () => import('@/views/Test.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

export default router