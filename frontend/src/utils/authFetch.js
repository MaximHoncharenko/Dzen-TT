export async function authFetch(url, options = {}) {
  let access = localStorage.getItem('access');
  let refresh = localStorage.getItem('refresh');

  options.headers = {
    ...(options.headers || {}),
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json',
  };

  let response = await fetch(url, options);

  // Якщо токен протерміновано — пробуємо оновити
  if (response.status === 401 && refresh) {
    const refreshRes = await fetch('http://54.196.231.54/api/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (refreshRes.ok) {
      const data = await refreshRes.json();
      localStorage.setItem('access', data.access);

      // оновлюємо заголовок із новим токеном
      options.headers['Authorization'] = `Bearer ${data.access}`;
      response = await fetch(url, options);
    } else {
      // якщо refresh теж не валідний — видаляємо токени
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      window.location.href = '/login';
    }
  }

  return response;
}
