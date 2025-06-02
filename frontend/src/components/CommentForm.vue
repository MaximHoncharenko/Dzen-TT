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

      const token = localStorage.getItem('access'); // ⬅️ Витягуємо токен

      try {
        const response = await fetch('http://localhost:8000/api/comments/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // ⬅️ Додаємо токен у заголовок
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
