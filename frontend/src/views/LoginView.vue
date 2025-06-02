<template>
  <div class="login-container">
    <h1>Авторизація</h1>
    <form @submit.prevent="login">
      <label>Ім'я користувача:</label>
      <input v-model="username" type="text" required />
      <label>Пароль:</label>
      <input v-model="password" type="password" required />
      <button type="submit">Увійти</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await fetch('http://localhost:8000/api/token/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });

        if (!response.ok) {
          throw new Error('Невірний логін або пароль');
        }

        const data = await response.json();
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);

        this.$router.push('/'); // або на сторінку з коментарями
      } catch (err) {
        this.error = err.message;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
}
label, input {
  display: block;
  margin-bottom: 10px;
}
.error {
  color: red;
}
</style>
