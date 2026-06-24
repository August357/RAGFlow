<template>

<MainLayout>

<div class="chunk-page pixel-card">

<h2>Chunk 管理</h2>

<p class="hint">
按文档查看切片。内容在<strong>重建向量库</strong>时生成，不会随每次提问变化；问答实际引用的 Chunk 见聊天「来源」。
</p>

<div class="toolbar">
  <el-button @click="load" :loading="loading">刷新</el-button>
  <span v-if="total > 0" class="stats">
    {{ documentCount }} 个文档 · {{ total }} 个 Chunk
  </span>
</div>

<el-empty v-if="!loading && documents.length === 0" description="暂无 Chunk，请先重建向量库" />

<div v-else class="layout">

  <!-- 文档列表 -->
  <div class="doc-list">
    <div class="doc-list-title">文档列表</div>
    <el-input
      v-model="keyword"
      placeholder="搜索文档名..."
      clearable
      class="doc-search"
    />
    <div class="doc-items">
      <div
        v-for="doc in filteredDocuments"
        :key="doc.source"
        class="doc-item"
        :class="{ active: selectedSource === doc.source }"
        @click="selectDocument(doc.source)"
      >
        <div class="doc-name" :title="doc.source">📄 {{ doc.source }}</div>
        <div class="doc-meta">{{ doc.chunk_count }} 片 · {{ doc.total_length }} 字</div>
      </div>
    </div>
  </div>

  <!-- 切片详情 -->
  <div class="chunk-panel">
    <template v-if="currentDocument">
      <div class="panel-header">
        <h3>{{ currentDocument.source }}</h3>
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="list">分片列表</el-radio-button>
          <el-radio-button label="merged">合并预览</el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="viewMode === 'list'" class="chunk-list">
        <el-collapse v-model="activeChunks">
          <el-collapse-item
            v-for="chunk in currentDocument.chunks"
            :key="chunk.chunk_id"
            :name="chunk.chunk_id"
          >
            <template #title>
              <span class="chunk-title">
                Chunk {{ chunk.chunk_id }}
                <el-tag size="small" type="info">P{{ chunk.page }}</el-tag>
                <el-tag size="small">{{ chunk.length }} 字</el-tag>
              </span>
            </template>
            <pre class="chunk-content">{{ chunk.content }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>

      <pre v-else class="merged-box">{{ mergedContent }}</pre>
    </template>

    <el-empty v-else description="请从左侧选择文档" />
  </div>

</div>

</div>

</MainLayout>

</template>

<script setup>

import { ref, computed, onMounted } from "vue";
import MainLayout from "../layouts/MainLayout.vue";
import { getChunks } from "../api/rag";

const loading = ref(false);
const documents = ref([]);
const total = ref(0);
const documentCount = ref(0);
const selectedSource = ref("");
const viewMode = ref("list");
const activeChunks = ref([]);
const keyword = ref("");

const filteredDocuments = computed(() => {
  const kw = keyword.value.trim().toLowerCase();
  if (!kw) return documents.value;
  return documents.value.filter((d) => d.source.toLowerCase().includes(kw));
});

const currentDocument = computed(() =>
  documents.value.find((d) => d.source === selectedSource.value) || null
);

const mergedContent = computed(() => {
  if (!currentDocument.value) return "";
  return currentDocument.value.chunks
    .map((c, i) => `--- Chunk ${c.chunk_id} (P${c.page}) ---\n${c.content}`)
    .join("\n\n");
});

const selectDocument = (source) => {
  selectedSource.value = source;
  const doc = documents.value.find((d) => d.source === source);
  activeChunks.value = doc?.chunks?.length ? [doc.chunks[0].chunk_id] : [];
  viewMode.value = "list";
};

const load = async () => {
  loading.value = true;
  try {
    const res = await getChunks();
    documents.value = res.data.documents || [];
    total.value = res.data.total || 0;
    documentCount.value = res.data.document_count || documents.value.length;

    if (documents.value.length === 0) {
      selectedSource.value = "";
      return;
    }

    const stillExists = documents.value.some((d) => d.source === selectedSource.value);
    if (!stillExists) {
      selectDocument(documents.value[0].source);
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => load());

</script>

<style scoped>

.chunk-page {
  padding: 20px;
  min-height: calc(100vh - 80px);
}

.hint {
  color: #666;
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.stats {
  color: #888;
  font-size: 13px;
}

.layout {
  display: flex;
  gap: 16px;
  min-height: 620px;
}

.doc-list {
  width: 280px;
  flex-shrink: 0;
  border: 2px solid #333;
  background: #fafafa;
  display: flex;
  flex-direction: column;
}

.doc-list-title {
  padding: 12px;
  font-weight: bold;
  border-bottom: 2px solid #333;
  background: #eee;
}

.doc-search {
  padding: 8px;
}

.doc-items {
  overflow-y: auto;
  flex: 1;
  max-height: 560px;
}

.doc-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
  transition: background 0.15s;
}

.doc-item:hover {
  background: #f0f0f0;
}

.doc-item.active {
  background: #e8f4ff;
  border-left: 4px solid #409eff;
}

.doc-name {
  font-size: 13px;
  word-break: break-all;
  line-height: 1.4;
}

.doc-meta {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.chunk-panel {
  flex: 1;
  border: 2px solid #333;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.panel-header h3 {
  margin: 0;
  font-size: 15px;
  word-break: break-all;
  flex: 1;
}

.chunk-list {
  overflow-y: auto;
  flex: 1;
}

.chunk-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.chunk-content,
.merged-box {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  padding: 12px;
  background: #f9f9f9;
  border: 1px solid #eee;
  max-height: 400px;
  overflow-y: auto;
}

.merged-box {
  flex: 1;
  max-height: none;
  height: 100%;
}

</style>
