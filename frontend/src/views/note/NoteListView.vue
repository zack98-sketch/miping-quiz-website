<template>
  <div class="note-list">
    <el-card shadow="never">
      <template #header><h2>我的备注</h2></template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column label="题目" min-width="200">
          <template #default="{ row }">{{ row.question_content }}</template>
        </el-table-column>
        <el-table-column label="备注" min-width="200" prop="content" />
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">{{ row.updated_at?.slice(0, 19).replace('T', ' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteNote(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { noteApi } from '../../api/quiz'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const items = ref([])

onMounted(() => loadItems())

async function loadItems() {
  loading.value = true
  try {
    const res = await noteApi.getList({ page: 1, page_size: 100 })
    items.value = res.items || []
  } finally { loading.value = false }
}

async function deleteNote(row) {
  try {
    await ElMessageBox.confirm('确定删除该备注？', '提示')
    await noteApi.delete(row.id)
    ElMessage.success('删除成功')
    loadItems()
  } catch {}
}
</script>

<style scoped>
.note-list { max-width: 1200px; margin: 0 auto; }
</style>
