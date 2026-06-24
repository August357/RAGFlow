<template>
  <div class="chunk">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Chunk切片信息</span>
          <el-button @click="fetchChunks" :icon="Refresh">刷新</el-button>
        </div>
      </template>
      
      <el-input
        v-model="searchKeyword"
        placeholder="搜索Chunk内容..."
        @input="handleSearch"
        clearable
        style="margin-bottom: 20px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-input
        v-model="chunkText"
        type="textarea"
        :rows="25"
        readonly
        class="chunk-textarea"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getChunks } from '@/api'

const chunkText = ref('')
const searchKeyword = ref('')
const originalContent = ref('')

const fetchChunks = async () => {
  try {
    const response = await getChunks()
    originalContent.value = response.data.content || '暂无Chunk信息'
    chunkText.value = originalContent.value
  } catch (error) {
    ElMessage.error('获取Chunk信息失败')
  }
}

const handleSearch = () => {
  if (!searchKeyword.value) {
    chunkText.value = originalContent.value
    return
  }
  
  const lines = originalContent.value.split('\n')
  const filtered = lines.filter(line => 
    line.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
  chunkText.value = filtered.join('\n') || '未找到匹配内容'
}

onMounted(() => {
  fetchChunks()
})
</script>

<style scoped>
.chunk {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chunk-textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}
</style>