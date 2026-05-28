<template>
  <div class="error-book">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <h2>错题本</h2>
          <div class="header-actions">
            <el-select v-model="filter.knowledge_point" placeholder="知识点筛选" clearable style="width:180px" @change="loadItems">
              <el-option v-for="kp in knowledgePoints" :key="kp" :label="kp" :value="kp" />
            </el-select>
            <el-select v-model="filter.question_type" placeholder="题型筛选" clearable style="width:110px" @change="loadItems">
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multi" />
              <el-option label="判断题" value="judge" />
            </el-select>
            <el-button type="primary" @click="startPractice">错题重做</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="题目" min-width="300">
          <template #default="{ row }">
            <div class="question-preview clickable" @click="redoQuestion(row)">{{ row.question_content }}</div>
          </template>
        </el-table-column>
        <el-table-column label="题型" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.question_type === 'single' ? '' : row.question_type === 'multi' ? 'warning' : 'success'">
              {{ {single:'单选',multi:'多选',judge:'判断'}[row.question_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="知识点" width="120" prop="knowledge_point" show-overflow-tooltip />
        <el-table-column label="错误次数" width="80" prop="error_count" align="center" />
        <el-table-column label="掌握状态" width="100">
          <template #default="{ row }">
            <el-select v-model="row.mastery_status" size="small" @change="updateMastery(row)">
              <el-option value="not_mastered" label="未掌握" />
              <el-option value="partially" label="部分掌握" />
              <el-option value="mastered" label="已掌握" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="redoQuestion(row)">重做</el-button>
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination v-if="total > pageSize" :current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="p => { page = p; loadItems() }" style="margin-top:20px; text-align:center" />
    </el-card>

    <!-- Redo Dialog -->
    <el-dialog v-model="showRedo" title="错题重做" width="600px" :close-on-click-modal="false" :append-to-body="true">
      <div v-if="redoItem">
        <div class="redo-type">
          <el-tag :type="redoItem.question_type === 'single' ? '' : redoItem.question_type === 'multi' ? 'warning' : 'success'" effect="dark">
            {{ {single:'单选题',multi:'多选题',judge:'判断题'}[redoItem.question_type] }}
          </el-tag>
        </div>
        <div class="redo-content">{{ redoItem.question_content }}</div>
        <div class="redo-options">
          <!-- Single Choice -->
          <el-radio-group v-if="redoItem.question_type === 'single' && !redoAnswered" v-model="redoAnswer" class="option-group">
            <el-radio v-for="opt in redoItem.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
            </el-radio>
          </el-radio-group>
          <!-- Multi Choice -->
          <el-checkbox-group v-if="redoItem.question_type === 'multi' && !redoAnswered" v-model="redoMultiAnswer" class="option-group">
            <el-checkbox v-for="opt in redoItem.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
            </el-checkbox>
          </el-checkbox-group>
          <!-- Judge -->
          <el-radio-group v-if="redoItem.question_type === 'judge' && !redoAnswered" v-model="redoAnswer" class="option-group">
            <el-radio v-for="opt in redoItem.options" :key="opt.label" :value="opt.label" class="option-item" size="large">
              {{ opt.content }}
            </el-radio>
          </el-radio-group>
          <!-- Answered -->
          <div v-if="redoAnswered" class="answered-options">
            <div v-for="opt in redoItem.options" :key="opt.label" class="answered-option" :class="getRedoOptionClass(opt)">
              <span class="option-label">{{ opt.label }}.</span> {{ opt.content }}
              <el-icon v-if="redoItem.correct_answer?.includes(opt.label)" class="option-icon" color="#67c23a"><CircleCheck /></el-icon>
              <el-icon v-if="isRedoWrong(opt)" class="option-icon" color="#f56c6c"><CircleClose /></el-icon>
            </div>
          </div>
        </div>
        <!-- Result -->
        <div v-if="redoAnswered" class="redo-result" :class="{ correct: redoCorrect, wrong: !redoCorrect }">
          <el-icon :size="20"><component :is="redoCorrect ? 'CircleCheck' : 'CircleClose'" /></el-icon>
          <span>{{ redoCorrect ? '回答正确！已从错题本移除' : '回答错误，继续加油！' }}</span>
          <div v-if="!redoCorrect" class="correct-answer">正确答案：<strong>{{ redoItem.correct_answer }}</strong></div>
          <div v-if="redoItem.explanation" class="explanation">解析：{{ redoItem.explanation }}</div>
        </div>
      </div>
      <template #footer>
        <el-button v-if="!redoAnswered" type="primary" :disabled="!redoHasAnswer" @click="submitRedo">提交答案</el-button>
        <el-button v-else @click="showRedo = false; loadItems()">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="showDetail" title="题目详情" width="600px" :append-to-body="true">
      <div v-if="detailItem">
        <div class="detail-content">{{ detailItem.question_content }}</div>
        <div class="detail-options">
          <div v-for="opt in detailItem.options" :key="opt.label" class="detail-option" :class="{ correct: detailItem.correct_answer?.includes(opt.label) }">
            {{ opt.label }}. {{ opt.content }}
          </div>
        </div>
        <div class="detail-answer">正确答案：<strong>{{ detailItem.correct_answer }}</strong></div>
        <div class="detail-user-answer">你的答案：<strong class="wrong">{{ detailItem.user_answer }}</strong></div>
        <div v-if="detailItem.explanation" class="detail-explanation">解析：{{ detailItem.explanation }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { errorBookApi, questionApi, quizApi } from '../../api/quiz'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const knowledgePoints = ref([])
const filter = ref({ knowledge_point: '', question_type: '' })
const showDetail = ref(false)
const detailItem = ref(null)

// Redo state
const showRedo = ref(false)
const redoItem = ref(null)
const redoAnswer = ref('')
const redoMultiAnswer = ref([])
const redoAnswered = ref(false)
const redoCorrect = ref(false)

const redoHasAnswer = computed(() => {
  if (!redoItem.value) return false
  if (redoItem.value.question_type === 'multi') return redoMultiAnswer.value.length > 0
  return !!redoAnswer.value
})

onMounted(async () => {
  loadItems()
  try {
    const res = await questionApi.getKnowledgePoints()
    knowledgePoints.value = res.knowledge_points || []
  } catch {}
})

async function loadItems() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filter.value.knowledge_point) params.knowledge_point = filter.value.knowledge_point
    if (filter.value.question_type) params.question_type = filter.value.question_type
    const res = await errorBookApi.getItems(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function viewDetail(row) {
  detailItem.value = row
  showDetail.value = true
}

function redoQuestion(row) {
  redoItem.value = row
  redoAnswer.value = ''
  redoMultiAnswer.value = []
  redoAnswered.value = false
  redoCorrect.value = false
  showRedo.value = true
}

async function submitRedo() {
  if (!redoItem.value) return
  let answer = redoAnswer.value
  if (redoItem.value.question_type === 'multi') {
    answer = redoMultiAnswer.value.sort().join(',')
  }
  // Compare with correct answer
  const correct = redoItem.value.correct_answer
  const isCorrect = answer === correct || (answer.split(',').sort().join(',') === correct.split(',').sort().join(','))
  redoCorrect.value = isCorrect
  redoAnswered.value = true

  // If correct, auto-remove from error book
  if (isCorrect) {
    try {
      await errorBookApi.deleteItem(redoItem.value.id)
    } catch {}
  }
}

function getRedoOptionClass(opt) {
  if (!redoItem.value) return ''
  if (redoItem.value.correct_answer?.includes(opt.label)) return 'correct-option'
  const answer = redoAnswer.value || redoMultiAnswer.value.sort().join(',')
  if (answer.includes(opt.label) && !redoItem.value.correct_answer?.includes(opt.label)) return 'wrong-option'
  return ''
}

function isRedoWrong(opt) {
  const answer = redoAnswer.value || redoMultiAnswer.value.sort().join(',')
  return answer?.includes(opt.label) && !redoItem.value?.correct_answer?.includes(opt.label)
}

async function updateMastery(row) {
  try {
    await errorBookApi.updateItem(row.id, { mastery_status: row.mastery_status })
  } catch {}
}

async function deleteItem(row) {
  try {
    await ElMessageBox.confirm('确定删除该错题记录？', '提示')
    await errorBookApi.deleteItem(row.id)
    ElMessage.success('删除成功')
    loadItems()
  } catch {}
}

async function startPractice() {
  try {
    const res = await errorBookApi.practice({ count: 20 })
    router.push(`/quiz/session/${res.session_id}`)
  } catch (e) {
    ElMessage.error(e.detail || '没有可练习的错题')
  }
}
</script>

<style scoped>
.error-book { max-width: 1200px; margin: 0 auto; }
.main-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.card-header h2 { margin: 0; }
.header-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.question-preview { max-height: 60px; overflow: hidden; text-overflow: ellipsis; line-height: 1.6; }
.question-preview.clickable { cursor: pointer; color: #409eff; }
.question-preview.clickable:hover { text-decoration: underline; }
/* Redo dialog */
.redo-type { margin-bottom: 12px; }
.redo-content { font-size: 16px; line-height: 2; margin-bottom: 20px; padding: 12px 16px; background: #fafafa; border-radius: 8px; border-left: 4px solid #e94560; }
.redo-options { margin-bottom: 16px; }
.option-group { display: flex; flex-direction: column; gap: 10px; width: 100%; }
.option-item { padding: 12px 16px; border: 2px solid #e8e8e8; border-radius: 8px; width: 100%; }
.option-item:hover { border-color: #e94560; background: rgba(233,69,96,0.04); }
.option-label { font-weight: bold; color: #e94560; margin-right: 6px; }
.answered-options { display: flex; flex-direction: column; gap: 8px; }
.answered-option { padding: 12px 16px; border: 2px solid #e8e8e8; border-radius: 8px; display: flex; align-items: center; }
.answered-option.correct-option { background: #f0f9eb; border-color: #67c23a; }
.answered-option.wrong-option { background: #fef0f0; border-color: #f56c6c; }
.option-icon { margin-left: auto; }
.redo-result { padding: 14px; border-radius: 8px; margin-top: 12px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.redo-result.correct { background: #f0f9eb; color: #67c23a; }
.redo-result.wrong { background: #fef0f0; color: #f56c6c; }
.correct-answer { margin-left: 16px; }
.explanation { width: 100%; margin-top: 8px; color: #666; line-height: 1.6; }
/* Detail */
.detail-content { font-size: 16px; line-height: 1.8; margin-bottom: 15px; }
.detail-options { margin-bottom: 15px; }
.detail-option { padding: 8px 12px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 5px; }
.detail-option.correct { background: #f0f9eb; border-color: #67c23a; }
.detail-answer { color: #67c23a; margin-bottom: 8px; }
.detail-user-answer { margin-bottom: 8px; }
.wrong { color: #f56c6c; }
.detail-explanation { color: #666; line-height: 1.6; }

@media (max-width: 768px) {
  .header-actions { flex-direction: column; }
  .redo-content { font-size: 14px; }
}
</style>
