<template>
  <!-- 工作台：左侧输入 + 右侧 AI 回答，类 ChatGPT 对话布局 -->
  <section class="workbench-layout">
    <!-- 左侧：输入面板 -->
    <aside class="panel input-panel">
      <h2>图像分析</h2>
      <p class="subtitle">上传图片，选择分析类型，获取 AI 语义理解结果</p>

      <!-- 上传区 -->
      <div class="input-section">
        <div class="input-section-title">1. 上传图片</div>
        <div class="upload-zone" :class="{ 'has-file': selectedFile }">
          <input
            ref="fileInputRef"
            type="file"
            accept="image/png,image/jpeg,image/gif,image/webp"
            @change="onFileChange"
          />
          <div class="upload-icon">{{ selectedFile ? "✅" : "📁" }}</div>
          <div class="upload-text" v-if="!selectedFile">
            点击选择图片，或拖拽到此处<br>
            <strong>支持 JPG / PNG / GIF / WEBP，最大 10MB</strong>
          </div>
          <div class="upload-text" v-else>
            已选择：<strong>{{ selectedFile.name }}</strong>
            <span v-if="selectedFile.size">（{{ formatFileSize(selectedFile.size) }}）</span>
          </div>
        </div>
        <button
          class="primary"
          style="width: 100%; margin-top: 10px"
          :disabled="!selectedFile || uploading"
          @click="handleUpload"
        >
          {{ uploading ? "上传中..." : "上传图片" }}
        </button>
      </div>

      <!-- 分析配置区 -->
      <div class="input-section">
        <div class="input-section-title">2. 配置分析</div>
        <div class="stack">
          <label>
            选择图片
            <select v-model.number="analysisForm.image_id">
              <option :value="0" disabled>请选择已上传图片</option>
              <option v-for="item in images" :key="item.id" :value="item.id">
                #{{ item.id }} - {{ item.filename }}
              </option>
            </select>
          </label>

          <label>
            分析类型
            <select v-model="analysisForm.analysis_type">
              <option value="all">all（完整分析）</option>
              <option value="describe">describe（内容描述）</option>
              <option value="tags">tags（标签提取）</option>
              <option value="scene">scene（场景识别）</option>
              <option value="prompt">prompt（反推提示词）</option>
            </select>
          </label>

          <label>
            AI 配置（可选）
            <select v-model.number="analysisForm.ai_config_id">
              <option :value="0">默认配置</option>
              <option v-for="item in aiConfigs" :key="item.id" :value="item.id">
                #{{ item.id }} - {{ item.config_name }}
              </option>
            </select>
          </label>
        </div>
      </div>

      <!-- 提交按钮 -->
      <button
        class="primary"
        style="width: 100%"
        :disabled="analyzing || !analysisForm.image_id"
        @click="handleAnalyze"
      >
        {{ analyzing ? "分析中..." : "开始分析" }}
      </button>

      <!-- 错误提示 -->
      <p class="error" v-if="errorText" style="margin-top: 12px">{{ errorText }}</p>
    </aside>

    <!-- 右侧：AI 回答面板 -->
    <section class="panel response-panel">
      <h2>AI 回答</h2>
      <p class="subtitle">结果将同步保存到历史记录，可后续查看和编辑</p>

      <!-- 分析中：骨架屏加载态 -->
      <div v-if="analyzing" class="ai-bubble" style="animation: skeleton-pulse 1.5s ease-in-out infinite">
        <div class="ai-bubble-header">
          <div class="ai-avatar"></div>
          <div class="ai-bubble-meta">AI Vision · 正在分析中...</div>
        </div>
        <div class="result-grid">
          <div class="result-card">
            <div class="skeleton-line skeleton-line-title" style="width: 100px; height: 11px; margin-bottom: 8px"></div>
            <div class="skeleton-line" style="height: 14px; width: 90%; margin-bottom: 6px"></div>
            <div class="skeleton-line" style="height: 14px; width: 70%"></div>
          </div>
          <div class="result-card">
            <div class="skeleton-line skeleton-line-title" style="width: 80px; height: 11px; margin-bottom: 8px"></div>
            <div style="display: flex; gap: 6px">
              <div class="skeleton-line" style="height: 24px; width: 60px; border-radius: 999px"></div>
              <div class="skeleton-line" style="height: 24px; width: 50px; border-radius: 999px"></div>
              <div class="skeleton-line" style="height: 24; width: 70px; border-radius: 999px"></div>
            </div>
          </div>
          <div class="result-card">
            <div class="skeleton-line skeleton-line-title" style="width: 80px; height: 11px; margin-bottom: 8px"></div>
            <div class="skeleton-line" style="height: 14px; width: 60%"></div>
          </div>
        </div>
      </div>

      <!-- 有分析结果时：展示 AI 回答气泡 -->
      <div v-else-if="latestResult" class="ai-bubble">
        <div class="ai-bubble-header">
          <div class="ai-avatar"></div>
          <div class="ai-bubble-meta">
            AI Vision · {{ latestResult.model_name || "vision-model" }} · {{ latestResult.analysis_type }}
            <span v-if="latestResult.latency"> · 耗时 {{ latestResult.latency }}s</span>
          </div>
        </div>

        <div class="result-grid">
          <!-- 内容描述 -->
          <div class="result-card" v-if="parsedResult.description">
            <div class="result-card-label">内容描述</div>
            <div class="result-card-value">{{ parsedResult.description }}</div>
          </div>

          <!-- 标签 -->
          <div class="result-card" v-if="parsedResult.tags.length">
            <div class="result-card-label">标签提取</div>
            <div class="ai-tags">
              <span v-for="tag in parsedResult.tags" :key="tag" class="ai-tag">{{ tag }}</span>
            </div>
          </div>

          <!-- 场景 -->
          <div class="result-card" v-if="parsedResult.scene">
            <div class="result-card-label">场景识别</div>
            <div class="result-card-value">{{ parsedResult.scene }}</div>
          </div>

          <!-- Prompt 反推 -->
          <div class="result-card" v-if="parsedResult.prompt">
            <div class="result-card-label">Prompt 反推</div>
            <div class="result-card-value">{{ parsedResult.prompt }}</div>
          </div>
        </div>
      </div>

      <!-- 无结果时：空状态引导 -->
      <div v-else class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>等待分析</h3>
        <p>上传一张图片并选择分析类型，AI 将为你生成语义分析结果</p>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { createAnalysis } from "../api/analysis";
import { listAIConfigs } from "../api/aiConfigs";
import { listImages, uploadImage } from "../api/images";
import { parseResult } from "../utils/result";

const images = ref([]);
const aiConfigs = ref([]);
const selectedFile = ref(null);
const fileInputRef = ref(null);
const uploading = ref(false);
const analyzing = ref(false);
const errorText = ref("");
const latestResult = ref(null);

// 分析表单状态
const analysisForm = reactive({
  image_id: 0,
  analysis_type: "all",
  ai_config_id: 0,
});

// 解析 result_json 字符串为对象
const parsedResult = computed(() => parseResult(latestResult.value?.result_json || ""));

// 格式化文件大小为可读字符串（KB/MB）
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function onFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null;
}

// 加载图片列表和 AI 配置列表
async function loadBaseData() {
  const [imageData, configData] = await Promise.all([listImages(), listAIConfigs()]);
  images.value = imageData;
  aiConfigs.value = configData;
  if (!analysisForm.image_id && imageData.length) {
    analysisForm.image_id = imageData[0].id;
  }
}

// 上传图片：完成后自动选中最新图片
async function handleUpload() {
  if (!selectedFile.value) return;
  uploading.value = true;
  errorText.value = "";
  try {
    const image = await uploadImage(selectedFile.value);
    await loadBaseData();
    analysisForm.image_id = image.id;
    selectedFile.value = null;
    // 重置 file input 的 DOM 值，确保视觉和内部状态一致
    if (fileInputRef.value) {
      fileInputRef.value.value = "";
    }
  } catch (error) {
    errorText.value = error.message || "上传失败";
  } finally {
    uploading.value = false;
  }
}

// 发起分析：同步调用后端 AI 接口
async function handleAnalyze() {
  if (!analysisForm.image_id) {
    errorText.value = "请先选择图片";
    return;
  }
  analyzing.value = true;
  errorText.value = "";
  try {
    const payload = {
      image_id: analysisForm.image_id,
      analysis_type: analysisForm.analysis_type,
    };
    if (analysisForm.ai_config_id) {
      payload.ai_config_id = analysisForm.ai_config_id;
    }
    latestResult.value = await createAnalysis(payload);
  } catch (error) {
    errorText.value = error.message || "分析失败";
  } finally {
    analyzing.value = false;
  }
}

onMounted(async () => {
  try {
    await loadBaseData();
  } catch (error) {
    errorText.value = error.message || "加载失败";
  }
});
</script>
