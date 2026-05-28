<template>
  <div id="app">
    <el-container v-if="auth.isLoggedIn" class="app-container">
      <el-header class="app-header">
        <div class="header-left">
          <h1 class="app-title" @click="$router.push('/')">密评题库答题系统</h1>
        </div>
        <el-menu :default-active="currentRoute" mode="horizontal" :ellipsis="false" class="header-menu" @select="handleMenuSelect">
          <el-menu-item index="/">开始答题</el-menu-item>
          <el-menu-item index="/error-book">错题本</el-menu-item>
          <el-menu-item index="/favorites">收藏夹</el-menu-item>
          <el-menu-item index="/analysis">学习分析</el-menu-item>
          <el-menu-item index="/exams">在线考试</el-menu-item>
          <el-menu-item index="/notes">我的备注</el-menu-item>
          <el-menu-item v-if="auth.isAdmin" index="/admin">管理</el-menu-item>
        </el-menu>
        <div class="header-right">
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ auth.user?.username }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const currentRoute = computed(() => route.path)

function handleMenuSelect(index) {
  router.push(index)
}

function handleUserCommand(command) {
  if (command === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif; }

.app-container { height: 100vh; }
.app-header {
  display: flex; align-items: center; background: #1a1a2e; color: #fff; padding: 0 20px; height: 60px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.app-title { font-size: 18px; cursor: pointer; color: #e94560; margin-right: 30px; white-space: nowrap; }
.header-menu { flex: 1; background: transparent; border: none; }
.header-menu .el-menu-item { color: #ccc; border-bottom: none !important; }
.header-menu .el-menu-item:hover, .header-menu .el-menu-item.is-active { color: #e94560; background: rgba(233,69,96,0.1); }
.header-right { margin-left: 20px; }
.user-info { color: #ccc; cursor: pointer; display: flex; align-items: center; gap: 6px; }
.user-info:hover { color: #e94560; }
.app-main { background: #f5f5f5; padding: 20px; overflow-y: auto; }

/* Responsive */
@media (max-width: 768px) {
  .app-header { padding: 0 10px; }
  .app-title { font-size: 14px; margin-right: 10px; }
  .header-menu .el-menu-item { padding: 0 8px; font-size: 13px; }
  .app-main { padding: 10px; }
}
</style>
