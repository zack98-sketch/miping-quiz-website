<template>
  <div class="analysis-view">
    <!-- Progress Overview -->
    <el-row :gutter="20" class="progress-row">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number">{{ progress.total_questions || 0 }}</div>
          <div class="stat-label">累计答题</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number" style="color:#67c23a">{{ progress.overall_accuracy || 0 }}%</div>
          <div class="stat-label">总正确率</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number" style="color:#f56c6c">{{ progress.total_errors || 0 }}</div>
          <div class="stat-label">累计错题</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-number" style="color:#409eff">{{ progress.study_days || 0 }}</div>
          <div class="stat-label">学习天数</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Mastery Analysis -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never" class="analysis-card">
          <template #header><h3>知识点掌握度</h3></template>
          <div v-if="masteryItems.length === 0" class="empty">暂无数据，开始答题后即可查看</div>
          <div v-for="item in masteryItems" :key="item.knowledge_point" class="mastery-item">
            <div class="mastery-label">{{ item.knowledge_point }}</div>
            <el-progress :percentage="item.mastery_rate" :color="getMasteryColor(item.mastery_rate)" :stroke-width="16" />
            <span class="mastery-text">{{ item.mastery_rate }}%</span>
          </div>
        </el-card>
      </el-col>

      <!-- Weak Points -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never" class="analysis-card">
          <template #header><h3>薄弱知识点</h3></template>
          <div v-if="weakPoints.length === 0" class="empty">暂无薄弱知识点</div>
          <div v-for="item in weakPoints" :key="item.knowledge_point" class="weak-item">
            <el-tag type="danger" size="small">{{ item.knowledge_point }}</el-tag>
            <span>掌握率 {{ item.mastery_rate }}%，共 {{ item.total_count }} 题</span>
          </div>
        </el-card>

        <!-- Recommendations -->
        <el-card shadow="never" class="analysis-card" style="margin-top:20px">
          <template #header><h3>练习建议</h3></template>
          <div v-if="recommendations.length === 0" class="empty">暂无建议</div>
          <div v-for="item in recommendations" :key="item.knowledge_point" class="rec-item">
            <el-tag type="warning" size="small">{{ item.knowledge_point }}</el-tag>
            <span>{{ item.reason }}（{{ item.question_count }} 题可练）</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Actions -->
    <div class="action-area">
      <el-button @click="$router.push('/history')">查看答题历史</el-button>
      <el-button @click="exportPdf">导出 PDF</el-button>
      <el-button @click="exportWord">导出 Word</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { analysisApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const progress = ref({})
const masteryItems = ref([])
const weakPoints = ref([])
const recommendations = ref([])

onMounted(async () => {
  try {
    const [p, m, w, r] = await Promise.all([
      analysisApi.getProgress(),
      analysisApi.getMastery(),
      analysisApi.getWeakPoints(),
      analysisApi.getRecommendations(),
    ])
    progress.value = p
    masteryItems.value = m.items || []
    weakPoints.value = w.items || []
    recommendations.value = r.items || []
  } catch {}
})

function getMasteryColor(rate) {
  if (rate >= 80) return '#67c23a'
  if (rate >= 60) return '#e6a23c'
  return '#f56c6c'
}

async function exportPdf() {
  try {
    const res = await analysisApi.exportPdf()
    const url = URL.createObjectURL(res)
    const a = document.createElement('a')
    a.href = url; a.download = 'answer_records.pdf'; a.click()
  } catch { ElMessage.error('导出失败') }
}

async function exportWord() {
  try {
    const res = await analysisApi.exportWord()
    const url = URL.createObjectURL(res)
    const a = document.createElement('a')
    a.href = url; a.download = 'answer_records.docx'; a.click()
  } catch { ElMessage.error('导出失败') }
}
</script>

<style scoped>
.analysis-view { max-width: 1200px; margin: 0 auto; }
.progress-row { margin-bottom: 20px; }
.stat-card { text-align: center; padding: 10px; }
.stat-number { font-size: 28px; font-weight: bold; color: #e94560; }
.stat-label { font-size: 13px; color: #999; margin-top: 5px; }
.analysis-card { margin-bottom: 20px; }
.analysis-card h3 { margin: 0; }
.empty { text-align: center; color: #999; padding: 20px; }
.mastery-item { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.mastery-label { width: 100px; font-size: 13px; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mastery-item .el-progress { flex: 1; }
.mastery-text { width: 50px; font-size: 13px; text-align: right; }
.weak-item, .rec-item { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px; }
.action-area { text-align: center; margin-top: 20px; }
</style>
