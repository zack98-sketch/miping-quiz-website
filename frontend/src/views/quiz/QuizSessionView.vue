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
            <el-tooltip content="AI智能辅导" placement="top">
              <el-button type="primary" size="small" :icon="'ChatDotRound'" circle @click="showAiDialog" />
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

      <!-- AI Chat Dialog -->
      <el-dialog v-model="aiDialogVisible" title="AI 智能辅导" width="600px" :append-to-body="true" class="ai-dialog" @close="aiMessages = []">
        <div class="ai-chat-container">
          <!-- Quick hint buttons -->
          <div class="ai-quick-actions">
            <el-button size="small" @click="requestAiHint('light')">💡 轻度提示</el-button>
            <el-button size="small" type="warning" @click="requestAiHint('medium')">🔍 中度提示</el-button>
            <el-button size="small" type="danger" @click="requestAiHint('deep')">📚 深度解析</el-button>
          </div>
          
          <!-- Chat messages -->
          <div class="ai-messages" ref="aiMessagesRef">
            <div v-for="(msg, i) in aiMessages" :key="i" class="ai-message" :class="msg.role">
              <div class="message-avatar">
                <el-avatar v-if="msg.role === 'assistant'" :size="32" style="background:#409eff">AI</el-avatar>
                <el-avatar v-else :size="32" style="background:#67c23a">我</el-avatar>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
              </div>
            </div>
            <div v-if="aiLoading" class="ai-message assistant">
              <div class="message-avatar"><el-avatar :size="32" style="background:#409eff">AI</el-avatar></div>
              <div class="message-content"><div class="message-text"><el-icon class="is-loading"><Loading /></el-icon> 思考中...</div></div>
            </div>
          </div>
          
          <!-- Input area -->
          <div class="ai-input-area">
            <el-input v-model="aiInput" placeholder="输入你的问题，与AI深入讨论..." @keyup.enter="sendAiMessage" :disabled="aiLoading">
              <template #append>
                <el-button type="primary" @click="sendAiMessage" :loading="aiLoading" :disabled="!aiInput.trim()">发送</el-button>
              </template>
            </el-input>
          </div>
        </div>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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

// AI Chat
const aiDialogVisible = ref(false)
const aiLoading = ref(false)
const aiMessages = ref([])
const aiInput = ref('')
const aiMessagesRef = ref(null)

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
    // Reset AI chat
    aiMessages.value = []
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
  if (currentIndex.value > 0) {
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

// AI Chat
function showAiDialog() {
  aiDialogVisible.value = true
}

async function requestAiHint(level) {
  if (!currentQuestion.value) return
  aiLoading.value = true
  try {
    const res = await aiHintApi.request({ question_id: currentQuestion.value.id, level })
    aiMessages.value.push({ role: 'assistant', content: res.hint_content })
    scrollToBottom()
  } catch (e) {
    aiMessages.value.push({ role: 'assistant', content: e.detail || '提示服务暂不可用' })
  } finally {
    aiLoading.value = false
  }
}

async function sendAiMessage() {
  if (!aiInput.value.trim() || aiLoading.value) return
  const userMessage = aiInput.value.trim()
  aiInput.value = ''
  
  aiMessages.value.push({ role: 'user', content: userMessage })
  aiLoading.value = true
  
  try {
    // Build context with question info
    const systemPrompt = buildSystemPrompt()
    const messages = [
      { role: 'system', content: systemPrompt },
      ...aiMessages.value.map(m => ({ role: m.role, content: m.content }))
    ]
    
    const res = await aiHintApi.chat({
      question_id: currentQuestion.value.id,
      messages: messages
    })
    aiMessages.value.push({ role: 'assistant', content: res.content })
    scrollToBottom()
  } catch (e) {
    aiMessages.value.push({ role: 'assistant', content: e.detail || 'AI服务暂时不可用' })
  } finally {
    aiLoading.value = false
  }
}

function buildSystemPrompt() {
  const q = currentQuestion.value
  const options = q.options?.map(o => `${o.label}. ${o.content}`).join('\n') || ''
  return `你是一个专业的密码学考试辅导老师。当前题目信息如下：

【题目】${q.content}

【选项】
${options}

【知识点】${q.knowledge_point || '密码学'}

请根据学生的问题给出专业、耐心的解答。注意：
1. 不要直接给出答案，要引导学生思考
2. 解释要清晰易懂，结合具体概念
3. 如果学生问的是相关知识点，可以适当拓展
4. 用中文回答，语言简洁专业`
}

function formatMessage(content) {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/- (.*?)(?=<br>|$)/g, '• $1')
}

function scrollToBottom() {
  nextTick(() => {
    if (aiMessagesRef.value) {
      aiMessagesRef.value.scrollTop = aiMessagesRef.value.scrollHeight
    }
  })
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
.option-item { padding: 14px 18px; border: 2px solid #e8e8e8; border-radius: 10px; transition: all 0.25s; width: 100%; display: flex; align-items: flex-start; min-height: 48px; }
.option-item:hover { border-color: #e94560; background: rgba(233,69,96,0.04); transform: translateX(4px); }
.option-label { font-weight: bold; color: #e94560; margin-right: 8px; flex-shrink: 0; min-width: 24px; }
.option-text { flex: 1; line-height: 1.6; }
.answered-options { display: flex; flex-direction: column; gap: 8px; }
.answered-option { padding: 14px 18px; border: 2px solid #e8e8e8; border-radius: 10px; display: flex; align-items: flex-start; min-height: 48px; transition: all 0.2s; }
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

/* AI Chat */
.ai-chat-container { display: flex; flex-direction: column; height: 500px; }
.ai-quick-actions { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.ai-messages { flex: 1; overflow-y: auto; padding: 12px; background: #f5f7fa; border-radius: 8px; margin-bottom: 12px; }
.ai-message { display: flex; gap: 10px; margin-bottom: 16px; }
.ai-message.user { flex-direction: row-reverse; }
.message-avatar { flex-shrink: 0; }
.message-content { flex: 1; max-width: 80%; }
.message-text { padding: 10px 14px; border-radius: 12px; line-height: 1.6; font-size: 14px; }
.ai-message.assistant .message-text { background: #fff; border: 1px solid #e4e7ed; }
.ai-message.user .message-text { background: #409eff; color: #fff; }
.ai-input-area { flex-shrink: 0; }

@media (max-width: 768px) {
  .quiz-session { padding: 0 4px; }
  .question-content { font-size: 14px; padding: 10px 12px; }
  .option-item { padding: 12px 14px; }
  .option-label { min-width: 20px; }
  .action-area { flex-wrap: wrap; }
  .action-area .el-button { min-width: 100px; flex: 1; }
  .question-actions { margin-left: 0; }
  .question-header { gap: 6px; }
  .ai-chat-container { height: 400px; }
}
</style>
