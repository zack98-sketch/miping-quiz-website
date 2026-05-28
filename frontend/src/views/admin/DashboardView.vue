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
          <h3>AI 智能辅导配置</h3>
          <el-button type="primary" size="small" @click="saveAiConfig" :loading="savingConfig">保存配置</el-button>
        </div>
      </template>
      
      <el-alert type="info" :closable="false" style="margin-bottom:16px">
        配置AI大模型后，学生可以在答题时获得智能提示和深度解析。支持OpenAI、DeepSeek、智谱、通义千问、Google Gemini等主流大模型。
      </el-alert>

      <el-form :model="aiConfig" label-width="120px" class="ai-form">
        <el-form-item label="启用AI辅导">
          <el-switch v-model="aiConfig.enabled" />
          <span class="form-hint">开启后学生可使用AI提示功能</span>
        </el-form-item>
        
        <el-form-item label="AI 服务商">
          <el-select v-model="aiConfig.provider" placeholder="选择AI服务" style="width:100%" @change="onProviderChange">
            <el-option-group label="国际大模型">
              <el-option label="OpenAI (GPT-3.5/4)" value="openai">
                <span>OpenAI (GPT-3.5/4)</span>
                <el-tag size="small" type="success" style="margin-left:8px">推荐</el-tag>
              </el-option>
              <el-option label="Google Gemini" value="google" />
              <el-option label="DeepSeek" value="deepseek">
                <span>DeepSeek</span>
                <el-tag size="small" type="warning" style="margin-left:8px">性价比高</el-tag>
              </el-option>
            </el-option-group>
            <el-option-group label="国内大模型">
              <el-option label="智谱AI (GLM-4)" value="zhipu" />
              <el-option label="阿里通义千问" value="qwen" />
              <el-option label="Moonshot (Kimi)" value="moonshot" />
              <el-option label="百度文心" value="wenxin" />
              <el-option label="华为云盘古" value="pangu" />
            </el-option-group>
            <el-option-group label="其他">
              <el-option label="自定义API (OpenAI兼容)" value="custom" />
            </el-option-group>
          </el-select>
        </el-form-item>
        
        <el-form-item label="API 地址">
          <el-input v-model="aiConfig.api_url" placeholder="留空则使用默认地址">
            <template #append>
              <el-button @click="resetApiUrl">重置</el-button>
            </template>
          </el-input>
          <div class="form-tip">不同服务商的API地址格式不同，留空使用默认值</div>
        </el-form-item>
        
        <el-form-item label="API Key">
          <el-input v-model="aiConfig.api_key" type="password" show-password placeholder="输入你的API Key">
            <template #prefix><el-icon><Key /></el-icon></template>
          </el-input>
          <div class="form-tip">API Key将加密存储，请妥善保管</div>
        </el-form-item>
        
        <el-form-item label="模型名称">
          <el-input v-model="aiConfig.model_name" placeholder="gpt-3.5-turbo" />
          <div class="form-tip">常用模型：gpt-3.5-turbo, gpt-4, deepseek-chat, glm-4-flash, qwen-turbo</div>
        </el-form-item>
        
        <el-form-item label="提示词模板">
          <el-input v-model="aiConfig.prompt_template" type="textarea" :rows="6" placeholder="自定义AI提示词模板" />
          <div class="form-tip">支持变量：{question}题目, {options}选项, {level}提示级别</div>
        </el-form-item>
        
        <el-form-item label="每日限制">
          <el-input-number v-model="aiConfig.daily_limit" :min="1" :max="200" />
          <span class="form-hint">次/天/用户</span>
        </el-form-item>
        
        <el-form-item label="测试连接">
          <el-button @click="testAiConnection" :loading="testingConnection">测试AI连接</el-button>
          <span v-if="testResult" :style="{color: testResult.success ? '#67c23a' : '#f56c6c', marginLeft: '10px'}">
            {{ testResult.message }}
          </span>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi, aiHintApi } from '../../api/quiz'
import { ElMessage } from 'element-plus'

const dashboard = ref({})
const importResult = ref(null)
const savingConfig = ref(false)
const testingConnection = ref(false)
const testResult = ref(null)

const defaultPrompt = `你是一个专业的密码学考试辅导老师。请根据以下题目给出提示和解析。

【题目】
{question}

【选项】
{options}

【要求】
- 提示级别：{level}
- 请根据提示级别给出相应深度的指导
- 轻度提示：只给出知识点提示和思考方向
- 中度提示：给出解题思路和关键步骤
- 深度提示：详细解析题目，说明每个选项的对错原因
- 注意：不要直接给出答案，要引导学生思考
- 用中文回答，语言简洁专业`

const aiConfig = ref({
  provider: 'openai',
  api_url: '',
  api_key: '',
  model_name: 'gpt-3.5-turbo',
  prompt_template: defaultPrompt,
  daily_limit: 50,
  enabled: false
})

const providerDefaults = {
  openai: { url: 'https://api.openai.com/v1/chat/completions', model: 'gpt-3.5-turbo' },
  deepseek: { url: 'https://api.deepseek.com/v1/chat/completions', model: 'deepseek-chat' },
  zhipu: { url: 'https://open.bigmodel.cn/api/paas/v4/chat/completions', model: 'glm-4-flash' },
  qwen: { url: 'https://dashscope.aliyuncs.com/api/v1/chat/completions', model: 'qwen-turbo' },
  google: { url: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent', model: 'gemini-pro' },
  moonshot: { url: 'https://api.moonshot.cn/v1/chat/completions', model: 'moonshot-v1-8k' },
  pangu: { url: 'https://pangu-api.cn-north-4.myhuaweicloud.com/v1/chat/completions', model: 'pangu-n2' },
  wenxin: { url: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxin/chat/completions', model: 'ernie-bot-turbo' },
  custom: { url: '', model: '' },
}

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
        else if (field === 'daily_limit') aiConfig.value[field] = parseInt(c.value) || 50
        else aiConfig.value[field] = c.value
      }
    }
  } catch {}
})

function onProviderChange(provider) {
  const defaults = providerDefaults[provider]
  if (defaults) {
    if (!aiConfig.value.api_url) {
      aiConfig.value.api_url = defaults.url
    }
    if (!aiConfig.value.model_name || aiConfig.value.model_name === 'gpt-3.5-turbo') {
      aiConfig.value.model_name = defaults.model
    }
  }
}

function resetApiUrl() {
  const defaults = providerDefaults[aiConfig.value.provider]
  aiConfig.value.api_url = defaults?.url || ''
}

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

async function testAiConnection() {
  if (!aiConfig.value.api_key) {
    ElMessage.warning('请先输入API Key')
    return
  }
  testingConnection.value = true
  testResult.value = null
  try {
    // Save config first
    await saveAiConfig()
    // Test with a simple message
    const res = await aiHintApi.chat({
      messages: [{ role: 'user', content: '你好，请回复"连接成功"' }]
    })
    if (res.content && res.content.includes('成功')) {
      testResult.value = { success: true, message: '连接成功！AI响应：' + res.content.slice(0, 50) }
    } else {
      testResult.value = { success: true, message: '连接成功！' }
    }
  } catch (e) {
    testResult.value = { success: false, message: e.detail || '连接失败' }
  } finally {
    testingConnection.value = false
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
.ai-form { max-width: 700px; }
.form-hint { margin-left: 8px; color: #999; font-size: 13px; }
.form-tip { font-size: 12px; color: #999; margin-top: 4px; line-height: 1.4; }

@media (max-width: 768px) {
  .ai-form { max-width: 100%; }
}
</style>
