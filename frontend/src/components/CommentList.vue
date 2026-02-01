<template>
  <div>
    <h2>Коментарі</h2>
    <button @click="logout" class="logout-button">Вийти</button>

    <div v-if="loading">Завантаження...</div>

    <div v-else>
      <div v-if="comments.length === 0">Ще немає жодного коментаря.</div>

      <!-- Таблиця коментарів -->
      <table class="comments-table">
        <thead>
          <tr>
            <th @click="setOrdering('user__username')">User Name</th>
            <th @click="setOrdering('created_at')">Дата</th>
            <th>Текст</th>
            <th>Файли</th>
            <th>Дії</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="comment in comments" :key="comment.id">
            <td>{{ comment.user || comment.username || 'Анонім' }}</td>
            <td>{{ new Date(comment.created_at).toLocaleString() }}</td>
            <td>
              {{ comment.text }}
              <!-- Выводим ответы прямо под текстом комментария -->
              <div v-if="comment.replies && comment.replies.length" class="replies">
                <div v-for="reply in comment.replies" :key="reply.id" class="reply">
                  <strong>{{ reply.user || reply.username || 'Анонім' }}</strong>: {{ reply.text }}
                  <div v-if="reply.attachments && reply.attachments.length">
                    <div v-for="att in reply.attachments" :key="att.id" style="display:inline-block; margin-right:5px;">
                      <img
                        v-if="isImage(att.file)"
                        :src="att.file.startsWith('http') ? att.file : 'http://54.196.231.54' + att.file"
                        @click="openLightbox(att.file.startsWith('http') ? att.file : 'http://54.196.231.54' + att.file)"
                        style="max-width:40px;max-height:40px;cursor:pointer;border:1px solid #ccc;"
                        alt="attachment"
                      />
                      <a
                        v-else
                        :href="att.file.startsWith('http') ? att.file : 'http://54.196.231.54' + att.file"
                        target="_blank"
                      >TXT</a>
                    </div>
                  </div>
                </div>
              </div>
            </td>
            <td>
              <div v-if="comment.attachments && comment.attachments.length">
                <div v-for="att in comment.attachments" :key="att.id" style="display:inline-block; margin-right:5px;">
                  <img
                    v-if="isImage(att.file)"
                    :src="att.file.startsWith('http') ? att.file : 'http://54.196.231.54' + att.file"
                    @click="openLightbox(att.file.startsWith('http') ? att.file : 'http://54.196.231.54' + att.file)"
                    style="max-width:60px;max-height:60px;cursor:pointer;border:1px solid #ccc;"
                    alt="attachment"
                  />
                  <a
                    v-else
                    :href="att.file.startsWith('http') ? att.file : 'http://54.196.231.54' + att.file"
                    target="_blank"
                  >TXT</a>
                </div>
              </div>
            </td>
            <td>
              <button @click="toggleReply(comment.id)">Відповісти</button>
              <button
                v-if="isAuthor(comment)"
                @click="deleteComment(comment.id)"
                style="margin-left:8px;background:#c0392b;border:none;color:#fff;border-radius:4px;padding:6px 14px;cursor:pointer;"
              >
                Видалити
              </button>
              <div style="font-size:12px;color:#aaa;">
                user: {{ comment.user }} | current: {{ currentUser }}
              </div>
              <div v-if="replyToId === comment.id">
                <CommentForm :parentId="comment.id" @comment-added="handleReplySubmitted" />
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Пагинация -->
      <div v-if="count > pageSize" class="pagination">
        <button @click="prevPage" :disabled="page === 1">Назад</button>
        <span>Сторінка {{ page }}</span>
        <button @click="nextPage" :disabled="!next">Вперед</button>
      </div>
    </div>

    <!-- форма для додавання нового коментаря -->
    <CommentForm v-if="isAuthenticated" @comment-added="fetchComments" />
    <p v-else>Увійдіть, щоб залишити коментар</p>
    
    <!-- Lightbox -->
    <div v-if="lightboxImg" class="lightbox" @click="lightboxImg=null">
      <img :src="lightboxImg" style="max-width:90vw;max-height:90vh;" />
    </div>
  </div>
</template>

<script>
import CommentForm from './CommentForm.vue';
import { authFetch } from '../utils/authFetch';

export default {
  name: 'CommentList',
  components: { CommentForm },
  data() {
    return {
      comments: [],
      count: 0,
      next: null,
      previous: null,
      page: 1,
      pageSize: 25,
      ordering: '-created_at', // LIFO по умолчанию
      loading: false,
      replyToId: null, // ID коментаря, на який зараз відповідають
      lightboxImg: null,
    };
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access');
    },
    currentUser() {
      return localStorage.getItem('username');
    },
  },
  mounted() {
    this.fetchComments();
    this.connectWebSocket();
  },
  methods: {
    async fetchComments() {
      this.loading = true;
      const params = new URLSearchParams({
        page: this.page,
        ordering: this.ordering,
      });
      try {
        const headers = {};
        const token = localStorage.getItem('access');
        if (token) {
          headers.Authorization = 'Bearer ' + token;
        }
        const res = await authFetch(`http://54.196.231.54/api/comments/?${params}`, {
          headers,
          credentials: 'include'
        });
        if (res.status === 401) {
          // Токен невалиден — удаляем его
          localStorage.removeItem('access');
          // Можно также разлогинить пользователя, если нужно
          // this.$emit('logout');
          // Повторяем запрос без токена
          return this.fetchComments();
        }
        if (!res.ok) {
          this.comments = [];
          this.count = 0;
          this.next = null;
          this.previous = null;
          this.loading = false;
          return;
        }
        const data = await res.json();
        this.comments = data.results;
        this.count = data.count;
        this.next = data.next;
        this.previous = data.previous;
      } catch (e) {
        // обработка других ошибок
      }
      console.log(this.comments);
      this.loading = false;
    },
    logout() {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      this.$router.push('/login');
    },
    toggleReply(commentId) {
      this.replyToId = this.replyToId === commentId ? null : commentId;
    },
    async handleReplySubmitted() {
      this.replyToId = null;
      await this.fetchComments();
    },
    isImage(url) {
      return /\.(jpg|jpeg|png|gif)$/i.test(url);
    },
    openLightbox(url) {
      this.lightboxImg = url;
    },
    nextPage() {
      if (this.next) {
        this.page++;
        this.fetchComments();
      }
    },
    prevPage() {
      if (this.page > 1) {
        this.page--;
        this.fetchComments();
      }
    },
    setOrdering(field) {
      if (this.ordering === field) {
        this.ordering = '-' + field;
      } else if (this.ordering === '-' + field) {
        this.ordering = field;
      } else {
        this.ordering = field;
      }
      this.page = 1;
      this.fetchComments();
    },
    connectWebSocket() {
      const ws = new WebSocket('ws://54.196.231.54:8000/ws/comments/');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Можно просто обновить список, либо добавить комментарий в начало
        this.fetchComments();
      };
      ws.onclose = () => {
        // Автоматически переподключаться при разрыве
        setTimeout(this.connectWebSocket, 2000);
      };
      this.ws = ws;
    },
    isAuthor(comment) {
      const user = localStorage.getItem('username');
      return user && (user === comment.user);
    },
    async deleteComment(commentId) {
      if (!confirm('Удалить комментарий?')) return;
      const token = localStorage.getItem('access');
      try {
        const res = await fetch(`http://54.196.231.54/api/comments/${commentId}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.status === 204) {
          this.comments = this.comments.filter(c => c.id !== commentId);
        } else if (res.status === 403) {
          alert('Нет прав на удаление этого комментария');
        } else {
          alert('Ошибка удаления');
        }
      } catch (e) {
        alert('Ошибка сети');
      }
    },
  },
  beforeUnmount() {
    if (this.ws) this.ws.close();
  },
};
</script>

<style>
body {
  background: #18191a;
  color: #fff;
}

.comment {
  border: 1px solid #333;
  background: #232324;
  padding: 10px;
  margin-bottom: 10px;
  color: #fff;
}

.replies {
  margin-left: 20px;
}

.reply {
  background: #222226;
  color: #fff;
  padding: 5px;
  margin-top: 5px;
  border-left: 3px solid #444;
}

.logout-button {
  float: right;
  margin-bottom: 1rem;
  background: #232324;
  color: #fff;
  border: 1px solid #444;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}
.logout-button:hover {
  background: #333;
}

.lightbox {
  position: fixed;
  z-index: 1000;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(10,10,10,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
}
.lightbox img {
  box-shadow: 0 0 20px #000;
}

.pagination {
  margin-top: 10px;
}
.pagination button {
  background: #232324;
  color: #fff;
  border: 1px solid #444;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 4px;
  transition: background 0.2s;
}
.pagination button:disabled {
  background: #18191a;
  color: #666;
  border-color: #222;
  cursor: not-allowed;
}
.pagination span {
  color: #fff;
}

.comments-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  background: #18191a;
  color: #fff;
}
.comments-table th,
.comments-table td {
  border: 1px solid #333;
  padding: 8px;
  text-align: left;
  background: #232324;
  color: #fff;
}
.comments-table th {
  background-color: #222226;
  cursor: pointer;
  color: #fff;
}
.comments-table tr:nth-child(even) td {
  background: #1a1b1c;
}
.comments-table tr:hover td {
  background: #292a2d;
}

a, a:visited {
  color: #9ecbff;
  text-decoration: underline;
}
a:hover {
  color: #fff;
}

input, textarea {
  background: #232324;
  color: #fff;
  border: 1px solid #444;
  border-radius: 4px;
  padding: 6px;
  margin-bottom: 6px;
}
input:focus, textarea:focus {
  outline: none;
  border-color: #9ecbff;
}

button {
  background: #232324;
  color: #fff;
  border: 1px solid #444;
  border-radius: 4px;
  padding: 6px 14px;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover {
  background: #333;
}
</style>
