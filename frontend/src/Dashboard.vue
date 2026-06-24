<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="知识库文件" :value="fileCount">
            <template #suffix>个</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="Chunk数量" :value="chunkCount">
            <template #suffix>个</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="系统状态" :value="statusText">
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="设备类型" :value="device">
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/chat')">
              <el-icon><ChatDotRound /></el-icon>
              开始问答
            </el-button>
            <el-button type="success" size="large" @click="$router.push('/knowledge')">
              <el-icon><Upload /></el-icon>
              上传文档
            </el-button>
            <el-button type="info" size="large" @click="$router.push('/chunk')">
              <el-icon><Document /></el-icon>
              查看切片
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近文件</span>
          </template>
          <el-list v-if="recentFiles.length > 0" :data="recentFiles">
            <el-list-item v-for="file in recentFiles" :key="file">
              <el-icon><Document /></el-icon>
              <span>{{ file }}</span>
            </el-list-item>
          </template>
          <p v-else class="empty-text">暂无文件</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFiles, getChunks } from '@/api'

const fileCount = ref(0)
const chunkCount = ref(0)
const statusText = ref('就绪')
const device = ref('CPU')
const recentFiles = ref([])

const fetchData = async () => {
  try {
    const filesRes = await getFiles()
    recentFiles.value = filesRes.data.files.slice(0, 5)
    fileCount.value = filesRes.data.files.length
    
    const chunksRes = await getChunks()
    if (chunksRes.data.content) {
      chunkCount.value = chunksRes.data.content.split('Chunk ').length - 1
    }
    
    device.value = 'GPU'
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  text-align: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quick-actions .el-button {
  width: 100%;
  height: 60px;
  font-size: 18px;
}

.empty-text {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style>