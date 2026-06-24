<template>
  <div class="system">
    <el-card>
      <template #header>
        <span>系统状态</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="status-card" :class="{ success: status.ready }">
            <div class="status-icon">
              <el-icon size="32"><CircleCheck /></el-icon>
            </div>
            <div class="status-text">
              <span class="status-label">系统状态</span>
              <span class="status-value">{{ status.ready ? '运行中' : '离线' }}</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="status-card">
            <div class="status-icon">
              <el-icon size="32"><Cpu /></el-icon>
            </div>
            <div class="status-text">
              <span class="status-label">设备</span>
              <span class="status-value">{{ status.device }}</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="status-card">
            <div class="status-icon">
              <el-icon size="32"><Database /></el-icon>
            </div>
            <div class="status-text">
              <span class="status-label">向量库</span>
              <span class="status-value">{{ status.vectorDb ? '已加载' : '未加载' }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>模型信息</span>
      </template>
      
      <el-descriptions :column="1" border>
        <el-descriptions-item label="LLM模型">ChatGLM3-6B</el-descriptions-item>
        <el-descriptions-item label="嵌入模型">BGE-small-zh-v1.5</el-descriptions-item>
        <el-descriptions-item label="向量数据库">FAISS</el-descriptions-item>
        <el-descriptions-item label="框架">LangChain</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>操作</span>
      </template>
      <div class="actions">
        <el-button type="warning" @click="clearCache">清除缓存</el-button>
        <el-button type="info" @click="exportConfig">导出配置</el-button>
        <el-button type="info" @click="importConfig">导入配置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck, Cpu, Database } from '@element-plus/icons-vue'

const status = ref({
  ready: true,
  device: 'CPU',
  vectorDb: true
})

const clearCache = () => {
  ElMessage.info('缓存已清除')
}

const exportConfig = () => {
  const config = {
    chunk_size: 500,
    chunk_overlap: 100,
    split_mode: 'zh',
    top_k: 5
  }
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'config.json'
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('配置已导出')
}

const importConfig = () => {
  ElMessage.info('功能开发中')
}

onMounted(() => {
  status.value.device = 'GPU'
})
</script>

<style scoped>
.system {
  padding: 20px;
}

.status-card {
  text-align: center;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-card.success {
  border-color: #67c23a;
}

.status-icon {
  color: #409eff;
  margin-right: 20px;
}

.status-card.success .status-icon {
  color: #67c23a;
}

.status-text {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 14px;
  color: #999;
}

.status-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>