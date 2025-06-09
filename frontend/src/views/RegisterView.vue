<template>
  <div class="register-container">
    <h1>Реєстрація</h1>
    <form @submit.prevent="register">
      <label>Ім'я користувача:</label>
      <input v-model="username" type="text" required />
      <label>Email:</label>
      <input v-model="email" type="email" />
      <label>Пароль:</label>
      <input v-model="password" type="password" required />
      <button type="submit">Зареєструватись</button>
      <p v-if="passwordWarning" class="error">Пароль повинен містити не менше 8 символів.</p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      error: '',
      success: '',
      passwordWarning: false
    };
  },
  methods: {
    async register() {
      this.error = '';
      this.success = '';
      this.passwordWarning = false;

      if (this.password.length < 8) {
        this.passwordWarning = true;
        return;
      }

      try {
        const res = await fetch('http://56.228.36.74:8000/api/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            email: this.email,
            password: this.password
          })
        });

        let data;
        try {
          data = await res.json();
        } catch {
          throw new Error('Сервер повернув невалідну відповідь. Спробуйте пізніше.');
        }

        if (!res.ok) {
          throw new Error(data.error || 'Помилка реєстрації');
        }

        this.success = 'Успішна реєстрація! Перенаправлення...';
        setTimeout(() => this.$router.push('/login'), 2000);
      } catch (err) {
        this.error = err.message;
      }
    }
  }
};
</script>

<style scoped>
.register-container {
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
.success {
  color: green;
}
</style>
