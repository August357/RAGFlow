<template>

<div class="register-page">

<div class="pixel-card register-card">

<h1>CREATE USER</h1>

<el-input
v-model="form.username"
placeholder="用户名"
/>

<el-input
v-model="form.email"
placeholder="邮箱"
style="margin-top:15px"
/>

<el-input
v-model="form.password"
type="password"
placeholder="密码"
style="margin-top:15px"
/>

<el-input
v-model="form.confirm"
type="password"
placeholder="确认密码"
style="margin-top:15px"
/>

<el-button

class="pixel-btn"

style="
width:100%;
margin-top:20px
"

@click="register"

>

REGISTER

</el-button>

<el-button

style="
width:100%;
margin-top:10px
"

@click="back"

>

BACK

</el-button>

</div>

</div>

</template>

<script setup>

import { reactive } from "vue";

import { useRouter } from "vue-router";

import { ElMessage } from "element-plus";

import { registerApi }
from "../api/user";

const router = useRouter();

const form = reactive({

username:"",
email:"",
password:"",
confirm:""

});

const register=async()=>{

if(
form.password
!== form.confirm
){

ElMessage.error(
"两次密码不一致"
)

return

}

try {
  await registerApi(form);

  ElMessage.success(
    "注册成功"
  );

  router.push(
    "/login"
  );
} catch (error) {
  ElMessage.error(
    error.response?.data?.detail || "注册失败"
  );
}
};

const back=()=>{

router.push(
"/login"
)

}

</script>

<style scoped>

.register-page{

height:100vh;

display:flex;

justify-content:center;

align-items:center;

background:#F5E6C8;

}

.register-card{

width:450px;

}

</style>