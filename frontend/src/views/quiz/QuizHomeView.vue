<template>
  <div class="quiz-home">
    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number">{{ stats.total || 0 }}</div>
          <div class="stat-label">总题数</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number">{{ stats.single_count || 0 }}</div>
          <div class="stat-label">单选题</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number">{{ stats.multi_count || 0 }}</div>
          <div class="stat-label">多选题</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number">{{ stats.judge_count || 0 }}</div>
          <div class="stat-label">判断题</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quiz Mode Selection -->
    <el-row :gutter="20" class="mode-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('mixed')">
          <el-icon :size="40" color="#e94560"><Refresh /></el-icon>
          <h3>随机练习</h3>
          <p>从题库中随机抽取题目</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('knowledge')">
          <el-icon :size="40" color="#0f3460"><Reading /></el-icon>
          <h3>知识点练习</h3>
          <p>选择知识点后出题</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('difficulty')">
          <el-icon :size="40" color="#533483"><TrendCharts /></el-icon>
          <h3>难度练习</h3>
          <p>选择难度等级后出题</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('single')">
          <el-icon :size="40" color="#16213e"><EditPen /></el-icon>
          <h3>单题模式</h3>
          <p>逐题作答，即时反馈</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- Config Dialog -->
    <el-dialog v-model="showConfig" :title="modeTitle" width="500px">
      <el-form :model="config" label-width="80px">
        <el-form-item label="题目数量">
          <el-radio-group v-model="config.count">
            <el-radio :value="10">10题</el-radio>
            <el-radio :value="20">20题</el-radio>
            <el-radio :value="50">50题</el-radio>
            <el-radio :value="100">100题</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="selectedMode !== 'difficulty'" label="题型筛选">
          <el-checkbox-group v-model="config.questionTypes">
            <el-checkbox value="single">单选题</el-checkbox>
            <el-checkbox value="multi">多选题</el-checkbox>
            <el-checkbox value="judge">判断题</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item v-if="selectedMode === 'knowledge'" label="知识点">
          <el-select v-model="config.knowledgePoints" multiple placeholder="选择知识点" style="width:100%">
            <el-option v-for="kp in knowledgePoints" :key="kp" :label="kp" :value="kp" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="selectedMode === 'difficulty'" label="难度">
          <el-radio-group v-model="config.difficulty">
            <el-radio value="easy">简单</el-radio>
            <el-radio value="medium">中等</el-radio>
            <el-radio value="hard">困难</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConfig = false">取消</el-button>
        <el-button type="primary" :loading="starting" @click="startQuiz">开始答题</el-button>
      </template>
    </el-dialog>

    <!-- Incomplete Sessions -->
    <el-card v-if="incompleteSessions.length > 0" class="incomplete-card" shadow="never">
      <template #header><span>未完成的答题</span></template>
      <div v-for="s in incompleteSessions" :key="s.id" class="incomplete-item">
        <span>{{ s.mode }} 模式 - 进度 {{ s.current_index }}/{{ s.total_count }}</span>
        <div>
          <el-button type="primary" size="small" @click="$router.push(`/quiz/session/${s.id}`)">继续</el-button>
          <el-button size="small" @click="abandonSession(s.id)">放弃</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { questionApi, quizApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const router = useRouter()
const stats = ref({})
const knowledgePoints = ref([])
const incompleteSessions = ref([])
const showConfig = ref(false)
const selectedMode = ref('mixed')
const starting = ref(false)
const config = ref({ count: 10, questionTypes: ['single', 'multi', 'judge'], knowledgePoints: [], difficulty: 'medium' })

const modeTitle = computed(() => {
  const titles = { mixed: '随机练习', knowledge: '知识点练习', difficulty: '难度练习', single: '单题模式' }
  return titles[selectedMode.value] || '答题设置'
})

onMounted(async () => {
  try {
    const [statsRes, kpRes, incRes] = await Promise.all([
      questionApi.getStats(),
      questionApi.getKnowledgePoints(),
      quizApi.getIncompleteSessions(),
    ])
    stats.value = statsRes
    knowledgePoints.value = kpRes.knowledge_points || []
    incompleteSessions.value = incRes.sessions || []
  } catch (e) {
    console.error(e)
  }
})

function selectMode(mode) {
  selectedMode.value = mode
  config.value = { count: 10, questionTypes: ['single', 'multi', 'judge'], knowledgePoints: [], difficulty: 'medium' }
  showConfig.value = true
}

async function startQuiz() {
  starting.value = true
  try {
    const data = {
      mode: selectedMode.value,
      count: config.value.count,
      question_types: config.value.questionTypes.length > 0 && config.value.questionTypes.length < 3 ? config.value.questionTypes : undefined,
      knowledge_points: config.value.knowledgePoints.length > 0 ? config.value.knowledgePoints : undefined,
      difficulty: selectedMode.value === 'difficulty' ? config.value.difficulty : undefined,
    }
    const res = await quizApi.createSession(data)
    showConfig.value = false
    router.push(`/quiz/session/${res.session_id}`)
  } catch (e) {
    ElMessage.error(e.detail || '创建答题会话失败')
  } finally {
    starting.value = false
  }
}

async function abandonSession(id) {
  try {
    await quizApi.abandonSession(id)
    incompleteSessions.value = incompleteSessions.value.filter(s => s.id !== id)
    ElMessage.success('已放弃')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}
</script>

<style scoped>
.quiz-home { max-width: 1200px; margin: 0 auto; }
.stats-row { margin-bottom: 20px; }
.stat-card { text-align: center; padding: 10px; }
.stat-number { font-size: 32px; font-weight: bold; color: #e94560; }
.stat-label { font-size: 14px; color: #999; margin-top: 5px; }
.mode-row { margin-bottom: 20px; }
.mode-card { text-align: center; padding: 20px; cursor: pointer; transition: all 0.3s; }
.mode-card:hover { transform: translateY(-5px); border-color: #e94560; }
.mode-card h3 { margin: 10px 0 5px; color: #333; }
.mode-card p { color: #999; font-size: 13px; }
.incomplete-card { margin-top: 20px; }
.incomplete-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }
</style>
