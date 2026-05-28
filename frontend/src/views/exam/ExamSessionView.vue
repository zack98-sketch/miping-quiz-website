<template>
  <div class="exam-session" v-loading="loading">
    <div v-if="examData" class="exam-container">
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

      <!-- Questions -->
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { examApi } from '../../api/quiz'
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
let timer = null

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
    ElMessage.success(`考试完成！得分：${res.score.toFixed(1)}分，正确：${res.correct_count}/${res.total_count}`)
    router.push('/exams')
  } catch (e) { ElMessage.error(e.detail || '交卷失败') }
  finally { submitting.value = false }
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
.nav-item {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s;
  border: 2px solid #e0e0e0; color: #999;
}
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
.question-options {}
.option-group { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.option-item { padding: 10px 14px; border: 2px solid #e8e8e8; border-radius: 8px; width: 100%; }
.option-item:hover { border-color: #e94560; background: rgba(233,69,96,0.04); }
.option-label { font-weight: bold; color: #e94560; margin-right: 6px; }

/* Submit */
.submit-area { text-align: center; margin: 24px 0; padding: 20px; background: #fff; border-radius: 12px; }
.submit-info { color: #666; margin-bottom: 12px; font-size: 14px; }
.submit-btn { min-width: 200px; }

@media (max-width: 768px) {
  .nav-item { width: 28px; height: 28px; font-size: 12px; }
  .exam-question { padding: 12px 14px; }
  .question-title { font-size: 14px; }
}
</style>
