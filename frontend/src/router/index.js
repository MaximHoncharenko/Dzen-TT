import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import CommentList from '../components/CommentList.vue';
import { requireAuth, requireGuest } from './authGuard';

const routes = [
  {
    path: '/',
    component: CommentList,
    beforeEnter: requireAuth,
  },
  {
    path: '/login',
    component: LoginView,
    beforeEnter: requireGuest,
  },
  {
    path: '/register',
    component: RegisterView,
    beforeEnter: requireGuest,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
