<template>
  <div class="error-book">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h2>错题本</h2>
          <div class="header-actions">
            <el-select v-model="filter.knowledge_point" placeholder="知识点筛选" clearable style="width:200px" @change="loadItems">
              <el-option v-for="kp in knowledgePoints" :key="kp" :label="kp" :value="kp" />
            </el-select>
            <el-select v-model="filter.question_type" placeholder="题型筛选" clearable style="width:120px" @change="loadItems">
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
            <div class="question-preview">{{ row.question_content }}</div>
          </template>
        </el-table-column>
        <el-table-column label="题型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ {single:'单选',multi:'多选',judge:'判断'}[row.question_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="知识点" width="120" prop="knowledge_point" />
        <el-table-column label="错误次数" width="80" prop="error_count" />
        <el-table-column label="掌握状态" width="100">
          <template #default="{ row }">
            <el-select v-model="row.mastery_status" size="small" @change="updateMastery(row)">
              <el-option value="not_mastered" label="未掌握" />
              <el-option value="partially" label="部分掌握" />
              <el-option value="mastered" label="已掌握" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看</el-button>
            <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination v-if="total > pageSize" :current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="p => { page = p; loadItems() }" style="margin-top:20px; text-align:center" />
    </el-card>

    <!-- Detail Dialog -->
    <el-dialog v-model="showDetail" title="题目详情" width="600px">
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
import { ref, onMounted } from 'vue'
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
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.card-header h2 { margin: 0; }
.header-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.question-preview { max-height: 60px; overflow: hidden; text-overflow: ellipsis; }
.detail-content { font-size: 16px; line-height: 1.8; margin-bottom: 15px; }
.detail-options { margin-bottom: 15px; }
.detail-option { padding: 8px 12px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 5px; }
.detail-option.correct { background: #f0f9eb; border-color: #67c23a; }
.detail-answer { color: #67c23a; margin-bottom: 8px; }
.detail-user-answer { margin-bottom: 8px; }
.wrong { color: #f56c6c; }
.detail-explanation { color: #666; line-height: 1.6; }
</style>
