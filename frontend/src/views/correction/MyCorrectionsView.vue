<template>
  <div class="correction-list">
    <el-card shadow="never">
      <template #header><h2>我的纠错</h2></template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column label="题目ID" width="80" prop="question_id" />
        <el-table-column label="纠错类型" width="100">
          <template #default="{ row }">{{ {content:'内容',option:'选项',answer:'答案',explanation:'解析',other:'其他'}[row.correction_type] }}</template>
        </el-table-column>
        <el-table-column label="描述" min-width="200" prop="description" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="{pending:'warning',approved:'success',rejected:'danger'}[row.status]" size="small">{{ {pending:'待审核',approved:'已通过',rejected:'已驳回'}[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { correctionApi } from '../../api/quiz'

const loading = ref(false)
const items = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const res = await correctionApi.getMy()
    items.value = res.items || []
  } finally { loading.value = false }
})
</script>

<style scoped>
.correction-list { max-width: 1200px; margin: 0 auto; }
</style>
