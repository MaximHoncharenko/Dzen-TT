<template>
  <div>
    <h1>Коментарі</h1>
    <CommentList />
  </div>
</template>

<script>
import CommentList from '../components/CommentList.vue'

export default {
  name: 'CommentPage',
  components: {
    CommentList
  }
}
</script>
