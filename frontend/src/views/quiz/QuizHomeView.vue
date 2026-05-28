<template>
  <div class="quiz-home">
    <!-- Search Bar -->
    <el-card class="search-card" shadow="never">
      <el-input v-model="searchKeyword" placeholder="搜索题目、答案、解析..." size="large" clearable @keyup.enter="doSearch" class="search-input">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button type="primary" @click="doSearch" :loading="searching">搜索</el-button>
        </template>
      </el-input>
    </el-card>

    <!-- Search Results -->
    <el-card v-if="searchResults.length > 0" class="search-results" shadow="never">
      <template #header>
        <span>搜索结果 ({{ searchResults.length }}题)</span>
        <el-button type="text" @click="searchResults = []" style="float:right">关闭</el-button>
      </template>
      <div v-for="q in searchResults" :key="q.id" class="search-result-item" @click="goToQuestion(q)">
        <div class="result-type">
          <el-tag :type="q.question_type === 'single' ? '' : q.question_type === 'multi' ? 'warning' : 'success'" size="small" effect="dark">
            {{ {single:'单选',multi:'多选',judge:'判断'}[q.question_type] }}
          </el-tag>
        </div>
        <div class="result-content">{{ q.content }}</div>
      </div>
    </el-card>

    <!-- Stats Cards -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="6" :sm="6">
        <el-card class="stat-card" shadow="hover" @click="quickStart('mixed')">
          <div class="stat-number">{{ stats.total || 0 }}</div>
          <div class="stat-label">总题数</div>
          <div class="stat-hint">点击练习</div>
        </el-card>
      </el-col>
      <el-col :xs="6" :sm="6">
        <el-card class="stat-card single-card" shadow="hover" @click="quickStartByType('single')">
          <div class="stat-number">{{ stats.single_count || 0 }}</div>
          <div class="stat-label">单选题</div>
          <div class="stat-hint">点击练习</div>
        </el-card>
      </el-col>
      <el-col :xs="6" :sm="6">
        <el-card class="stat-card multi-card" shadow="hover" @click="quickStartByType('multi')">
          <div class="stat-number">{{ stats.multi_count || 0 }}</div>
          <div class="stat-label">多选题</div>
          <div class="stat-hint">点击练习</div>
        </el-card>
      </el-col>
      <el-col :xs="6" :sm="6">
        <el-card class="stat-card judge-card" shadow="hover" @click="quickStartByType('judge')">
          <div class="stat-number">{{ stats.judge_count || 0 }}</div>
          <div class="stat-label">判断题</div>
          <div class="stat-hint">点击练习</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quiz Mode Selection -->
    <el-row :gutter="16" class="mode-row">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('mixed')">
          <el-icon :size="36" color="#e94560"><Refresh /></el-icon>
          <h3>随机练习</h3>
          <p>从题库中随机抽取题目</p>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('knowledge')">
          <el-icon :size="36" color="#0f3460"><Reading /></el-icon>
          <h3>知识点练习</h3>
          <p>选择知识点后出题</p>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('difficulty')">
          <el-icon :size="36" color="#533483"><TrendCharts /></el-icon>
          <h3>难度练习</h3>
          <p>选择难度等级后出题</p>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="mode-card" shadow="hover" @click="selectMode('single')">
          <el-icon :size="36" color="#16213e"><EditPen /></el-icon>
          <h3>单题模式</h3>
          <p>逐题作答，即时反馈</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- Config Dialog -->
    <el-dialog v-model="showConfig" :title="modeTitle" width="500px" :append-to-body="true">
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
        <span>{{ modeNameMap[s.mode] || s.mode }} - 进度 {{ s.current_index }}/{{ s.total_count }}</span>
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

// Search
const searchKeyword = ref('')
const searching = ref(false)
const searchResults = ref([])

const modeNameMap = {
  single: '单题模式', mixed: '随机练习', knowledge: '知识点练习',
  difficulty: '难度练习', error_book: '错题练习', favorite: '收藏练习'
}

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

// Quick start by clicking stat card
function quickStart(mode) {
  selectedMode.value = mode
  config.value = { count: 10, questionTypes: ['single', 'multi', 'judge'], knowledgePoints: [], difficulty: 'medium' }
  startQuiz()
}

function quickStartByType(type) {
  selectedMode.value = 'single'
  config.value = { count: 20, questionTypes: [type], knowledgePoints: [], difficulty: 'medium' }
  startQuiz()
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

// Search
async function doSearch() {
  if (!searchKeyword.value.trim()) return
  searching.value = true
  try {
    const res = await questionApi.search(searchKeyword.value.trim())
    searchResults.value = res.items || res || []
    if (searchResults.value.length === 0) {
      ElMessage.info('未找到匹配的题目')
    }
  } catch (e) {
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
}

function goToQuestion(q) {
  // Start a single-question session for this specific question
  selectedMode.value = 'single'
  config.value = { count: 1, questionTypes: [q.question_type], knowledgePoints: [], difficulty: 'medium' }
  startQuiz()
}
</script>

<style scoped>
.quiz-home { max-width: 1200px; margin: 0 auto; }
.search-card { margin-bottom: 16px; border-radius: 12px; }
.search-input { font-size: 16px; }
.search-results { margin-bottom: 16px; border-radius: 12px; }
.search-result-item {
  display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: background 0.2s;
}
.search-result-item:hover { background: #f5f7fa; }
.search-result-item:last-child { border-bottom: none; }
.result-type { flex-shrink: 0; }
.result-content { flex: 1; line-height: 1.6; color: #333; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.stats-row { margin-bottom: 16px; }
.stat-card {
  text-align: center; padding: 12px 8px; cursor: pointer; transition: all 0.3s; border-radius: 12px;
  position: relative; overflow: hidden;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(233,69,96,0.15); }
.stat-number { font-size: 28px; font-weight: bold; color: #e94560; }
.stat-label { font-size: 13px; color: #666; margin-top: 4px; }
.stat-hint { font-size: 11px; color: #bbb; margin-top: 2px; }
.single-card .stat-number { color: #409eff; }
.multi-card .stat-number { color: #e6a23c; }
.judge-card .stat-number { color: #67c23a; }
.mode-row { margin-bottom: 16px; }
.mode-card { text-align: center; padding: 20px 12px; cursor: pointer; transition: all 0.3s; border-radius: 12px; }
.mode-card:hover { transform: translateY(-5px); border-color: #e94560; box-shadow: 0 6px 16px rgba(233,69,96,0.12); }
.mode-card h3 { margin: 10px 0 5px; color: #333; font-size: 16px; }
.mode-card p { color: #999; font-size: 13px; }
.incomplete-card { margin-top: 16px; border-radius: 12px; }
.incomplete-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.incomplete-item:last-child { border-bottom: none; }

@media (max-width: 768px) {
  .stat-number { font-size: 22px; }
  .stat-label { font-size: 12px; }
  .stat-hint { display: none; }
  .mode-card { padding: 14px 8px; }
  .mode-card h3 { font-size: 14px; }
  .mode-card p { font-size: 12px; }
}
</style>
