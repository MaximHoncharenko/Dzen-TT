<template>
  <div>
    <h2>Комментарии</h2>
    <ul>
      <li v-for="comment in comments" :key="comment.id">
        <strong>{{ comment.user.username }}:</strong>
        <span v-html="comment.text"></span>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Comments',
  data() {
    return {
      comments: [],
      socket: null,
    }
  },
  methods: {
    fetchComments() {
      axios.get('http://localhost:8000/api/comments/')
        .then(response => {
          this.comments = response.data
        })
        .catch(error => {
          console.error('Ошибка при загрузке комментариев:', error)
        })
    },
    setupWebSocket() {
      // Адрес WebSocket (зміни на свій, якщо потрібно)
      const wsScheme = window.location.protocol === "https:" ? "wss" : "ws"
      const wsPath = `${wsScheme}://localhost:8000/ws/comments/`
      this.socket = new WebSocket(wsPath)

      this.socket.onopen = () => {
        console.log('WebSocket подключен')
      }

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'new_comment') {
          this.comments.push(data.comment)
        }
      }

      this.socket.onclose = () => {
        console.log('WebSocket отключен')
      }

      this.socket.onerror = (error) => {
        console.error('WebSocket ошибка:', error)
      }
    }
  },
  mounted() {
    this.fetchComments()
    this.setupWebSocket()
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close()
    }
  }
}
</script>
