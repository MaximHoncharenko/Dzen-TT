<!-- CaptchaImage.vue -->
<template>
  <div>
    <img :src="captchaUrl" @click="refreshCaptcha" alt="CAPTCHA" style="cursor:pointer; border:1px solid #ccc; vertical-align:middle;" />
    <button type="button" @click="refreshCaptcha" style="margin-left:8px;">Оновити CAPTCHA</button>
  </div>
</template>

<script>
export default {
  name: "CaptchaImage",
  props: {
    apiUrl: {
      type: String,
      default: "http://56.228.36.74:8000/api/captcha/"
    }
  },
  data() {
    return {
      captchaUrl: this.apiUrl + "?t=" + Date.now()
    };
  },
  methods: {
    refreshCaptcha() {
      this.captchaUrl = this.apiUrl + "?t=" + Date.now();
    }
  }
};
</script>