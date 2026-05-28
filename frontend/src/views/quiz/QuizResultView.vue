<template>
  <div class="quiz-result" v-loading="loading">
    <el-card v-if="result" class="result-card" shadow="hover">
      <h2>答题结果</h2>
      <el-row :gutter="20" class="summary-row">
        <el-col :span="6"><div class="summary-item"><div class="value">{{ result.session.total_count }}</div><div class="label">总题数</div></div></el-col>
        <el-col :span="6"><div class="summary-item success"><div class="value">{{ result.session.correct_count }}</div><div class="label">正确</div></div></el-col>
        <el-col :span="6"><div class="summary-item error"><div class="value">{{ result.session.total_count - result.session.correct_count }}</div><div class="label">错误</div></div></el-col>
        <el-col :span="6"><div class="summary-item"><div class="value">{{ result.accuracy }}%</div><div class="label">正确率</div></div></el-col>
      </el-row>
      
      <div v-if="result.error_questions.length > 0" class="error-section">
        <h3>错题详情</h3>
        <div v-for="(eq, i) in result.error_questions" :key="i" class="error-item">
          <div class="error-question">{{ eq.content }}</div>
          <div class="error-answers">
            <span class="wrong">你的答案：{{ eq.user_answer }}</span>
            <span class="correct">正确答案：{{ eq.correct_answer }}</span>
          </div>
          <div v-if="eq.explanation" class="error-explanation">解析：{{ eq.explanation }}</div>
        </div>
      </div>
      
      <div class="action-area">
        <el-button type="primary" @click="$router.push('/')">继续答题</el-button>
        <el-button @click="$router.push('/error-book')">查看错题本</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { quizApi } from '../../api/quiz'

const route = useRoute()
const loading = ref(true)
const result = ref(null)

onMounted(async () => {
  try {
    result.value = await quizApi.getResult(route.params.id)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.quiz-result { max-width: 800px; margin: 0 auto; }
.result-card h2 { text-align: center; margin-bottom: 20px; }
.summary-row { margin-bottom: 30px; }
.summary-item { text-align: center; padding: 15px; background: #f5f5f5; border-radius: 8px; }
.summary-item .value { font-size: 28px; font-weight: bold; color: #333; }
.summary-item .label { font-size: 13px; color: #999; margin-top: 5px; }
.summary-item.success .value { color: #67c23a; }
.summary-item.error .value { color: #f56c6c; }
.error-section { margin-top: 20px; }
.error-section h3 { margin-bottom: 15px; color: #f56c6c; }
.error-item { padding: 15px; border: 1px solid #fde2e2; border-radius: 8px; margin-bottom: 10px; }
.error-question { font-size: 14px; margin-bottom: 8px; }
.error-answers { display: flex; gap: 20px; font-size: 13px; }
.wrong { color: #f56c6c; }
.correct { color: #67c23a; }
.error-explanation { margin-top: 8px; font-size: 13px; color: #666; }
.action-area { text-align: center; margin-top: 30px; }
</style>
