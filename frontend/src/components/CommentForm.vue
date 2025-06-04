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

    <!-- Панель тегов -->
    <div class="tag-panel">
      <button type="button" @click="insertTag('i')"><i>i</i></button>
      <button type="button" @click="insertTag('strong')"><strong>strong</strong></button>
      <button type="button" @click="insertTag('code')"><code>code</code></button>
      <button type="button" @click="insertLink">a</button>
    </div>
    <!-- Поле ввода -->
    <textarea
      v-model="text"
      ref="textarea"
      placeholder="Ваш коментар..."
    />
    <CaptchaImage ref="captchaImg" />
    <input v-model="captcha" placeholder="Введіть CAPTCHA" />
    <input type="file" @change="handleFile" accept=".jpg,.jpeg,.png,.gif,.txt" />
    <div v-if="file">
      <span>Файл: {{ file.name }}</span>
      <button type="button" @click="removeFile">Видалити</button>
    </div>
    <button @click="submitComment">Надіслати</button>
    <p v-if="error" class="error">{{ error }}</p>

    <button type="button" @click="showPreview = !showPreview" style="margin-bottom:8px;">
      {{ showPreview ? 'Сховати перегляд' : 'Переглянути' }}
    </button>
    <div v-if="showPreview" class="preview-block">
      <h4>Попередній перегляд:</h4>
      <div v-html="renderedPreview" class="preview-content"></div>
      <div v-if="file" style="margin-top:8px;">
        <img v-if="isImage(file.name)" :src="fileUrl" style="max-width:120px;max-height:90px;" />
        <span v-else>TXT: {{ file.name }}</span>
      </div>
    </div>
  </div>
</template>

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
      showPreview: false,
      fileUrl: null,
    };
  },
  watch: {
    file(newFile) {
      if (newFile && this.isImage(newFile.name)) {
        this.fileUrl = URL.createObjectURL(newFile);
      } else {
        this.fileUrl = null;
      }
    }
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access');
    },
    renderedPreview() {
      // Оставляем только разрешённые теги и атрибуты
      const allowedTags = ['i', 'strong', 'code', 'a'];
      const allowedAttrs = { a: ['href', 'title'] };
      // Используем bleach или простую замену (если bleach не доступен на фронте)
      // Здесь пример простой фильтрации:
      let html = this.text
        .replace(/</g, '&lt;')
        .replace(/&lt;(\/?(i|strong|code|a)( [^&<>]*)?)&gt;/gi, '<$1>');
      // Очищаем атрибуты у <a>
      html = html.replace(/<a([^>]*)>/gi, (match, attrs) => {
        const href = (attrs.match(/href="([^"]*)"/) || [])[1] || '';
        const title = (attrs.match(/title="([^"]*)"/) || [])[1] || '';
        return `<a href="${href}" title="${title}">`;
      });
      return html;
    }
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

      try {
        const response = await fetch('http://localhost:8000/api/comments/', {
          method: 'POST',
          body: formData,
          credentials: 'include',
          headers: {
            Authorization: localStorage.getItem('access') ? 'Bearer ' + localStorage.getItem('access') : undefined,
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
        this.showPreview = false;
        this.$refs.captchaImg.refreshCaptcha();
        this.$emit('comment-added');
      } catch (e) {
        this.error = e.message || 'Помилка при зʼєднанні з API';
        this.$refs.captchaImg.refreshCaptcha();
      }
    },
    insertTag(tag) {
      // Добавить тег в конце, с новой строки
      const tagText = `<${tag}></${tag}>`;
      if (this.text && !this.text.endsWith('\n')) {
        this.text += '\n';
      }
      this.text += tagText;
      this.$nextTick(() => {
        this.$refs.textarea.focus();
      });
    },
    insertLink() {
      const url = prompt('Введіть URL:', 'https://');
      if (url) {
        const linkText = `<a href="${url}" title="">текст</a>`;
        if (this.text && !this.text.endsWith('\n')) {
          this.text += '\n';
        }
        this.text += linkText;
        this.$nextTick(() => {
          this.$refs.textarea.focus();
        });
      }
    },
    validateTags(text) {
      // Разрешённые теги
      const allowed = ['i', 'strong', 'code', 'a'];
      // Найти все открывающие и закрывающие теги
      const tags = [...text.matchAll(/<\/?([a-z]+)[^>]*>/gi)].map(m => m[1].toLowerCase());
      // Проверить, что все теги разрешённые
      for (const tag of tags) {
        if (!allowed.includes(tag)) {
          return `Дозволені лише теги: <i>, <strong>, <code>, <a>`;
        }
      }
      // Проверить парность тегов (упрощённо)
      for (const tag of allowed) {
        const open = (text.match(new RegExp(`<${tag}[^>]*>`, 'gi')) || []).length;
        const close = (text.match(new RegExp(`</${tag}>`, 'gi')) || []).length;
        if (open !== close) {
          return `Тег <${tag}> не закритий або закритий некоректно`;
        }
      }
      return null;
    },
    isImage(name) {
      return /\.(jpg|jpeg|png|gif)$/i.test(name);
    },
  },
};
</script>

<style>
.comment-form {
  margin-top: 2rem;
}
textarea {
  width: 100%;
  height: 80px;
  margin-bottom: 8px;
}
input {
  width: 100%;
  margin-bottom: 8px;
}
.error {
  color: red;
}
.tag-panel {
  margin-bottom: 8px;
}
.tag-panel button {
  background: #232324;
  color: #fff;
  border: 1px solid #444;
  border-radius: 4px;
  margin-right: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 1em;
  transition: background 0.2s;
}
.tag-panel button:hover {
  background: #333;
}
.preview-block {
  background: #232324;
  color: #fff;
  border: 1px solid #444;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}
.preview-content {
  white-space: pre-wrap;
  font-size: 1em;
}
</style>
