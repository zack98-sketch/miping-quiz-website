<template>
  <div class="admin-dashboard">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><h3>系统概览</h3></template>
          <div class="stat-row"><span>总题数：</span><strong>{{ dashboard.total_questions || 0 }}</strong></div>
          <div class="stat-row"><span>总用户：</span><strong>{{ dashboard.total_users || 0 }}</strong></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><h3>题库导入</h3></template>
          <el-upload :auto-upload="false" :on-change="handleFileChange" accept=".xlsx" :show-file-list="false">
            <el-button type="primary">选择Excel文件</el-button>
          </el-upload>
          <div v-if="importResult" class="import-result">
            <p>总数：{{ importResult.total }}</p>
            <p style="color:#67c23a">成功：{{ importResult.success }}</p>
            <p style="color:#f56c6c">失败：{{ importResult.errors }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const dashboard = ref({})
const importResult = ref(null)

onMounted(async () => {
  try {
    dashboard.value = await adminApi.getDashboard()
  } catch {}
})

async function handleFileChange(file) {
  try {
    const res = await adminApi.importQuestions(file.raw)
    importResult.value = res
    ElMessage.success(`导入完成：成功${res.success}题`)
    dashboard.value = await adminApi.getDashboard()
  } catch (e) { ElMessage.error('导入失败') }
}
</script>

<style scoped>
.admin-dashboard { max-width: 1200px; margin: 0 auto; }
.stat-row { padding: 8px 0; font-size: 15px; }
.import-result { margin-top: 15px; }
</style>
