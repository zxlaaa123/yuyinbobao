<script setup lang="ts">
</script>

<template>
  <div class="dashboard">
    <div class="hero-card">
      <h1>AI 知识点学习与音频播报系统</h1>
      <p>本地学习辅助工具</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 100px);
}

.hero-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 24px;
  box-shadow: 0 18px 45px rgba(25, 36, 70, 0.09);
  padding: 60px 48px;
  text-align: center;
  max-width: 560px;
  width: 100%;
}

.hero-card h1 {
  font-size: 28px;
  letter-spacing: -0.04em;
  margin: 0 0 12px;
  background: linear-gradient(135deg, #4f7cff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-card p {
  margin: 0;
  color: #667085;
  font-size: 16px;
}
</style>
