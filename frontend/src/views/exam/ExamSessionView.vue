<template>
  <div class="exam-session" v-loading="loading">
    <div v-if="examData" class="exam-container">
      <div class="exam-header">
        <h2>在线考试</h2>
        <div class="exam-timer">
          <el-icon><Timer /></el-icon> 剩余时间: {{ formattedTime }}
        </div>
      </div>
      <div v-for="(q, i) in examData.questions" :key="q.id" class="exam-question">
        <div class="question-title">{{ i + 1 }}. {{ q.content }}</div>
        <el-radio-group v-if="q.question_type === 'single' || q.question_type === 'judge'" v-model="answers[q.id]" class="option-group">
          <el-radio v-for="opt in q.options" :key="opt.label" :value="opt.label">{{ opt.label }}. {{ opt.content }}</el-radio>
        </el-radio-group>
        <el-checkbox-group v-else v-model="multiAnswers[q.id]" class="option-group">
          <el-checkbox v-for="opt in q.options" :key="opt.label" :value="opt.label">{{ opt.label }}. {{ opt.content }}</el-checkbox>
        </el-checkbox-group>
      </div>
      <div class="submit-area">
        <el-button type="primary" size="large" :loading="submitting" @click="submitExam">交卷</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { examApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const examId = computed(() => route.params.id)
const loading = ref(true)
const submitting = ref(false)
const examData = ref(null)
const answers = ref({})
const multiAnswers = ref({})
const remainingTime = ref(0)
let timer = null

const formattedTime = computed(() => {
  const m = Math.floor(remainingTime.value / 60)
  const s = remainingTime.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
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
.exam-session { max-width: 800px; margin: 0 auto; }
.exam-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.exam-timer { font-size: 20px; font-weight: bold; color: #e94560; }
.exam-question { margin-bottom: 20px; padding: 15px; background: #fff; border-radius: 8px; border: 1px solid #eee; }
.question-title { font-size: 15px; line-height: 1.6; margin-bottom: 10px; }
.option-group { display: flex; flex-direction: column; gap: 8px; }
.submit-area { text-align: center; margin-top: 30px; }
</style>
