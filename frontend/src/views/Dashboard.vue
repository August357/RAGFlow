<template>

<MainLayout>

<div class="dashboard">

<div class="pixel-card card">

<h3>知识库文件</h3>

<h1>{{data.files}}</h1>

</div>

<div class="pixel-card card">

<h3>Chunk数量</h3>

<h1>{{data.chunks}}</h1>

</div>

<div class="pixel-card card">

<h3>LLM模型</h3>

<h2>{{data.model}}</h2>

</div>

<div class="pixel-card card">

<h3>Embedding</h3>

<h2>{{data.embedding}}</h2>

</div>

<div class="pixel-card card">

<h3>向量库状态</h3>

<h2>

<span v-if="data.vector_db">✓ 已构建</span>

<span v-else>✗ 未构建</span>

</h2>

</div>

<div class="pixel-card card">

<h3>FAISS大小</h3>

<h2>{{detail.faiss_size}}</h2>

</div>

</div>

<div class="detail">

<div class="pixel-card">

<h3>最近上传文件</h3>

<ul>

<li v-for="file in detail.recent_files" :key="file">{{file}}</li>

<li v-if="detail.recent_files.length === 0">暂无文件</li>

</ul>

</div>

</div>

</MainLayout>

</template>

<script setup>

import { reactive,onMounted }
from "vue";

import MainLayout
from "../layouts/MainLayout.vue";

import {
getDashboard,
getDashboardDetail
}
from "../api/system";

const data = reactive({

files:0,

chunks:0,

model:"",

embedding:"",

vector_db:false

});

const detail = reactive({

recent_files:[],

faiss_size:"0MB",

questions:0

});

onMounted(async()=>{

const [res1, res2] = await Promise.all([
getDashboard(),
getDashboardDetail()
]);

Object.assign(data, res1.data);
Object.assign(detail, res2.data);

});

</script>

<style scoped>

.dashboard{

display:grid;

grid-template-columns:
repeat(3,1fr);

gap:20px;

}

.card{

height:180px;

text-align:center;

}

.card h1{

font-size:48px;

}

.detail{

margin-top:20px;

}

.detail ul{

list-style:none;

padding:0;

}

.detail li{

padding:8px 0;

border-bottom:2px dashed #4E342E;

}

</style>