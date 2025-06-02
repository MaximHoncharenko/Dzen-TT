import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import CommentList from '../components/CommentList.vue';
import { isAuthenticated } from '../utils/auth';

const routes = [
  {
    path: '/',
    component: CommentList,
    meta: { requiresAuth: true }  // 🔐 вимагає авторизацію
  },
  {
    path: '/login',
    component: LoginView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 🔐 Глобальний захист маршруту
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login');
  } else {
    next();
  }
});

export default router;
