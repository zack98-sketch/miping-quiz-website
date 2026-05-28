import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/RegisterView.vue'),
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/quiz/QuizHomeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/quiz/session/:id',
    name: 'QuizSession',
    component: () => import('../views/quiz/QuizSessionView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/quiz/result/:id',
    name: 'QuizResult',
    component: () => import('../views/quiz/QuizResultView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/error-book',
    name: 'ErrorBook',
    component: () => import('../views/errorbook/ErrorBookView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/favorite/FavoriteView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('../views/analysis/AnalysisView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/analysis/HistoryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/exams',
    name: 'Exams',
    component: () => import('../views/exam/ExamListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/exam/session/:id',
    name: 'ExamSession',
    component: () => import('../views/exam/ExamSessionView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/notes',
    name: 'Notes',
    component: () => import('../views/note/NoteListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/corrections',
    name: 'MyCorrections',
    component: () => import('../views/correction/MyCorrectionsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/admin/DashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
