<template>
  <!-- 认证页：居中卡片布局，参考 GPT 登录页简洁风格 -->
  <section class="auth-layout">
    <div class="auth-card">
      <!-- 品牌标识区 -->
      <div class="brand">
        <span class="brand-dot"></span>
        <div>
          <h1>AI Vision Web</h1>
          <p>基于多模态 AI 的图像识别与语义分析系统</p>
        </div>
      </div>

      <h2>{{ isLoginMode ? "欢迎回来" : "创建账号" }}</h2>
      <p class="subtitle">{{ isLoginMode ? "登录以继续使用图像分析功能" : "注册一个新账号" }}</p>

      <!-- 登录/注册表单 -->
      <form class="stack" @submit.prevent="handleSubmit">
        <label>
          用户名
          <input v-model.trim="form.username" placeholder="请输入用户名" required minlength="3" maxlength="64" />
        </label>

        <label>
          密码
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
            minlength="6"
            maxlength="128"
          />
        </label>

        <button class="primary" type="submit" :disabled="loading" style="margin-top: 4px">
          {{ loading ? "提交中..." : isLoginMode ? "登录" : "注册" }}
        </button>
      </form>

      <!-- 错误提示 -->
      <p class="error" v-if="errorText">{{ errorText }}</p>

      <!-- 切换登录/注册 -->
      <button class="ghost" @click="toggleMode" style="width: 100%; margin-top: 8px">
        {{ isLoginMode ? "没有账号？去注册" : "已有账号？去登录" }}
      </button>

      <!-- 测试入口提示 -->
      <p class="demo-tip">测试快捷入口：admin / 123456（无需后端）</p>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { login, register } from "../api/auth";
import { setToken } from "../stores/authStore";

const router = useRouter();
const isLoginMode = ref(true);
const loading = ref(false);
const errorText = ref("");

// 认证页统一表单状态，避免登录和注册维护两份重复数据
const form = reactive({
  username: "",
  password: "",
});

function toggleMode() {
  isLoginMode.value = !isLoginMode.value;
  errorText.value = "";
}

// 提交登录或注册
async function handleSubmit() {
  loading.value = true;
  errorText.value = "";
  try {
    // 纯前端演示登录：admin/123456 无需后端即可进入系统
    if (isLoginMode.value && form.username === "admin" && form.password === "123456") {
      setToken("demo-admin-token");
      router.push("/workbench");
      return;
    }

    if (isLoginMode.value) {
      const tokenData = await login(form);
      setToken(tokenData.access_token);
    } else {
      await register(form);
      const tokenData = await login(form);
      setToken(tokenData.access_token);
    }
    router.push("/workbench");
  } catch (error) {
    errorText.value = error.message || "操作失败";
  } finally {
    loading.value = false;
  }
}
</script>
