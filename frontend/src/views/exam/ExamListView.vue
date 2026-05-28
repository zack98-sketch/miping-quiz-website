<template>
  <div class="exam-list">
    <el-card shadow="never">
      <template #header><h2>在线考试</h2></template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column label="考试名称" prop="title" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="{upcoming:'info',ongoing:'success',ended:'danger'}[row.status]">{{ {upcoming:'未开始',ongoing:'进行中',ended:'已结束'}[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间限制" width="100">
          <template #default="{ row }">{{ row.time_limit }}分钟</template>
        </el-table-column>
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">{{ row.start_time?.slice(0, 16).replace('T', ' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button v-if="row.status === 'ongoing' && !row.has_participated" type="primary" size="small" @click="enterExam(row.id)">参加</el-button>
            <el-tag v-else-if="row.has_participated" type="info" size="small">已参加</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { examApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const items = ref([])

onMounted(() => loadExams())

async function loadExams() {
  loading.value = true
  try {
    const res = await examApi.getList()
    items.value = res.items || []
  } finally { loading.value = false }
}

async function enterExam(id) {
  try {
    const res = await examApi.enter(id)
    // Store exam data for session view
    sessionStorage.setItem(`exam_${id}`, JSON.stringify(res))
    router.push(`/exam/session/${id}`)
  } catch (e) { ElMessage.error(e.detail || '进入考试失败') }
}
</script>

<style scoped>
.exam-list { max-width: 1200px; margin: 0 auto; }
</style>
