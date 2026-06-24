<template>

<div class="layout">

<div class="sidebar">

<h2>RAG SYSTEM</h2>

<div class="menu">

<router-link
active-class="active"
to="/dashboard"
>
首页
</router-link>

<router-link
active-class="active"
to="/chat"
>
智能问答
</router-link>

<router-link
active-class="active"
to="/knowledge"
>
知识库
</router-link>

<router-link
active-class="active"
to="/chunks"
>
Chunk管理
</router-link>

<router-link
active-class="active"
to="/config"
>
参数配置
</router-link>

<router-link
active-class="active"
to="/system"
>
系统监控
</router-link>

</div>

<div class="user">

{{ username }}

<el-button
size="small"
@click="toggleDark"
>

{{ dark ? '🌙' : '☀' }}

</el-button>

<el-button
size="small"
@click="logout"
>

退出

</el-button>

</div>

</div>

<div class="content">

<slot />

</div>

</div>

</template>

<script setup>

import { computed,ref,onMounted,watch } from "vue";

import { useRouter } from "vue-router";

import { useUserStore } from "../stores/user";

const router =
useRouter();

const userStore =
useUserStore();

const username =
computed(
()=>userStore.username
);

const dark = ref(false);

const toggleDark = () => {
  dark.value = !dark.value;
  if (dark.value) {
    document.body.classList.add('dark');
  } else {
    document.body.classList.remove('dark');
  }
};

const logout=()=>{

userStore.logout();

router.push(
"/login"
);

};

onMounted(() => {
  // 从localStorage加载夜间模式设置
  const savedDark = localStorage.getItem('darkMode');
  if (savedDark === 'true') {
    dark.value = true;
    document.body.classList.add('dark');
  }
});

// 监听dark变化并保存到localStorage
watch(dark, (newVal) => {
  localStorage.setItem('darkMode', newVal);
});

</script>

<style scoped>

.layout{

display:flex;

height:100vh;

}

.sidebar{

width:240px;

background:var(--sidebar-bg);

padding:20px;

display:flex;

flex-direction:column;

transition:background 0.3s;

}

.sidebar h2{

color:var(--sidebar-text);

margin-bottom:30px;

}

.menu{

flex:1;

}

.menu a{

display:block;

color:var(--sidebar-text);

text-decoration:none;

padding:12px 15px;

margin:8px 0;

border-radius:8px;

}

.menu a:hover{

background:var(--primary);

color:var(--text);

}

.menu a.active{

background:var(--primary);

padding:8px;

border-radius:6px;

color:var(--text);

font-weight:bold;

}

.user{

padding:15px;

background:var(--card-color);

border-radius:8px;

display:flex;

justify-content:space-between;

align-items:center;

color:var(--text);

transition:background 0.3s;

}

.content{

flex:1;

padding:30px;

overflow:auto;

}

</style>