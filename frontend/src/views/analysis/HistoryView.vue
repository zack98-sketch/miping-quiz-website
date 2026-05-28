<template>
  <div class="history-view">
    <el-card shadow="never">
      <template #header><h2>答题历史</h2></template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ row.started_at?.slice(0, 19).replace('T', ' ') }}</template>
        </el-table-column>
        <el-table-column label="模式" width="100">
          <template #default="{ row }">{{ {mixed:'随机',knowledge:'知识点',difficulty:'难度',single:'单题',error_book:'错题重做',favorite:'收藏练习'}[row.mode] || row.mode }}</template>
        </el-table-column>
        <el-table-column label="题数" width="60" prop="total_count" />
        <el-table-column label="正确" width="60" prop="correct_count" />
        <el-table-column label="正确率" width="80">
          <template #default="{ row }"><el-tag :type="row.accuracy >= 80 ? 'success' : row.accuracy >= 60 ? 'warning' : 'danger'" size="small">{{ row.accuracy }}%</el-tag></template>
        </el-table-column>
        <el-table-column label="用时" width="80">
          <template #default="{ row }">{{ Math.floor(row.time_spent / 60) }}分{{ row.time_spent % 60 }}秒</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }"><el-button size="small" @click="$router.push(`/quiz/result/${row.session_id}`)">详情</el-button></template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > 20" :current-page="page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="p => { page = p; loadItems() }" style="margin-top:20px; text-align:center" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { analysisApi } from '../../api/quiz'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)

onMounted(() => loadItems())

async function loadItems() {
  loading.value = true
  try {
    const res = await analysisApi.getHistory({ page: page.value, page_size: 20 })
    items.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false }
}
</script>

<style scoped>
.history-view { max-width: 1200px; margin: 0 auto; }
</style>
