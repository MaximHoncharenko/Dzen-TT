<template>
  <div class="comment-form">
    <h3>Додати новий коментар</h3>
    <textarea v-model="text" placeholder="Ваш коментар..." />
    <input v-model="captcha" placeholder="Введіть CAPTCHA (abcd)" />
    <button @click="submitComment">Надіслати</button>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
export default {
  name: 'CommentForm',
  data() {
    return {
      text: '',
      captcha: '',
      error: '',
    };
  },
  methods: {
    async submitComment() {
      this.error = '';
      if (!this.text.trim() || !this.captcha.trim()) {
        this.error = 'Усі поля обовʼязкові';
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/comments/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: this.text,
            captcha: this.captcha,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          this.error = JSON.stringify(err);
          return;
        }

        this.text = '';
        this.captcha = '';
        this.$emit('comment-added'); // повідомляє CommentList.vue перезавантажити список
      } catch (e) {
        this.error = 'Помилка при зʼєднанні з API';
      }
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
</style>
