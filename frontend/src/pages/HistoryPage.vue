<template>
  <!-- 历史记录页：搜索 + 筛选 + 排序 + 卡片列表 -->
  <section class="history-layout">
    <!-- 页面标题区 -->
    <div class="history-header">
      <h2>分析历史</h2>
      <span class="history-count" v-if="records.length">
        {{ filteredRecords.length }} / {{ records.length }} 条记录
      </span>
    </div>

    <!-- 搜索与筛选工具栏 -->
    <div class="filter-bar" v-if="records.length">
      <!-- 搜索框：按描述/标签/模型名关键词搜索 -->
      <div class="filter-search">
        <input
          v-model.trim="searchKeyword"
          placeholder="搜索关键词..."
          @keyup.enter="searchKeyword = searchKeyword"
        />
      </div>

      <!-- 类型筛选 -->
      <select v-model="filterType" class="filter-select">
        <option value="all">全部类型</option>
        <option value="all">all</option>
        <option value="describe">describe</option>
        <option value="tags">tags</option>
        <option value="scene">scene</option>
        <option value="prompt">prompt</option>
      </select>

      <!-- 排序方式 -->
      <select v-model="sortOrder" class="filter-select">
        <option value="newest">最新优先</option>
        <option value="oldest">最早优先</option>
        <option value="id_desc">ID 降序</option>
        <option value="id_asc">ID 升序</option>
      </select>
    </div>

    <!-- 错误提示 -->
    <p class="error" v-if="errorText">{{ errorText }}</p>

    <!-- 骨架屏加载态 -->
    <div v-if="loading" class="history-list">
      <div v-for="n in 4" :key="'skeleton-' + n" class="history-card skeleton-card">
        <div class="skeleton-icon"></div>
        <div class="skeleton-body">
          <div class="skeleton-line skeleton-line-title"></div>
          <div class="skeleton-line skeleton-line-desc"></div>
        </div>
        <div class="skeleton-line skeleton-line-time"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!records.length" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>暂无分析记录</h3>
      <p>前往工作台上传图片并分析，结果将自动保存到这里</p>
    </div>

    <!-- 搜索无结果 -->
    <div v-else-if="!filteredRecords.length" class="empty-state" style="padding: 30px">
      <div class="empty-icon">🔍</div>
      <h3>无匹配结果</h3>
      <p>尝试调整搜索关键词或筛选条件</p>
    </div>

    <!-- 历史记录卡片列表 -->
    <div v-else class="history-list">
      <div v-for="item in filteredRecords" :key="item.id" class="history-card">
        <!-- 左侧图标 -->
        <div class="history-card-icon">🖼️</div>

        <!-- 中间信息 -->
        <div class="history-card-body">
          <div class="history-card-title">
            分析 #{{ item.id }}
            <span class="ai-tag" style="font-size: 11px; padding: 2px 8px">{{ item.analysis_type }}</span>
          </div>
          <div class="history-card-desc" v-if="getPreview(item.result_json)">
            {{ getPreview(item.result_json) }}
          </div>
          <div class="history-card-desc" v-else>
            模型：{{ item.model_name || "未指定" }} · 图片ID：{{ item.image_id }}
          </div>
        </div>

        <!-- 右侧时间 -->
        <div class="history-card-time">{{ formatDate(item.created_at) }}</div>

        <!-- 操作按钮 -->
        <div class="history-card-actions">
          <button class="ghost btn-sm" @click="openEditor(item)">编辑</button>
          <button class="danger btn-sm" @click="handleDelete(item.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗：修改 result_json 内容 -->
    <dialog ref="editorRef" class="dialog">
      <div class="dialog-header">
        <h3>编辑分析结果 #{{ editing?.id }}</h3>
        <button class="ghost btn-sm" @click="closeEditor">✕</button>
      </div>
      <div class="dialog-body">
        <p style="font-size: 13px; color: var(--ink-secondary); margin-bottom: 12px">
          编辑 result_json 字符串内容（修改后前端会自动重新解析展示）
        </p>
        <textarea v-model="editingText" rows="14" style="font-family: monospace; font-size: 13px"></textarea>
      </div>
      <div class="dialog-footer">
        <button class="ghost" @click="closeEditor">取消</button>
        <button class="primary" @click="handleSaveEdit">保存修改</button>
      </div>
    </dialog>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { deleteAnalysis, listAnalysis, updateAnalysis } from "../api/analysis";
import { parseResult } from "../utils/result";

const records = ref([]);
const loading = ref(false);
const errorText = ref("");
const editing = ref(null);
const editingText = ref("");
const editorRef = ref(null);

// 筛选与排序状态
const searchKeyword = ref("");
const filterType = ref("all");
const sortOrder = ref("newest");

// 根据搜索关键词和类型筛选，再排序
const filteredRecords = computed(() => {
  let result = [...records.value];

  // 按类型筛选
  if (filterType.value !== "all") {
    result = result.filter((item) => item.analysis_type === filterType.value);
  }

  // 按关键词搜索（匹配 description / tags / scene / prompt / model_name）
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase();
    result = result.filter((item) => {
      const parsed = parseResult(item.result_json);
      const searchable = [
        parsed.description,
        parsed.scene,
        parsed.prompt,
        parsed.tags.join(" "),
        item.model_name || "",
      ]
        .join(" ")
        .toLowerCase();
      return searchable.includes(kw);
    });
  }

  // 排序
  switch (sortOrder.value) {
    case "newest":
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      break;
    case "oldest":
      result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      break;
    case "id_desc":
      result.sort((a, b) => b.id - a.id);
      break;
    case "id_asc":
      result.sort((a, b) => a.id - b.id);
      break;
  }

  return result;
});

// 从 result_json 中提取简短预览文本
function getPreview(resultJson) {
  const parsed = parseResult(resultJson);
  return parsed.description || parsed.scene || parsed.prompt || "";
}

// 格式化日期为可读字符串
function formatDate(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("zh-CN");
}

// 加载分析历史列表
async function loadRecords() {
  loading.value = true;
  errorText.value = "";
  try {
    records.value = await listAnalysis();
  } catch (error) {
    errorText.value = error.message || "加载历史失败";
  } finally {
    loading.value = false;
  }
}

// 打开编辑弹窗
function openEditor(item) {
  editing.value = item;
  editingText.value = item.result_json || "";
  editorRef.value?.showModal();
}

function closeEditor() {
  editorRef.value?.close();
}

// 保存编辑结果
async function handleSaveEdit() {
  if (!editing.value) return;
  try {
    await updateAnalysis(editing.value.id, { result_json: editingText.value });
    closeEditor();
    await loadRecords();
  } catch (error) {
    errorText.value = error.message || "更新失败";
  }
}

// 删除分析记录：需二次确认
async function handleDelete(id) {
  if (!confirm("确定要删除这条分析记录吗？此操作不可恢复。")) return;
  try {
    await deleteAnalysis(id);
    await loadRecords();
  } catch (error) {
    errorText.value = error.message || "删除失败";
  }
}

onMounted(loadRecords);
</script>
