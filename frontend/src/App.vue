<template>
  <div class="app-shell">
    <!-- 顶部导航栏：参考 GPT 窄栏设计，品牌 + 导航 + 退出 -->
    <header class="topbar" v-if="showTopbar">
      <div class="brand">
        <span class="brand-dot"></span>
        <h1>AI Vision Web</h1>
      </div>
      <nav class="topnav">
        <RouterLink to="/workbench">工作台</RouterLink>
        <RouterLink to="/history">历史记录</RouterLink>
        <RouterLink to="/ai-configs">AI 配置</RouterLink>
        <button class="ghost topbar-btn" @click="logout">退出</button>
      </nav>
    </header>

    <!-- 页面内容区 -->
    <main class="page-wrap">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter, RouterLink, RouterView } from "vue-router";
import { clearToken, getToken } from "./stores/authStore";

const route = useRoute();
const router = useRouter();

// 登录注册页不显示顶部导航，避免干扰登录操作
const showTopbar = computed(() => !["/auth"].includes(route.path) && !!getToken());

// 退出登录：清空 token 并跳转到登录页
function logout() {
  clearToken();
  router.push("/auth");
}
</script>
