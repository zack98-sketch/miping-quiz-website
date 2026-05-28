<template>
  <div class="favorite-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h2>收藏夹</h2>
          <el-button type="primary" @click="startPractice">收藏题目练习</el-button>
        </div>
      </template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="题目" min-width="300">
          <template #default="{ row }">{{ row.question_content }}</template>
        </el-table-column>
        <el-table-column label="题型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ {single:'单选',multi:'多选',judge:'判断'}[row.question_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="知识点" width="120" prop="knowledge_point" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看</el-button>
            <el-button size="small" type="warning" @click="removeFav(row)">取消收藏</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > 20" :current-page="page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="p => { page = p; loadItems() }" style="margin-top:20px; text-align:center" />
    </el-card>
    <el-dialog v-model="showDetail" title="题目详情" width="600px">
      <div v-if="detailItem">
        <div style="font-size:16px;line-height:1.8;margin-bottom:15px">{{ detailItem.question_content }}</div>
        <div v-for="opt in detailItem.options" :key="opt.label" style="padding:8px 12px;border:1px solid #eee;border-radius:4px;margin-bottom:5px" :style="{ background: detailItem.correct_answer?.includes(opt.label) ? '#f0f9eb' : '' }">
          {{ opt.label }}. {{ opt.content }}
        </div>
        <div style="margin-top:10px;color:#67c23a">正确答案：{{ detailItem.correct_answer }}</div>
        <div v-if="detailItem.explanation" style="margin-top:10px;color:#666">解析：{{ detailItem.explanation }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { favoriteApi, quizApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const showDetail = ref(false)
const detailItem = ref(null)

onMounted(() => loadItems())

async function loadItems() {
  loading.value = true
  try {
    const res = await favoriteApi.getList({ page: page.value, page_size: 20 })
    items.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false }
}

function viewDetail(row) { detailItem.value = row; showDetail.value = true }

async function removeFav(row) {
  try {
    await favoriteApi.remove(row.question_id)
    ElMessage.success('取消收藏')
    loadItems()
  } catch {}
}

async function startPractice() {
  try {
    const res = await favoriteApi.practice([])
    router.push(`/quiz/session/${res.session_id}`)
  } catch (e) { ElMessage.error(e.detail || '没有收藏题目') }
}
</script>

<style scoped>
.favorite-view { max-width: 1200px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h2 { margin: 0; }
</style>
