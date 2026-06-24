<template>
  <div class="chat">
    <el-card>
      <el-input
        v-model="query"
        type="textarea"
        :rows="3"
        placeholder="请输入你的问题..."
        @keydown.ctrl.enter="handleSend"
      />
      <div style="margin-top: 10px; text-align: right">
        <el-button type="primary" @click="handleSend" :loading="loading">
          发送 (Ctrl+Enter)
        </el-button>
      </div>
    </el-card>

    <el-card v-if="answer" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>AI回答</span>
          <el-tag type="info">上下文: {{ contextLength }} 字符</el-tag>
        </div>
      </template>
      <div class="answer-content">{{ answer }}</div>
      
      <el-divider v-if="sources.length > 0" />
      
      <div v-if="sources.length > 0">
        <h4>参考来源：</h4>
        <el-table :data="sources" style="width: 100%">
          <el-table-column prop="source" label="来源文件" width="200" />
          <el-table-column prop="page" label="页码" width="100" />
          <el-table-column prop="chunk_id" label="Chunk编号" width="120" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ask } from '@/api'

const query = ref('')
const answer = ref('')
const sources = ref([])
const contextLength = ref(0)
const loading = ref(false)

const handleSend = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  loading.value = true
  try {
    const response = await ask(query.value)
    answer.value = response.data.answer
    sources.value = response.data.sources || []
    contextLength.value = response.data.context_length || 0
  } catch (error) {
    ElMessage.error('问答失败: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat {
  padding: 20px;
}

.answer-content {
  white-space: pre-wrap;
  line-height: 1.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>