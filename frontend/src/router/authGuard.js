export function requireAuth(to, from, next) {
  const access = localStorage.getItem('access');
  if (access) {
    next();
  } else {
    next('/login');
  }
}

export function requireGuest(to, from, next) {
  const access = localStorage.getItem('access');
  if (access) {
    next('/');
  } else {
    next();
  }
}
