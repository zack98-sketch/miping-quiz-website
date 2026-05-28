<template>
  <div class="exam-list">
    <!-- Quick Mock Exam -->
    <el-card shadow="never" class="mock-card">
      <template #header>
        <div class="card-header">
          <h2>模拟考试</h2>
        </div>
      </template>
      <p class="mock-desc">随机抽取各题型组合成模拟试卷，支持自定义题型数量和时间</p>
      <el-form :model="mockConfig" label-width="100px" class="mock-form">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="单选题数">
              <el-input-number v-model="mockConfig.single_count" :min="0" :max="200" :step="10" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="多选题数">
              <el-input-number v-model="mockConfig.multi_count" :min="0" :max="200" :step="10" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="判断题数">
              <el-input-number v-model="mockConfig.judge_count" :min="0" :max="200" :step="5" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="考试时间">
              <el-input-number v-model="mockConfig.time_limit" :min="10" :max="300" :step="10" />
              <span class="unit">分钟</span>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="mock-summary">
          共 <strong>{{ mockConfig.single_count + mockConfig.multi_count + mockConfig.judge_count }}</strong> 题，
          考试时间 <strong>{{ mockConfig.time_limit }}</strong> 分钟
        </div>
        <el-button type="primary" size="large" :loading="creating" @click="createMockExam" class="start-btn">
          开始模拟考试
        </el-button>
      </el-form>
    </el-card>

    <!-- Exam List -->
    <el-card shadow="never" class="list-card">
      <template #header><h2>考试列表</h2></template>
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
import { examApi, quizApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const items = ref([])
const creating = ref(false)
const mockConfig = ref({
  single_count: 50,
  multi_count: 50,
  judge_count: 20,
  time_limit: 120
})

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
    sessionStorage.setItem(`exam_${id}`, JSON.stringify(res))
    router.push(`/exam/session/${id}`)
  } catch (e) { ElMessage.error(e.detail || '进入考试失败') }
}

async function createMockExam() {
  const total = mockConfig.value.single_count + mockConfig.value.multi_count + mockConfig.value.judge_count
  if (total === 0) {
    ElMessage.warning('请至少选择一种题型')
    return
  }
  creating.value = true
  try {
    // Create a quiz session with mixed mode and specific type counts
    const res = await quizApi.createSession({
      mode: 'mixed',
      count: total,
      question_types: ['single', 'multi', 'judge'],
      single_count: mockConfig.value.single_count,
      multi_count: mockConfig.value.multi_count,
      judge_count: mockConfig.value.judge_count,
      time_limit: mockConfig.value.time_limit,
      is_exam: true
    })
    // Store exam config for session view
    sessionStorage.setItem(`exam_session_${res.session_id}`, JSON.stringify({
      time_limit: mockConfig.value.time_limit,
      total: total,
      is_mock: true
    }))
    router.push(`/quiz/session/${res.session_id}`)
  } catch (e) {
    ElMessage.error(e.detail || '创建模拟考试失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.exam-list { max-width: 1200px; margin: 0 auto; }
.mock-card { margin-bottom: 16px; border-radius: 12px; }
.card-header h2 { margin: 0; }
.mock-desc { color: #999; margin-bottom: 16px; font-size: 14px; }
.mock-form { max-width: 600px; }
.unit { margin-left: 8px; color: #999; }
.mock-summary { margin: 12px 0; color: #666; font-size: 14px; }
.mock-summary strong { color: #e94560; }
.start-btn { margin-top: 8px; min-width: 200px; }
.list-card { border-radius: 12px; }

@media (max-width: 768px) {
  .mock-form { max-width: 100%; }
}
</style>
