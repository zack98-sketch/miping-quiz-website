<template>
  <div id="app">
    <el-container v-if="auth.isLoggedIn" class="app-container">
      <!-- Desktop Header -->
      <el-header class="app-header desktop-header">
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
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Mobile Header -->
      <el-header class="app-header mobile-header">
        <div class="mobile-header-top">
          <h1 class="app-title" @click="$router.push('/')">密评题库</h1>
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ auth.user?.username }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="mobile-nav">
          <div v-for="item in mobileNavItems" :key="item.path" class="mobile-nav-item" :class="{ active: currentRoute === item.path }" @click="handleMenuSelect(item.path)">
            <el-icon :size="18"><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
    <router-view v-else />
  </div>

  <!-- Password Change Dialog -->
  <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px" :append-to-body="true">
    <el-form :model="passwordForm" label-width="80px">
      <el-form-item label="旧密码">
        <el-input v-model="passwordForm.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="passwordForm.new_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="passwordDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="passwordLoading" @click="changePassword">确认修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { authApi } from './api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const currentRoute = computed(() => route.path)

const mobileNavItems = [
  { path: '/', label: '答题', icon: 'EditPen' },
  { path: '/error-book', label: '错题', icon: 'DocumentDelete' },
  { path: '/favorites', label: '收藏', icon: 'Star' },
  { path: '/analysis', label: '分析', icon: 'DataAnalysis' },
  { path: '/exams', label: '考试', icon: 'Finished' },
  { path: '/notes', label: '备注', icon: 'Notebook' },
]

// Password
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordForm = ref({ old_password: '', new_password: '' })

function handleMenuSelect(index) {
  router.push(index)
}

function handleUserCommand(command) {
  if (command === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (command === 'password') {
    passwordForm.value = { old_password: '', new_password: '' }
    passwordDialogVisible.value = true
  }
}

async function changePassword() {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    ElMessage.warning('请输入旧密码和新密码')
    return
  }
  passwordLoading.value = true
  try {
    await authApi.changePassword(passwordForm.value)
    ElMessage.success('密码修改成功，请重新登录')
    passwordDialogVisible.value = false
    auth.logout()
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.detail || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif; }

.app-container { height: 100vh; display: flex; flex-direction: column; }
.app-header {
  display: flex; align-items: center; background: #1a1a2e; color: #fff; padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15); flex-shrink: 0;
}
.app-title { font-size: 18px; cursor: pointer; color: #e94560; margin-right: 30px; white-space: nowrap; font-weight: bold; }
.header-menu { flex: 1; background: transparent; border: none; }
.header-menu .el-menu-item { color: #ccc; border-bottom: none !important; }
.header-menu .el-menu-item:hover, .header-menu .el-menu-item.is-active { color: #e94560; background: rgba(233,69,96,0.1); }
.header-right { margin-left: 20px; }
.user-info { color: #ccc; cursor: pointer; display: flex; align-items: center; gap: 6px; }
.user-info:hover { color: #e94560; }
.app-main { background: #f5f5f5; padding: 20px; overflow-y: auto; flex: 1; }

/* Mobile header - hidden by default */
.mobile-header { display: none !important; }
.desktop-header { display: flex !important; }

/* Mobile nav */
.mobile-nav {
  display: flex; width: 100%; overflow-x: auto; gap: 0;
  -webkit-overflow-scrolling: touch; scrollbar-width: none;
}
.mobile-nav::-webkit-scrollbar { display: none; }
.mobile-nav-item {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 6px 4px; color: #aaa; cursor: pointer; transition: all 0.2s; min-width: 56px;
  font-size: 11px; gap: 2px;
}
.mobile-nav-item.active { color: #e94560; }
.mobile-nav-item:hover { color: #e94560; }
.mobile-header-top { display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 4px; }

/* Responsive */
@media (max-width: 768px) {
  .desktop-header { display: none !important; }
  .mobile-header { display: flex !important; flex-direction: column; height: auto !important; padding: 8px 12px 0; }
  .app-title { font-size: 16px; margin-right: 0; }
  .app-main { padding: 12px; }
}
</style>
