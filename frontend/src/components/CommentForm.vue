<<<<<<< HEAD
<template>
  <div class="comment-form">
    <h3 v-if="!parentId">Додати новий коментар</h3>
    <h3 v-else>Відповідь на коментар</h3>

    <!-- Только для анонимов -->
    <div v-if="!isAuthenticated">
      <input v-model="username" placeholder="User Name (латиниця, цифри)" required />
      <input v-model="email" placeholder="Email" required type="email" />
      <input v-model="homepage" placeholder="Home page (необовʼязково)" type="url" />
    </div>

    <textarea v-model="text" placeholder="Ваш коментар..." />
    <CaptchaImage ref="captchaImg" />
    <input v-model="captcha" placeholder="Введіть CAPTCHA" />
    <input type="file" @change="handleFile" accept=".jpg,.jpeg,.png,.gif,.txt" />
    <div v-if="file">
      <span>Файл: {{ file.name }}</span>
      <button type="button" @click="removeFile">Видалити</button>
    </div>
    <button @click="submitComment">Надіслати</button>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

=======
>>>>>>> 87de69ce221dc6cf0d22ed8ea060621e465c5864
<script>
import { authFetch } from '../utils/authFetch';
import CaptchaImage from './CaptchaImage.vue';

export default {
  name: 'CommentForm',
  components: { CaptchaImage },
  props: {
    parentId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      text: '',
      captcha: '',
      error: '',
      username: '',
      email: '',
      homepage: '',
      file: null,
    };
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access');
    },
  },
  mounted() {
    // Если пользователь авторизован, можно подставить email/username из профиля (если нужно)
  },
  methods: {
    handleFile(e) {
      const selected = e.target.files[0];
      if (!selected) return;
      const ext = selected.name.split('.').pop().toLowerCase();
      if (['jpg', 'jpeg', 'png', 'gif'].includes(ext) && selected.size > 2 * 1024 * 1024) {
        this.error = 'Зображення повинно бути не більше 2 МБ';
        return;
      }
      if (ext === 'txt' && selected.size > 100 * 1024) {
        this.error = 'Текстовий файл повинен бути не більше 100 КБ';
        return;
      }
      this.file = selected;
    },
    removeFile() {
      this.file = null;
    },
    async submitComment() {
      this.error = '';
      if (!this.text.trim() || !this.captcha.trim()) {
        this.error = 'Усі поля обовʼязкові';
        return;
      }
      if (!this.isAuthenticated && (!this.username.trim() || !this.email.trim())) {
        this.error = 'User Name та Email обовʼязкові для анонімних коментарів';
        return;
      }
      const formData = new FormData();
      formData.append('text', this.text);
      formData.append('captcha', this.captcha);
      if (!this.isAuthenticated) {
        formData.append('username', this.username);
        formData.append('email', this.email);
        formData.append('homepage', this.homepage);
      }
      if (this.parentId) formData.append('parent_id', this.parentId);
      if (this.file) formData.append('file', this.file);

      const token = localStorage.getItem('access'); // ⬅️ Витягуємо токен

      try {
        const response = await fetch('http://localhost:8000/api/comments/', {
          method: 'POST',
          body: formData,
          credentials: 'include',
          headers: {
<<<<<<< HEAD
            Authorization: localStorage.getItem('access') ? 'Bearer ' + localStorage.getItem('access') : undefined,
            // НЕ добавляйте Content-Type вручную!
=======
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // ⬅️ Додаємо токен у заголовок
>>>>>>> 87de69ce221dc6cf0d22ed8ea060621e465c5864
          },
        });
        if (!response.ok) {
          const err = await response.json();
          this.error = JSON.stringify(err);
          this.$refs.captchaImg.refreshCaptcha();
          return;
        }
        // очистка
        this.text = '';
        this.captcha = '';
        this.username = '';
        this.email = '';
        this.homepage = '';
        this.file = null;
        this.$refs.captchaImg.refreshCaptcha();
        this.$emit('comment-added');
      } catch (e) {
        this.error = e.message || 'Помилка при зʼєднанні з API';
        this.$refs.captchaImg.refreshCaptcha();
      }
    },
  },
};
</script>
