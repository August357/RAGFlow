<template>
  <div class="config">
    <el-card>
      <template #header>
        <span>向量库配置</span>
      </template>
      
      <el-form :model="config" label-width="120px">
        <el-form-item label="Chunk大小">
          <el-input-number v-model="config.chunk_size" :min="100" :max="2000" />
          <span style="margin-left: 10px; color: #999">建议: 500-1000</span>
        </el-form-item>
        <el-form-item label="Chunk重叠">
          <el-input-number v-model="config.chunk_overlap" :min="0" :max="500" />
          <span style="margin-left: 10px; color: #999">建议: 50-200</span>
        </el-form-item>
        <el-form-item label="切分策略">
          <el-select v-model="config.split_mode">
            <el-option label="中文智能切分" value="zh" />
            <el-option label="段落切分" value="paragraph" />
            <el-option label="句子切分" value="sentence" />
          </el-select>
        </el-form-item>
        <el-form-item label="检索TopK">
          <el-input-number v-model="config.top_k" :min="1" :max="10" />
          <span style="margin-left: 10px; color: #999">建议: 3-5</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRebuild" :loading="rebuilding">
            应用配置并重建向量库
          </el-button>
          <el-button @click="resetConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>配置说明</span>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="Chunk大小">每个文本块的最大字符数，越大包含信息越多，但可能包含无关内容</el-descriptions-item>
        <el-descriptions-item label="Chunk重叠">相邻文本块之间的重叠字符数，用于保持上下文连贯性</el-descriptions-item>
        <el-descriptions-item label="切分策略">zh: 中文智能切分；paragraph: 按段落切分；sentence: 按句子切分</el-descriptions-item>
        <el-descriptions-item label="检索TopK">检索时返回的最相关文档数量</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getConfig, buildDb } from '@/api'

const config = ref({
  chunk_size: 500,
  chunk_overlap: 100,
  split_mode: 'zh',
  top_k: 5
})

const originalConfig = ref({ ...config.value })
const rebuilding = ref(false)

const fetchConfig = async () => {
  try {
    const response = await getConfig()
    config.value = response.data
    originalConfig.value = { ...response.data }
  } catch (error) {
    ElMessage.error('获取配置失败')
  }
}

const handleRebuild = async () => {
  try {
    rebuilding.value = true
    const response = await buildDb(config.value)
    
    if (response.data.success) {
      ElMessage.success('配置已应用并重建向量库成功')
      originalConfig.value = { ...config.value }
    } else {
      ElMessage.error('重建失败')
    }
  } catch (error) {
    ElMessage.error('重建失败: ' + error.message)
  } finally {
    rebuilding.value = false
  }
}

const resetConfig = () => {
  config.value = { ...originalConfig.value }
  ElMessage.info('已重置为当前配置')
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.config {
  padding: 20px;
}
</style>