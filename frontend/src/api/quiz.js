import api from './index'

export const questionApi = {
  getQuestions: (params) => api.get('/questions', { params }),
  getQuestion: (id) => api.get(`/questions/${id}`),
  getStats: () => api.get('/questions/stats'),
  getKnowledgePoints: () => api.get('/questions/knowledge-points'),
  search: (keyword) => api.get('/questions/search', { params: { keyword } }),
}

export const quizApi = {
  createSession: (data) => api.post('/quiz/sessions', data),
  getCurrentQuestion: (sessionId) => api.get(`/quiz/sessions/${sessionId}/current`),
  submitAnswer: (sessionId, data) => api.post(`/quiz/sessions/${sessionId}/answer`, data),
  getResult: (sessionId) => api.get(`/quiz/sessions/${sessionId}/result`),
  getIncompleteSessions: () => api.get('/quiz/sessions/incomplete'),
  abandonSession: (sessionId) => api.put(`/quiz/sessions/${sessionId}/abandon`),
}

export const errorBookApi = {
  getItems: (params) => api.get('/error-book', { params }),
  updateItem: (id, data) => api.put(`/error-book/${id}`, data),
  deleteItem: (id) => api.delete(`/error-book/${id}`),
  practice: (data) => api.post('/error-book/practice', data),
  getStats: () => api.get('/error-book/stats'),
}

export const favoriteApi = {
  add: (questionId) => api.post('/favorites', null, { params: { question_id: questionId } }),
  remove: (questionId) => api.delete(`/favorites/${questionId}`),
  getList: (params) => api.get('/favorites', { params }),
  practice: (questionIds) => api.post('/favorites/practice', questionIds),
  check: (questionId) => api.get(`/favorites/check/${questionId}`),
}

export const noteApi = {
  upsert: (questionId, content) => api.post('/notes', null, { params: { question_id: questionId, content } }),
  delete: (id) => api.delete(`/notes/${id}`),
  getList: (params) => api.get('/notes', { params }),
  getByQuestion: (questionId) => api.get(`/notes/question/${questionId}`),
}

export const correctionApi = {
  submit: (data) => api.post('/corrections', data),
  getMy: (params) => api.get('/corrections/my', { params }),
  getPending: (params) => api.get('/corrections/pending', { params }),
  review: (id, data) => api.put(`/corrections/${id}/review`, data),
  getByQuestion: (questionId) => api.get(`/corrections/question/${questionId}`),
}

export const analysisApi = {
  getMastery: () => api.get('/analysis/mastery'),
  getWeakPoints: () => api.get('/analysis/weak-points'),
  getRecommendations: () => api.get('/analysis/recommendations'),
  getProgress: () => api.get('/analysis/progress'),
  getHistory: (params) => api.get('/analysis/history', { params }),
  getTrend: (params) => api.get('/analysis/trend', { params }),
  exportPdf: () => api.get('/analysis/export/pdf', { responseType: 'blob' }),
  exportWord: () => api.get('/analysis/export/word', { responseType: 'blob' }),
}

export const examApi = {
  create: (data) => api.post('/exams', data),
  getList: (params) => api.get('/exams', { params }),
  getExam: (id) => api.get(`/exams/${id}`),
  enter: (id) => api.post(`/exams/${id}/enter`),
  submit: (id, data) => api.post(`/exams/${id}/submit`, data),
  getMyHistory: () => api.get('/exams/my-history'),
}

export const aiHintApi = {
  request: (data) => api.post('/ai-hint/request', data),
  getUsage: () => api.get('/ai-hint/usage'),
  getRemaining: (questionId) => api.get(`/ai-hint/remaining/${questionId}`),
}

export const adminApi = {
  importQuestions: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/admin/questions/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getConfig: () => api.get('/admin/config'),
  getConfigs: () => api.get('/admin/config'),
  updateConfig: (data) => api.put('/admin/config', data),
  setConfig: (data) => api.post('/admin/config', data),
  getDashboard: () => api.get('/admin/dashboard'),
}
