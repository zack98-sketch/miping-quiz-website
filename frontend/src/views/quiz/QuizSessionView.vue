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
          <el-tag :type="questionTypeTag">{{ questionTypeLabel }}</el-tag>
          <el-tag type="info" size="small">{{ currentQuestion.knowledge_point }}</el-tag>
          <el-tag :type="difficultyTag" size="small">{{ difficultyLabel }}</el-tag>
          <div class="question-actions">
            <el-button :type="isFavorited ? 'warning' : 'default'" size="small" :icon="isFavorited ? 'StarFilled' : 'Star'" circle @click="toggleFavorite" />
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
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
            </el-radio>
          </el-radio-group>

          <!-- Multi Choice -->
          <el-checkbox-group v-if="currentQuestion.question_type === 'multi' && !isAnswered" v-model="selectedMultiAnswer" class="option-group">
            <el-checkbox v-for="opt in currentQuestion.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
            </el-checkbox>
          </el-checkbox-group>

          <!-- Judge -->
          <el-radio-group v-if="currentQuestion.question_type === 'judge' && !isAnswered" v-model="selectedAnswer" class="option-group">
            <el-radio v-for="opt in currentQuestion.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              {{ opt.content }}
            </el-radio>
          </el-radio-group>

          <!-- Answered State -->
          <div v-if="isAnswered" class="answered-options">
            <div v-for="opt in currentQuestion.options" :key="opt.label" class="answered-option" :class="getOptionClass(opt)">
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
              <el-icon v-if="isCorrectOption(opt)" class="option-icon"><Check /></el-icon>
              <el-icon v-if="isWrongOption(opt)" class="option-icon"><Close /></el-icon>
            </div>
          </div>
        </div>

        <!-- Answer Feedback -->
        <div v-if="isAnswered" class="answer-feedback" :class="{ correct: lastResult?.is_correct, wrong: !lastResult?.is_correct }">
          <el-icon :size="20"><component :is="lastResult?.is_correct ? 'CircleCheck' : 'CircleClose'" /></el-icon>
          <span>{{ lastResult?.is_correct ? '回答正确！' : '回答错误' }}</span>
          <div v-if="!lastResult?.is_correct" class="correct-answer">
            正确答案：<strong>{{ lastResult?.correct_answer }}</strong>
          </div>
          <div v-if="!lastResult?.is_correct && lastResult?.explanation" class="explanation">
            <strong>解析：</strong>{{ lastResult?.explanation }}
          </div>
        </div>

        <!-- Submit / Next Button -->
        <div class="action-area">
          <el-button v-if="!isAnswered" type="primary" size="large" :disabled="!hasAnswer" @click="submitAnswer">
            提交答案
          </el-button>
          <el-button v-else type="primary" size="large" @click="nextQuestion">
            {{ isLastQuestion ? '查看结果' : '下一题' }}
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { quizApi, favoriteApi } from '../../api/quiz'
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
    if (!res.is_correct) {
      // Error feedback already shown in template
    }
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

async function toggleFavorite() {
  try {
    if (isFavorited.value) {
      await favoriteApi.remove(currentQuestion.value.id)
      isFavorited.value = false
    } else {
      await favoriteApi.add(currentQuestion.value.id)
      isFavorited.value = true
    }
  } catch (e) {
    ElMessage.error('操作失败')
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
.timer { font-size: 18px; font-weight: bold; color: #e94560; white-space: nowrap; }
.question-card { margin-bottom: 20px; }
.question-header { display: flex; align-items: center; gap: 8px; margin-bottom: 15px; }
.question-actions { margin-left: auto; }
.question-content { font-size: 16px; line-height: 1.8; margin-bottom: 20px; color: #333; }
.question-number { font-weight: bold; color: #e94560; margin-right: 4px; }
.options-area { margin-bottom: 20px; }
.option-group { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.option-item { padding: 12px 16px; border: 1px solid #e0e0e0; border-radius: 8px; transition: all 0.2s; width: 100%; }
.option-item:hover { border-color: #e94560; background: rgba(233,69,96,0.05); }
.option-label { font-weight: bold; color: #e94560; margin-right: 4px; }
.answered-options { display: flex; flex-direction: column; gap: 8px; }
.answered-option { padding: 12px 16px; border: 1px solid #e0e0e0; border-radius: 8px; display: flex; align-items: center; }
.answered-option.correct-option { background: #f0f9eb; border-color: #67c23a; }
.answered-option.wrong-option { background: #fef0f0; border-color: #f56c6c; }
.option-icon { margin-left: auto; }
.answer-feedback { padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.answer-feedback.correct { background: #f0f9eb; color: #67c23a; }
.answer-feedback.wrong { background: #fef0f0; color: #f56c6c; }
.correct-answer { margin-left: 20px; }
.explanation { width: 100%; margin-top: 10px; color: #666; line-height: 1.6; }
.action-area { text-align: center; }
.action-area .el-button { min-width: 200px; }

@media (max-width: 768px) {
  .question-content { font-size: 14px; }
  .option-item { padding: 10px 12px; }
}
</style>
