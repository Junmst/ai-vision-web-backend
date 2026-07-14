<template>
  <!-- AI 配置页：表单 + 卡片列表，参考 GPT 设置页风格 -->
  <section class="config-layout">
    <!-- 新增/编辑配置表单 -->
    <div class="config-form-card">
      <h2>{{ editingId ? "编辑配置" : "新增 AI 配置" }}</h2>
      <p class="subtitle">管理你的云端模型配置，用于图像分析时调用对应的 AI 服务</p>

      <form class="stack" @submit.prevent="handleSubmit">
        <div class="config-grid">
          <label>
            配置名称
            <input v-model.trim="form.config_name" placeholder="例如：我的视觉模型" required />
          </label>

          <label>
            Provider
            <select v-model="form.provider">
              <option value="cloud">cloud（云端 API）</option>
              <option value="local">local（预留，暂不可用）</option>
            </select>
          </label>

          <label>
            Base URL
            <input v-model.trim="form.base_url" placeholder="https://api.example.com/v1" />
          </label>

          <label>
            API Key
            <input v-model.trim="form.api_key" :placeholder="editingId ? '留空则不更新' : 'sk-...'" />
          </label>

          <label>
            鉴权方式
            <select v-model="form.auth_mode">
              <option value="bearer">Bearer Token（Authorization: Bearer xxx）</option>
              <option value="api-key">API Key（自定义 Header）</option>
            </select>
          </label>

          <label v-if="form.auth_mode === 'api-key'">
            Header 名称
            <input v-model.trim="form.auth_header" placeholder="例如：X-API-Key" />
          </label>

          <label>
            模型名称
            <input v-model.trim="form.model_name" placeholder="例如：gpt-4o" />
          </label>

          <label class="checkbox-line" style="align-self: end">
            <input type="checkbox" v-model="form.is_default" />
            设为默认配置
          </label>
        </div>

        <div class="actions" style="margin-top: 8px">
          <button class="primary" type="submit">
            {{ editingId ? "更新配置" : "新增配置" }}
          </button>
          <button class="ghost" type="button" @click="resetForm" v-if="editingId">取消编辑</button>
          <button class="ghost" type="button" @click="resetForm" v-else>重置</button>
        </div>
      </form>

      <p class="error" v-if="errorText" style="margin-top: 12px">{{ errorText }}</p>
    </div>

    <!-- 已有配置列表 -->
    <div>
      <div class="history-header">
        <h2 style="font-size: 18px; font-weight: 600">已有配置</h2>
        <span class="history-count" v-if="configs.length">{{ configs.length }} 个</span>
      </div>

      <!-- 骨架屏加载态 -->
      <div v-if="loading" class="config-list" style="margin-top: 12px">
        <div v-for="n in 3" :key="'skeleton-' + n" class="config-card" style="pointer-events: none">
          <div class="skeleton-icon"></div>
          <div class="skeleton-body" style="flex: 1">
            <div class="skeleton-line skeleton-line-title"></div>
            <div class="skeleton-line skeleton-line-desc" style="width: 180px"></div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!configs.length" class="empty-state" style="padding: 40px">
        <div class="empty-icon">⚙️</div>
        <h3>暂无配置</h3>
        <p>在上方表单中新增一个 AI 模型配置</p>
      </div>

      <!-- 配置卡片列表 -->
      <div v-else-if="configs.length" class="config-list" style="margin-top: 12px">
        <div v-for="item in configs" :key="item.id" class="config-card">
          <!-- 图标 -->
          <div class="config-card-icon">🔑</div>

          <!-- 信息 -->
          <div class="config-card-body">
            <div class="config-card-title">
              {{ item.config_name }}
              <span class="default-badge" v-if="item.is_default">默认</span>
            </div>
            <div class="config-card-meta">
              <span>{{ item.provider }}</span>
              <span>{{ item.auth_mode === 'api-key' ? 'API-Key' : 'Bearer' }}</span>
              <span>{{ item.model_name || "未指定模型" }}</span>
            </div>
          </div>

          <!-- 操作 -->
          <div class="config-card-actions">
            <button class="ghost btn-sm" @click="startEdit(item)">编辑</button>
            <button class="danger btn-sm" @click="handleDelete(item.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { createAIConfig, deleteAIConfig, listAIConfigs, updateAIConfig } from "../api/aiConfigs";

const configs = ref([]);
const loading = ref(false);
const errorText = ref("");
const editingId = ref(0);

// 配置表单状态
const form = reactive({
  config_name: "默认配置",
  provider: "cloud",
  base_url: "",
  api_key: "",
  auth_mode: "bearer",
  auth_header: "Authorization",
  model_name: "",
  is_default: false,
});

function resetForm() {
  editingId.value = 0;
  form.config_name = "默认配置";
  form.provider = "cloud";
  form.base_url = "";
  form.api_key = "";
  form.auth_mode = "bearer";
  form.auth_header = "Authorization";
  form.model_name = "";
  form.is_default = false;
}

// 加载配置列表
async function loadConfigs() {
  loading.value = true;
  try {
    configs.value = await listAIConfigs();
  } catch (error) {
    errorText.value = error.message || "配置加载失败";
  } finally {
    loading.value = false;
  }
}

// 进入编辑模式：填充表单
function startEdit(item) {
  editingId.value = item.id;
  form.config_name = item.config_name;
  form.provider = item.provider;
  form.base_url = item.base_url;
  form.api_key = "";  // api_key 不回显，留空表示不更新
  form.auth_mode = item.auth_mode || "bearer";
  form.auth_header = item.auth_header || "Authorization";
  form.model_name = item.model_name;
  form.is_default = !!item.is_default;
}

// 提交新增或更新
async function handleSubmit() {
  errorText.value = "";
  try {
    const payload = {
      config_name: form.config_name,
      provider: form.provider,
      base_url: form.base_url,
      auth_mode: form.auth_mode,
      auth_header: form.auth_mode === "api-key" ? form.auth_header : "Authorization",
      model_name: form.model_name,
      is_default: form.is_default ? 1 : 0,
    };

    // api_key 仅在有值时才提交（编辑时留空表示不更新）
    if (form.api_key) {
      payload.api_key = form.api_key;
    }

    if (editingId.value) {
      await updateAIConfig(editingId.value, payload);
    } else {
      payload.api_key = payload.api_key || "";
      await createAIConfig(payload);
    }

    resetForm();
    await loadConfigs();
  } catch (error) {
    errorText.value = error.message || "保存失败";
  }
}

// 删除配置：需二次确认，防止误操作
async function handleDelete(id) {
  if (!confirm("确定要删除这个 AI 配置吗？此操作不可恢复。")) return;
  try {
    await deleteAIConfig(id);
    await loadConfigs();
  } catch (error) {
    errorText.value = error.message || "删除失败";
  }
}

onMounted(loadConfigs);
</script>
