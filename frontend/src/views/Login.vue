<template>

<div class="login-page">

  <div class="pixel-card login-card">

    <h1>RAG TERMINAL</h1>

    <p>
      Pixel Knowledge System
    </p>

    <el-input
      v-model="form.username"
      placeholder="用户名"
    />

    <el-input
      v-model="form.password"
      type="password"
      placeholder="密码"
      style="margin-top:15px"
    />

    <el-button
      class="pixel-btn"
      style="width:100%;margin-top:20px"
      @click="login"
    >
      LOGIN
    </el-button>

    <el-button
      style="width:100%;margin-top:10px"
      @click="goRegister"
    >
      REGISTER
    </el-button>

  </div>

</div>

</template>

<script setup>

import { reactive } from "vue";

import { useRouter } from "vue-router";

import { ElMessage } from "element-plus";

import { useUserStore }
from "../stores/user";

import { loginApi }
from "../api/user";

const router = useRouter();

const userStore = useUserStore();

const form = reactive({

  username:"",
  password:""

});

const login = async()=>{

  if(
    !form.username ||
    !form.password
  ){
    ElMessage.error("请输入账号密码");
    return;
  }

  try {
    const res = await loginApi(form);

    userStore.login(
      res.data.token,
      res.data.username
    );

    ElMessage.success(
      "登录成功"
    );

    router.push(
      "/dashboard"
    );
  } catch (error) {
    ElMessage.error(
      error.response?.data?.detail || "登录失败"
    );
  }
};

const goRegister=()=>{

  router.push(
    "/register"
  );
};

</script>

<style scoped>

.login-page{

  height:100vh;

  display:flex;

  justify-content:center;

  align-items:center;

  background:#F5E6C8;

}

.login-card{

  width:420px;

  text-align:center;

}

h1{

  color:#4E342E;

}

</style>