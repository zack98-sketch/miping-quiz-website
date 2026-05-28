<template>
  <div class="admin-dashboard">
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="dash-card">
          <template #header><h3>系统概览</h3></template>
          <div class="stat-row"><span>总题数：</span><strong>{{ dashboard.total_questions || 0 }}</strong></div>
          <div class="stat-row"><span>总用户：</span><strong>{{ dashboard.total_users || 0 }}</strong></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="dash-card">
          <template #header><h3>题库导入</h3></template>
          <el-upload :auto-upload="false" :on-change="handleFileChange" accept=".xlsx" :show-file-list="false">
            <el-button type="primary">选择Excel文件</el-button>
          </el-upload>
          <div v-if="importResult" class="import-result">
            <p>总数：{{ importResult.total }}</p>
            <p style="color:#67c23a">成功：{{ importResult.success }}</p>
            <p style="color:#f56c6c">失败：{{ importResult.errors }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI Configuration -->
    <el-card shadow="hover" class="ai-card">
      <template #header>
        <div class="card-header">
          <h3>AI 助手配置</h3>
          <el-button type="primary" size="small" @click="saveAiConfig" :loading="savingConfig">保存配置</el-button>
        </div>
      </template>
      <el-form :model="aiConfig" label-width="120px" class="ai-form">
        <el-form-item label="AI 服务类型">
          <el-select v-model="aiConfig.provider" placeholder="选择AI服务" style="width:100%">
            <el-option label="OpenAI (GPT)" value="openai" />
            <el-option label="华为云盘古" value="pangu" />
            <el-option label="智谱AI (GLM)" value="zhipu" />
            <el-option label="百度文心" value="wenxin" />
            <el-option label="自定义API" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input v-model="aiConfig.api_url" placeholder="https://api.openai.com/v1/chat/completions" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="aiConfig.api_key" type="password" show-password placeholder="输入你的API Key" />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="aiConfig.model_name" placeholder="gpt-3.5-turbo" />
        </el-form-item>
        <el-form-item label="提示词模板">
          <el-input v-model="aiConfig.prompt_template" type="textarea" :rows="4" placeholder="你是一个专业的密码学考试辅导老师，请根据题目内容给出提示..." />
        </el-form-item>
        <el-form-item label="每日提示限制">
          <el-input-number v-model="aiConfig.daily_limit" :min="1" :max="100" />
          <span class="form-hint">次/天</span>
        </el-form-item>
        <el-form-item label="启用AI提示">
          <el-switch v-model="aiConfig.enabled" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const dashboard = ref({})
const importResult = ref(null)
const savingConfig = ref(false)
const aiConfig = ref({
  provider: 'openai',
  api_url: '',
  api_key: '',
  model_name: 'gpt-3.5-turbo',
  prompt_template: '你是一个专业的密码学考试辅导老师，请根据以下题目给出提示（不要直接给出答案）：\n\n题目：{question}\n选项：{options}\n\n请给出{level}级别的提示。',
  daily_limit: 20,
  enabled: false
})

onMounted(async () => {
  try {
    dashboard.value = await adminApi.getDashboard()
  } catch {}
  try {
    const configs = await adminApi.getConfigs()
    const aiConfigs = configs.items || configs || []
    for (const c of aiConfigs) {
      if (c.key && c.key.startsWith('ai_')) {
        const field = c.key.replace('ai_', '')
        if (field === 'enabled') aiConfig.value[field] = c.value === 'true' || c.value === true
        else if (field === 'daily_limit') aiConfig.value[field] = parseInt(c.value) || 20
        else aiConfig.value[field] = c.value
      }
    }
  } catch {}
})

async function handleFileChange(file) {
  try {
    const res = await adminApi.importQuestions(file.raw)
    importResult.value = res
    ElMessage.success(`导入完成：成功${res.success}题`)
    dashboard.value = await adminApi.getDashboard()
  } catch (e) { ElMessage.error('导入失败') }
}

async function saveAiConfig() {
  savingConfig.value = true
  try {
    const configs = [
      { key: 'ai_provider', value: aiConfig.value.provider },
      { key: 'ai_api_url', value: aiConfig.value.api_url },
      { key: 'ai_api_key', value: aiConfig.value.api_key },
      { key: 'ai_model_name', value: aiConfig.value.model_name },
      { key: 'ai_prompt_template', value: aiConfig.value.prompt_template },
      { key: 'ai_daily_limit', value: String(aiConfig.value.daily_limit) },
      { key: 'ai_enabled', value: String(aiConfig.value.enabled) },
    ]
    for (const c of configs) {
      await adminApi.setConfig(c)
    }
    ElMessage.success('AI配置保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingConfig.value = false
  }
}
</script>

<style scoped>
.admin-dashboard { max-width: 1200px; margin: 0 auto; }
.dash-card { margin-bottom: 16px; border-radius: 12px; }
.stat-row { padding: 8px 0; font-size: 15px; }
.import-result { margin-top: 15px; }
.ai-card { margin-top: 16px; border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; }
.ai-form { max-width: 600px; }
.form-hint { margin-left: 8px; color: #999; font-size: 13px; }

@media (max-width: 768px) {
  .ai-form { max-width: 100%; }
}
</style>
