<template>

<MainLayout>

<div class="grid">

<div class="pixel-card item">

<h3>CPU</h3>

<h1>{{info.cpu}}%</h1>

</div>

<div class="pixel-card item">

<h3>内存</h3>

<h1>{{info.memory}}%</h1>

</div>

<div class="pixel-card item">

<h3>GPU利用率</h3>

<h1>{{info.gpu_usage}}%</h1>

</div>

<div class="pixel-card item">

<h3>显存</h3>

<h1>

{{info.gpu_memory}}

/

{{info.gpu_total}}

GB

</h1>

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
getSystemInfo
}
from "../api/system";

const info = reactive({

cpu:0,

memory:0,

gpu_usage:0,

gpu_memory:0,

gpu_total:0

});

const load = async()=>{

const res =
await getSystemInfo();

Object.assign(
info,
res.data
);

};

onMounted(()=>{

load();

setInterval(
load,
3000
);

});

</script>

<style scoped>

.grid{

display:grid;

grid-template-columns:
repeat(2,1fr);

gap:20px;

}

.item{

height:200px;

text-align:center;

}

.item h1{

font-size:42px;

}

</style>