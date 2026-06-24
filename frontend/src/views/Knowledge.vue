<template>

<MainLayout>

<div class="page">

<div class="top">

<el-upload

:auto-upload="false"

:show-file-list="false"

:on-change="handleUpload"

>

<el-button
class="pixel-btn"
>
上传文档
</el-button>

</el-upload>

</div>

<div class="file-list">

<div

v-for="file in files"

:key="file"

class="pixel-card item"

>

<h3>{{file}}</h3>

<div class="actions">

<el-button
size="small"
@click="preview(file)"
>
预览
</el-button>

<el-button
size="small"
type="danger"
@click="remove(file)"
>
删除
</el-button>

</div>

</div>

</div>

<el-dialog
v-model="dialogVisible"
width="70%"
>

<pre>
{{previewContent}}
</pre>

</el-dialog>

</div>

</MainLayout>

</template>

<script setup>

import { ref,onMounted } from "vue";

import { ElMessage }
from "element-plus";

import MainLayout
from "../layouts/MainLayout.vue";

import {

getFiles,
uploadFile,
deleteFile,
previewFile

}

from "../api/rag";

const files = ref([]);

const dialogVisible = ref(false);

const previewContent = ref("");

const loadFiles = async()=>{

const res =
await getFiles();

files.value =
res.data.files;

};

onMounted(()=>{

loadFiles();

});

const handleUpload =
async(file)=>{

const formData =
new FormData();

formData.append(
"file",
file.raw
);

await uploadFile(
formData
);

ElMessage.success(
"上传成功"
);

loadFiles();

};

const remove =
async(filename)=>{

await deleteFile(
filename
);

ElMessage.success(
"删除成功"
);

loadFiles();

};

const preview =
async(filename)=>{

const res =
await previewFile(
filename
);

previewContent.value =
res.data.content;

dialogVisible.value =
true;

};

</script>

<style scoped>

.page{

padding:20px;

}

.file-list{

display:grid;

grid-template-columns:
repeat(2,1fr);

gap:20px;

margin-top:20px;

}

.item{

min-height:120px;

}

.actions{

display:flex;

gap:10px;

}

</style>