<template>
  <div class="exam-session" v-loading="loading">
    <div v-if="examData" class="exam-container">
      <!-- Exam in progress -->
      <template v-if="!submitted">
        <!-- Header with timer -->
        <div class="exam-header">
          <h2>模拟考试</h2>
          <div class="exam-timer" :class="{ warning: remainingTime < 300, danger: remainingTime < 60 }">
            <el-icon><Timer /></el-icon> {{ formattedTime }}
          </div>
        </div>

        <!-- Question Navigation -->
        <el-card class="nav-card" shadow="never">
          <div class="question-nav">
            <div v-for="(q, i) in examData.questions" :key="q.id"
              class="nav-item" :class="getNavClass(q, i)"
              @click="scrollToQuestion(i)">
              {{ i + 1 }}
            </div>
          </div>
          <div class="nav-legend">
            <span class="legend-item"><span class="dot current"></span>当前</span>
            <span class="legend-item"><span class="dot answered"></span>已答</span>
            <span class="legend-item"><span class="dot unanswered"></span>未答</span>
          </div>
        </el-card>

        <!-- Questions - No AI, No explanation during exam -->
        <div v-for="(q, i) in examData.questions" :key="q.id" class="exam-question" :id="`q-${i}`">
          <div class="question-header">
            <span class="question-number">{{ i + 1 }}.</span>
            <el-tag :type="q.question_type === 'single' ? '' : q.question_type === 'multi' ? 'warning' : 'success'" size="small" effect="dark">
              {{ {single:'单选',multi:'多选',judge:'判断'}[q.question_type] }}
            </el-tag>
          </div>
          <div class="question-title">{{ q.content }}</div>
          <div class="question-options">
            <el-radio-group v-if="q.question_type === 'single' || q.question_type === 'judge'" v-model="answers[q.id]" class="option-group">
              <el-radio v-for="opt in q.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
                <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
              </el-radio>
            </el-radio-group>
            <el-checkbox-group v-else v-model="multiAnswers[q.id]" class="option-group">
              <el-checkbox v-for="opt in q.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
                <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>

        <!-- Submit -->
        <div class="submit-area">
          <div class="submit-info">已答 {{ answeredCount }}/{{ examData.questions.length }} 题</div>
          <el-button type="primary" size="large" :loading="submitting" @click="confirmSubmit" class="submit-btn">交卷</el-button>
        </div>
      </template>

      <!-- Exam Result - Show answers and explanations -->
      <template v-else>
        <div class="result-header">
          <h2>考试结果</h2>
          <el-button type="primary" @click="router.push('/exams')">返回列表</el-button>
        </div>

        <!-- Score Summary -->
        <el-card class="score-card" shadow="hover">
          <div class="score-summary">
            <div class="score-item">
              <div class="score-value" :class="scoreClass">{{ examResult.score.toFixed(1) }}</div>
              <div class="score-label">得分</div>
            </div>
            <div class="score-item">
              <div class="score-value correct">{{ examResult.correct_count }}</div>
              <div class="score-label">正确</div>
            </div>
            <div class="score-item">
              <div class="score-value wrong">{{ examResult.total_count - examResult.correct_count }}</div>
              <div class="score-label">错误</div>
            </div>
            <div class="score-item">
              <div class="score-value">{{ examResult.total_count }}</div>
              <div class="score-label">总题数</div>
            </div>
          </div>
          <div class="time-spent">用时：{{ formatTimeSpent(examResult.time_spent) }}</div>
        </el-card>

        <!-- Result Questions with answers and explanations -->
        <div v-for="(q, i) in examData.questions" :key="q.id" class="result-question" :class="getResultClass(q)">
          <div class="question-header">
            <span class="question-number">{{ i + 1 }}.</span>
            <el-tag :type="q.question_type === 'single' ? '' : q.question_type === 'multi' ? 'warning' : 'success'" size="small" effect="dark">
              {{ {single:'单选',multi:'多选',judge:'判断'}[q.question_type] }}
            </el-tag>
            <el-tag :type="isCorrect(q) ? 'success' : 'danger'" size="small">
              {{ isCorrect(q) ? '正确' : '错误' }}
            </el-tag>
            <div class="question-actions">
              <el-tooltip content="AI分析" placement="top">
                <el-button type="primary" size="small" :icon="'ChatDotRound'" circle @click="showAiAnalysis(q, i)" />
              </el-tooltip>
            </div>
          </div>
          <div class="question-title">{{ q.content }}</div>
          
          <!-- Options with correct/wrong marking -->
          <div class="question-options">
            <div v-for="opt in q.options" :key="opt.label" class="result-option" :class="getOptionResultClass(q, opt)">
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
              <el-icon v-if="isCorrectOption(q, opt)" class="option-icon" color="#67c23a"><CircleCheck /></el-icon>
              <el-icon v-if="isWrongOption(q, opt)" class="option-icon" color="#f56c6c"><CircleClose /></el-icon>
            </div>
          </div>
          
          <!-- Answer info -->
          <div class="answer-info">
            <div class="user-answer">你的答案：<strong :class="isCorrect(q) ? 'correct' : 'wrong'">{{ getUserAnswer(q) }}</strong></div>
            <div v-if="!isCorrect(q)" class="correct-answer">正确答案：<strong>{{ q.correct_answer }}</strong></div>
            <div v-if="q.explanation" class="explanation"><strong>解析：</strong>{{ q.explanation }}</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="result-actions">
          <el-button type="primary" size="large" @click="redoExam">重做试卷</el-button>
          <el-button size="large" @click="router.push('/exams')">返回列表</el-button>
        </div>
      </template>
    </div>

    <!-- AI Analysis Dialog -->
    <el-dialog v-model="aiDialogVisible" title="AI 题目分析" width="600px" :append-to-body="true">
      <div v-if="aiLoading" style="text-align:center;padding:20px">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon> 正在分析...
      </div>
      <div v-else-if="aiContent" class="ai-content" v-html="formatAiContent(aiContent)"></div>
      <template #footer>
        <el-button @click="aiDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="requestDeepAnalysis" :loading="aiLoading">深度分析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { examApi, aiHintApi } from '../../api/quiz'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const examId = computed(() => route.params.id)
const loading = ref(true)
const submitting = ref(false)
const examData = ref(null)
const answers = ref({})
const multiAnswers = ref({})
const remainingTime = ref(0)
const currentQuestionIndex = ref(0)
const submitted = ref(false)
const examResult = ref(null)
let timer = null

// AI
const aiDialogVisible = ref(false)
const aiLoading = ref(false)
const aiContent = ref('')
const currentAiQuestion = ref(null)

const formattedTime = computed(() => {
  const h = Math.floor(remainingTime.value / 3600)
  const m = Math.floor((remainingTime.value % 3600) / 60)
  const s = remainingTime.value % 60
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const answeredCount = computed(() => {
  if (!examData.value) return 0
  let count = 0
  for (const q of examData.value.questions) {
    if (q.question_type === 'multi') {
      if (multiAnswers.value[q.id]?.length > 0) count++
    } else {
      if (answers.value[q.id]) count++
    }
  }
  return count
})

const scoreClass = computed(() => {
  if (!examResult.value) return ''
  const percent = examResult.value.score / 100
  if (percent >= 0.8) return 'excellent'
  if (percent >= 0.6) return 'good'
  return 'poor'
})

onMounted(() => {
  const data = sessionStorage.getItem(`exam_${examId.value}`)
  if (data) {
    examData.value = JSON.parse(data)
    remainingTime.value = examData.value.time_limit * 60
    timer = setInterval(() => {
      remainingTime.value--
      if (remainingTime.value <= 0) {
        clearInterval(timer)
        submitExam()
      }
    }, 1000)
  }
  loading.value = false
})

onUnmounted(() => { if (timer) clearInterval(timer) })

function getNavClass(q, i) {
  const isAnswered = q.question_type === 'multi'
    ? (multiAnswers.value[q.id]?.length > 0)
    : !!answers.value[q.id]
  if (i === currentQuestionIndex.value) return 'current'
  return isAnswered ? 'answered' : 'unanswered'
}

function scrollToQuestion(index) {
  currentQuestionIndex.value = index
  const el = document.getElementById(`q-${index}`)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function confirmSubmit() {
  const unanswered = examData.value.questions.length - answeredCount.value
  if (unanswered > 0) {
    try {
      await ElMessageBox.confirm(`还有 ${unanswered} 题未作答，确定交卷？`, '提示', { type: 'warning' })
    } catch { return }
  }
  submitExam()
}

async function submitExam() {
  submitting.value = true
  try {
    const answerList = []
    for (const [qid, ans] of Object.entries(answers.value)) {
      if (ans) answerList.push({ question_id: parseInt(qid), answer: ans })
    }
    for (const [qid, ansArr] of Object.entries(multiAnswers.value)) {
      if (ansArr?.length > 0) answerList.push({ question_id: parseInt(qid), answer: ansArr.sort().join(',') })
    }
    const timeSpent = (examData.value.time_limit * 60) - remainingTime.value
    const res = await examApi.submit(examId.value, { answers: answerList, time_spent: timeSpent })
    examResult.value = res
    submitted.value = true
    // Merge result data with questions
    if (res.questions) {
      examData.value.questions = res.questions
    }
    ElMessage.success(`考试完成！得分：${res.score.toFixed(1)}分`)
  } catch (e) { ElMessage.error(e.detail || '交卷失败') }
  finally { submitting.value = false }
}

function isCorrect(q) {
  const userAns = getUserAnswer(q)
  if (!userAns) return false
  const correct = q.correct_answer || ''
  return userAns === correct || userAns.split(',').sort().join(',') === correct.split(',').sort().join(',')
}

function getUserAnswer(q) {
  if (q.question_type === 'multi') {
    return multiAnswers.value[q.id]?.sort().join(',') || ''
  }
  return answers.value[q.id] || ''
}

function getResultClass(q) {
  return isCorrect(q) ? 'correct' : 'wrong'
}

function isCorrectOption(q, opt) {
  return (q.correct_answer || '').includes(opt.label)
}

function isWrongOption(q, opt) {
  const userAns = getUserAnswer(q)
  return userAns.includes(opt.label) && !isCorrectOption(q, opt)
}

function getOptionResultClass(q, opt) {
  if (isCorrectOption(q, opt)) return 'correct-option'
  if (isWrongOption(q, opt)) return 'wrong-option'
  return ''
}

function formatTimeSpent(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}分${s}秒`
}

function redoExam() {
  // Reset answers and allow redo with answers shown
  ElMessage.info('重做模式下可查看答案和解析')
}

// AI Analysis
async function showAiAnalysis(q, index) {
  currentAiQuestion.value = q
  aiContent.value = ''
  aiDialogVisible.value = true
  await requestDeepAnalysis()
}

async function requestDeepAnalysis() {
  if (!currentAiQuestion.value) return
  aiLoading.value = true
  try {
    const res = await aiHintApi.request({ 
      question_id: currentAiQuestion.value.id, 
      level: 'deep' 
    })
    aiContent.value = res.hint_content
  } catch (e) {
    aiContent.value = e.detail || 'AI分析暂不可用'
  } finally {
    aiLoading.value = false
  }
}

function formatAiContent(content) {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/- (.*?)(?=<br>|$)/g, '• $1')
}
</script>

<style scoped>
.exam-session { max-width: 900px; margin: 0 auto; }
.exam-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.exam-timer { font-size: 22px; font-weight: bold; color: #e94560; display: flex; align-items: center; gap: 6px; }
.exam-timer.warning { color: #e6a23c; }
.exam-timer.danger { color: #f56c6c; animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0.5; } }

/* Navigation */
.nav-card { margin-bottom: 16px; border-radius: 12px; }
.question-nav { display: flex; flex-wrap: wrap; gap: 6px; }
.nav-item { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s; border: 2px solid #e0e0e0; color: #999; }
.nav-item:hover { border-color: #e94560; color: #e94560; }
.nav-item.current { background: #e94560; color: #fff; border-color: #e94560; }
.nav-item.answered { background: #67c23a; color: #fff; border-color: #67c23a; }
.nav-item.unanswered { background: #fff; color: #999; border-color: #e0e0e0; }
.nav-legend { display: flex; gap: 16px; margin-top: 10px; font-size: 12px; color: #999; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.dot.current { background: #e94560; }
.dot.answered { background: #67c23a; }
.dot.unanswered { background: #fff; border: 1px solid #e0e0e0; }

/* Questions */
.exam-question { margin-bottom: 12px; padding: 16px 20px; background: #fff; border-radius: 10px; border: 1px solid #eee; }
.question-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.question-number { font-weight: bold; color: #e94560; font-size: 16px; }
.question-title { font-size: 15px; line-height: 1.8; margin-bottom: 12px; }
.question-actions { margin-left: auto; }
.option-group { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.option-item { padding: 10px 14px; border: 2px solid #e8e8e8; border-radius: 8px; width: 100%; }
.option-item:hover { border-color: #e94560; background: rgba(233,69,96,0.04); }
.option-label { font-weight: bold; color: #e94560; margin-right: 6px; }

/* Submit */
.submit-area { text-align: center; margin: 24px 0; padding: 20px; background: #fff; border-radius: 12px; }
.submit-info { color: #666; margin-bottom: 12px; font-size: 14px; }
.submit-btn { min-width: 200px; }

/* Result */
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.score-card { margin-bottom: 20px; border-radius: 12px; }
.score-summary { display: flex; justify-content: space-around; text-align: center; }
.score-item { padding: 10px; }
.score-value { font-size: 32px; font-weight: bold; color: #333; }
.score-value.excellent { color: #67c23a; }
.score-value.good { color: #e6a23c; }
.score-value.poor { color: #f56c6c; }
.score-value.correct { color: #67c23a; }
.score-value.wrong { color: #f56c6c; }
.score-label { font-size: 14px; color: #999; margin-top: 4px; }
.time-spent { text-align: center; color: #666; margin-top: 10px; }

.result-question { margin-bottom: 12px; padding: 16px 20px; background: #fff; border-radius: 10px; border: 2px solid #eee; }
.result-question.correct { border-color: #67c23a; }
.result-question.wrong { border-color: #f56c6c; }
.result-option { padding: 10px 14px; border: 2px solid #e8e8e8; border-radius: 8px; margin-bottom: 6px; display: flex; align-items: center; }
.result-option.correct-option { background: #f0f9eb; border-color: #67c23a; }
.result-option.wrong-option { background: #fef0f0; border-color: #f56c6c; }
.option-icon { margin-left: auto; }
.answer-info { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #ddd; }
.user-answer { margin-bottom: 6px; }
.correct-answer { margin-bottom: 6px; color: #67c23a; }
.explanation { color: #666; line-height: 1.6; }
.correct { color: #67c23a; }
.wrong { color: #f56c6c; }

.result-actions { text-align: center; margin: 24px 0; display: flex; justify-content: center; gap: 16px; }

/* AI */
.ai-content { line-height: 1.8; padding: 10px; background: #f0f5ff; border-radius: 8px; border-left: 3px solid #409eff; }

@media (max-width: 768px) {
  .nav-item { width: 28px; height: 28px; font-size: 12px; }
  .exam-question, .result-question { padding: 12px 14px; }
  .question-title { font-size: 14px; }
  .score-value { font-size: 24px; }
}
</style>
