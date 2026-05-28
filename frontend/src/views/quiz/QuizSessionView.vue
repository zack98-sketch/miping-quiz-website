<template>
  <div class="quiz-session" v-loading="loading">
    <div v-if="currentQuestion" class="question-container">
      <!-- Progress Bar -->
      <div class="progress-bar">
        <el-progress :percentage="progressPercent" :stroke-width="20" :text-inside="true" :format="() => `${currentIndex + 1} / ${totalCount}`" />
        <div class="timer">
          <el-icon><Timer /></el-icon> {{ formattedTime }}
        </div>
      </div>

      <!-- Question Card -->
      <el-card class="question-card" shadow="hover">
        <div class="question-header">
          <el-tag :type="questionTypeTag" effect="dark" round>{{ questionTypeLabel }}</el-tag>
          <el-tag type="info" size="small" effect="plain">{{ currentQuestion.knowledge_point }}</el-tag>
          <el-tag :type="difficultyTag" size="small" effect="plain">{{ difficultyLabel }}</el-tag>
          <div class="question-actions">
            <el-tooltip content="AI提示" placement="top">
              <el-button type="primary" size="small" :icon="'ChatDotRound'" circle @click="showAiHint" />
            </el-tooltip>
            <el-tooltip content="添加备注" placement="top">
              <el-button type="success" size="small" :icon="'EditPen'" circle @click="showNoteDialog" />
            </el-tooltip>
            <el-tooltip :content="isFavorited ? '取消收藏' : '收藏'" placement="top">
              <el-button :type="isFavorited ? 'warning' : 'default'" size="small" :icon="isFavorited ? 'StarFilled' : 'Star'" circle @click="toggleFavorite" />
            </el-tooltip>
          </div>
        </div>
        
        <div class="question-content">
          <span class="question-number">{{ currentIndex + 1 }}.</span>
          {{ currentQuestion.content }}
        </div>

        <!-- Options -->
        <div class="options-area">
          <!-- Single Choice -->
          <el-radio-group v-if="currentQuestion.question_type === 'single' && !isAnswered" v-model="selectedAnswer" class="option-group">
            <el-radio v-for="opt in currentQuestion.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              <span class="option-label">{{ opt.label }}.</span>
              <span class="option-text">{{ opt.content }}</span>
            </el-radio>
          </el-radio-group>

          <!-- Multi Choice -->
          <el-checkbox-group v-if="currentQuestion.question_type === 'multi' && !isAnswered" v-model="selectedMultiAnswer" class="option-group">
            <el-checkbox v-for="opt in currentQuestion.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              <span class="option-label">{{ opt.label }}.</span>
              <span class="option-text">{{ opt.content }}</span>
            </el-checkbox>
          </el-checkbox-group>

          <!-- Judge -->
          <el-radio-group v-if="currentQuestion.question_type === 'judge' && !isAnswered" v-model="selectedAnswer" class="option-group">
            <el-radio v-for="opt in currentQuestion.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              <span class="option-text">{{ opt.content }}</span>
            </el-radio>
          </el-radio-group>

          <!-- Answered State -->
          <div v-if="isAnswered" class="answered-options">
            <div v-for="opt in currentQuestion.options" :key="opt.label" class="answered-option" :class="getOptionClass(opt)">
              <span class="option-label">{{ opt.label }}.</span>
              <span class="option-text">{{ opt.content }}</span>
              <el-icon v-if="isCorrectOption(opt)" class="option-icon" color="#67c23a"><CircleCheck /></el-icon>
              <el-icon v-if="isWrongOption(opt)" class="option-icon" color="#f56c6c"><CircleClose /></el-icon>
            </div>
          </div>
        </div>

        <!-- Answer Feedback -->
        <div v-if="isAnswered" class="answer-feedback" :class="{ correct: lastResult?.is_correct, wrong: !lastResult?.is_correct }">
          <div class="feedback-header">
            <el-icon :size="22"><component :is="lastResult?.is_correct ? 'CircleCheck' : 'CircleClose'" /></el-icon>
            <span class="feedback-text">{{ lastResult?.is_correct ? '回答正确！' : '回答错误' }}</span>
          </div>
          <div v-if="!lastResult?.is_correct" class="correct-answer">
            正确答案：<strong>{{ lastResult?.correct_answer }}</strong>
          </div>
          <div v-if="lastResult?.explanation" class="explanation">
            <strong>解析：</strong>{{ lastResult?.explanation }}
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="action-area">
          <el-button v-if="currentIndex > 0" size="large" @click="prevQuestion">
            <el-icon><ArrowLeft /></el-icon> 上一题
          </el-button>
          <el-button v-if="!isAnswered" type="primary" size="large" :disabled="!hasAnswer" @click="submitAnswer">
            提交答案
          </el-button>
          <el-button v-if="isAnswered && !isLastQuestion" type="primary" size="large" @click="nextQuestion">
            下一题 <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button v-if="isAnswered && isLastQuestion" type="success" size="large" @click="nextQuestion">
            查看结果
          </el-button>
        </div>
      </el-card>

      <!-- AI Hint Dialog -->
      <el-dialog v-model="aiDialogVisible" title="AI 智能提示" width="500px" :append-to-body="true">
        <div v-if="aiLoading" style="text-align:center;padding:20px">
          <el-icon class="is-loading" :size="24"><Loading /></el-icon> 正在生成提示...
        </div>
        <div v-else-if="aiHintContent" class="ai-hint-content">{{ aiHintContent }}</div>
        <div v-else style="text-align:center;color:#999;padding:20px">选择提示级别获取帮助</div>
        <template #footer>
          <div style="display:flex;gap:10px;justify-content:center">
            <el-button @click="requestAiHint('light')">轻度提示</el-button>
            <el-button type="warning" @click="requestAiHint('medium')">中度提示</el-button>
            <el-button type="danger" @click="requestAiHint('deep')">深度提示</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- Note Dialog -->
      <el-dialog v-model="noteDialogVisible" title="添加备注" width="500px" :append-to-body="true">
        <el-input v-model="noteContent" type="textarea" :rows="5" placeholder="输入你的备注、解析或心得..." maxlength="2000" show-word-limit />
        <template #footer>
          <el-button @click="noteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveNote">保存</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { quizApi, favoriteApi, aiHintApi, noteApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const sessionId = computed(() => route.params.id)

const loading = ref(true)
const currentQuestion = ref(null)
const currentIndex = ref(0)
const totalCount = ref(0)
const isAnswered = ref(false)
const isFavorited = ref(false)
const lastResult = ref(null)
const selectedAnswer = ref('')
const selectedMultiAnswer = ref([])
const elapsedTime = ref(0)
const questionStartTime = ref(Date.now())
// AI hint
const aiDialogVisible = ref(false)
const aiLoading = ref(false)
const aiHintContent = ref('')
// Note
const noteDialogVisible = ref(false)
const noteContent = ref('')

let timer = null

const hasAnswer = computed(() => {
  if (!currentQuestion.value) return false
  if (currentQuestion.value.question_type === 'multi') return selectedMultiAnswer.value.length > 0
  return !!selectedAnswer.value
})

const isLastQuestion = computed(() => currentIndex.value >= totalCount.value - 1)
const progressPercent = computed(() => totalCount.value > 0 ? ((currentIndex.value + (isAnswered.value ? 1 : 0)) / totalCount.value * 100) : 0)
const formattedTime = computed(() => {
  const m = Math.floor(elapsedTime.value / 60)
  const s = elapsedTime.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const questionTypeLabel = computed(() => {
  const map = { single: '单选题', multi: '多选题', judge: '判断题' }
  return map[currentQuestion.value?.question_type] || ''
})
const questionTypeTag = computed(() => {
  const map = { single: '', multi: 'warning', judge: 'success' }
  return map[currentQuestion.value?.question_type] || ''
})
const difficultyLabel = computed(() => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[currentQuestion.value?.difficulty] || ''
})
const difficultyTag = computed(() => {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[currentQuestion.value?.difficulty] || ''
})

onMounted(async () => {
  timer = setInterval(() => elapsedTime.value++, 1000)
  await loadCurrentQuestion()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

async function loadCurrentQuestion() {
  loading.value = true
  try {
    const res = await quizApi.getCurrentQuestion(sessionId.value)
    currentIndex.value = res.question_index
    totalCount.value = res.total_count
    currentQuestion.value = res.question
    isAnswered.value = res.is_answered
    isFavorited.value = res.is_favorited || false
    if (res.is_answered) {
      selectedAnswer.value = res.user_answer || ''
    } else {
      selectedAnswer.value = ''
      selectedMultiAnswer.value = []
    }
    questionStartTime.value = Date.now()
    // Load existing note
    try {
      const noteRes = await noteApi.getByQuestion(currentQuestion.value.id)
      noteContent.value = noteRes.note?.content || ''
    } catch {}
  } catch (e) {
    ElMessage.error(e.detail || '加载题目失败')
  } finally {
    loading.value = false
  }
}

async function submitAnswer() {
  let answer = selectedAnswer.value
  if (currentQuestion.value.question_type === 'multi') {
    answer = selectedMultiAnswer.value.sort().join(',')
  }
  const timeSpent = Math.floor((Date.now() - questionStartTime.value) / 1000)
  
  try {
    const res = await quizApi.submitAnswer(sessionId.value, {
      question_id: currentQuestion.value.id,
      answer,
      time_spent: timeSpent,
    })
    lastResult.value = res
    isAnswered.value = true
  } catch (e) {
    ElMessage.error(e.detail || '提交答案失败')
  }
}

function nextQuestion() {
  if (lastResult.value?.is_completed) {
    router.push(`/quiz/result/${sessionId.value}`)
  } else {
    lastResult.value = null
    isAnswered.value = false
    loadCurrentQuestion()
  }
}

function prevQuestion() {
  // Navigate to previous question by adjusting the session's current_index
  // We need a backend endpoint or workaround - for now we reload and skip
  if (currentIndex.value > 0) {
    // Simple approach: just reload current (backend tracks index)
    // We'll add a proper prev endpoint later
    ElMessage.info('已提交的答案无法返回修改')
  }
}

async function toggleFavorite() {
  try {
    if (isFavorited.value) {
      await favoriteApi.remove(currentQuestion.value.id)
      isFavorited.value = false
      ElMessage.success('取消收藏')
    } else {
      await favoriteApi.add(currentQuestion.value.id)
      isFavorited.value = true
      ElMessage.success('已收藏')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// AI Hint
function showAiHint() {
  aiHintContent.value = ''
  aiDialogVisible.value = true
}

async function requestAiHint(level) {
  if (!currentQuestion.value) return
  aiLoading.value = true
  try {
    const res = await aiHintApi.request({ question_id: currentQuestion.value.id, level })
    aiHintContent.value = res.hint_content
  } catch (e) {
    aiHintContent.value = e.detail || '提示服务暂不可用'
  } finally {
    aiLoading.value = false
  }
}

// Note
function showNoteDialog() {
  noteDialogVisible.value = true
}

async function saveNote() {
  if (!noteContent.value.trim()) {
    ElMessage.warning('请输入备注内容')
    return
  }
  try {
    await noteApi.upsert(currentQuestion.value.id, noteContent.value)
    ElMessage.success('备注保存成功')
    noteDialogVisible.value = false
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

function getOptionClass(opt) {
  if (!lastResult.value) return ''
  const correct = lastResult.value.correct_answer
  const userAnswer = selectedAnswer.value || (selectedMultiAnswer.value.sort().join(','))
  if (correct.includes(opt.label)) return 'correct-option'
  if (userAnswer.includes(opt.label) && !correct.includes(opt.label)) return 'wrong-option'
  return ''
}

function isCorrectOption(opt) {
  return lastResult.value?.correct_answer?.includes(opt.label)
}

function isWrongOption(opt) {
  const userAnswer = selectedAnswer.value || (selectedMultiAnswer.value.sort().join(','))
  return userAnswer?.includes(opt.label) && !lastResult.value?.correct_answer?.includes(opt.label)
}
</script>

<style scoped>
.quiz-session { max-width: 800px; margin: 0 auto; }
.progress-bar { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.progress-bar .el-progress { flex: 1; }
.timer { font-size: 18px; font-weight: bold; color: #e94560; white-space: nowrap; display: flex; align-items: center; gap: 4px; }
.question-card { margin-bottom: 20px; border-radius: 12px; }
.question-header { display: flex; align-items: center; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }
.question-actions { margin-left: auto; display: flex; gap: 6px; }
.question-content { font-size: 16px; line-height: 2; margin-bottom: 24px; color: #333; padding: 12px 16px; background: #fafafa; border-radius: 8px; border-left: 4px solid #e94560; }
.question-number { font-weight: bold; color: #e94560; margin-right: 4px; }
.options-area { margin-bottom: 20px; }
.option-group { display: flex; flex-direction: column; gap: 10px; width: 100%; }
.option-item {
  padding: 14px 18px; border: 2px solid #e8e8e8; border-radius: 10px; transition: all 0.25s;
  width: 100%; display: flex; align-items: flex-start; min-height: 48px;
}
.option-item:hover { border-color: #e94560; background: rgba(233,69,96,0.04); transform: translateX(4px); }
.option-label { font-weight: bold; color: #e94560; margin-right: 8px; flex-shrink: 0; min-width: 24px; }
.option-text { flex: 1; line-height: 1.6; }
.answered-options { display: flex; flex-direction: column; gap: 8px; }
.answered-option {
  padding: 14px 18px; border: 2px solid #e8e8e8; border-radius: 10px;
  display: flex; align-items: flex-start; min-height: 48px; transition: all 0.2s;
}
.answered-option.correct-option { background: #f0f9eb; border-color: #67c23a; }
.answered-option.wrong-option { background: #fef0f0; border-color: #f56c6c; }
.option-icon { margin-left: auto; flex-shrink: 0; }
.answer-feedback { padding: 16px 20px; border-radius: 10px; margin-bottom: 20px; }
.feedback-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.feedback-text { font-size: 16px; font-weight: bold; }
.answer-feedback.correct { background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%); color: #67c23a; }
.answer-feedback.wrong { background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%); color: #f56c6c; }
.correct-answer { margin-bottom: 8px; }
.explanation { color: #666; line-height: 1.8; padding-top: 8px; border-top: 1px dashed #ddd; }
.action-area { display: flex; justify-content: center; gap: 12px; padding-top: 10px; }
.action-area .el-button { min-width: 140px; }
.ai-hint-content { line-height: 1.8; color: #333; padding: 10px; background: #f0f5ff; border-radius: 8px; border-left: 3px solid #409eff; }

@media (max-width: 768px) {
  .quiz-session { padding: 0 4px; }
  .question-content { font-size: 14px; padding: 10px 12px; }
  .option-item { padding: 12px 14px; }
  .option-label { min-width: 20px; }
  .action-area { flex-wrap: wrap; }
  .action-area .el-button { min-width: 100px; flex: 1; }
  .question-actions { margin-left: 0; }
  .question-header { gap: 6px; }
}
</style>
