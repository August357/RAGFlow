<template>
  <div class="knowledge">
    <el-card>
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        @click="showUploadDialog"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 TXT/PDF/DOCX 格式
          </div>
        </template>
      </el-upload>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>知识库文件</span>
          <el-button @click="fetchFiles" :icon="Refresh">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="files" style="width: 100%">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handlePreview(row)">预览</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="previewDialogVisible" title="文件预览" width="70%">
      <el-input
        v-model="previewContent"
        type="textarea"
        :rows="20"
        readonly
      />
    </el-dialog>

    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="50%">
      <input type="file" ref="fileInput" multiple @change="handleUpload" />
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpload" :loading="uploading">确认上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getFiles, previewFile, deleteFile, uploadFile } from '@/api'

const files = ref([])
const previewDialogVisible = ref(false)
const previewContent = ref('')
const uploadDialogVisible = ref(false)
const fileInput = ref(null)
const selectedFiles = ref([])
const uploading = ref(false)

const fetchFiles = async () => {
  try {
    const response = await getFiles()
    files.value = response.data.files.map(f => ({ filename: f }))
  } catch (error) {
    ElMessage.error('获取文件列表失败')
  }
}

const showUploadDialog = () => {
  uploadDialogVisible.value = true
}

const handleFileChange = () => {}

const handleUpload = (event) => {
  selectedFiles.value = Array.from(event.target.files)
}

const confirmUpload = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    for (const file of selectedFiles.value) {
      await uploadFile(file)
    }
    ElMessage.success('上传成功')
    fetchFiles()
    uploadDialogVisible.value = false
    selectedFiles.value = []
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handlePreview = async (row) => {
  try {
    const response = await previewFile(row.filename)
    previewContent.value = response.data.content
    previewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('预览失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文件吗？', '确认删除', {
      type: 'warning'
    })
    
    await deleteFile(row.filename)
    ElMessage.success('删除成功')
    fetchFiles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchFiles()
})
</script>

<style scoped>
.knowledge {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>