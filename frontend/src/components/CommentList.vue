<template>
  <div>
    <h2>Коментарі</h2>
    <button @click="logout" class="logout-button">Вийти</button>

    <div v-if="loading">Завантаження...</div>

    <div v-else>
      <div v-for="comment in comments" :key="comment.id" class="comment">
        <p><strong>{{ comment.user?.username || 'Анонім' }}</strong></p>
        <p>{{ comment.text }}</p>
        <div v-if="comment.replies" class="replies">
          <div v-for="reply in comment.replies" :key="reply.id" class="reply">
            ↳ <strong>{{ reply.user?.username || 'Анонім' }}</strong>: {{ reply.text }}
          </div>
        </div>
      </div>
    </div>

    <CommentForm @comment-added="fetchComments" />
  </div>
</template>

<script>
import CommentForm from './CommentForm.vue';

export default {
  name: 'CommentList',
  components: { CommentForm },
  data() {
    return {
      comments: [],
      loading: true,
    };
  },
  mounted() {
    const token = localStorage.getItem('access');
    if (!token) {
      this.$router.push('/login');
      return;
    }
    this.fetchComments();
  },
  methods: {
    async fetchComments() {
      this.loading = true;
      try {
        const token = localStorage.getItem('access');
        const response = await fetch('http://localhost:8000/api/comments/', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });

        if (response.status === 401) {
          this.logout();
          return;
        }

        const data = await response.json();
        this.comments = data.results;
      } catch (error) {
        console.error('Помилка при завантаженні коментарів:', error);
      } finally {
        this.loading = false;
      }
    },

    logout() {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      this.$router.push('/login');
    }
  }
};
</script>

<style>
.comment {
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
}
.replies {
  margin-left: 20px;
}
.reply {
  background: #f3f3f3;
  padding: 5px;
  margin-top: 5px;
}
.logout-button {
  float: right;
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 12px;
  margin-bottom: 10px;
  cursor: pointer;
}
</style>
