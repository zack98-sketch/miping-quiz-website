# 技术设计文档 - 密评题库答题网站

## 1. 系统架构概述

### 1.1 架构风格

系统采用**前后端分离的B/S架构**，前端为SPA（单页应用），后端为RESTful API服务。整体遵循**分层架构**和**领域驱动设计（DDD）**思想：

- **表现层（Presentation）**：Vue3 SPA + 响应式UI，负责用户交互和页面渲染
- **应用层（Application）**：FastAPI路由和业务编排，负责请求处理和流程控制
- **领域层（Domain）**：核心业务逻辑，包括答题判题、出题策略、学习分析等
- **基础设施层（Infrastructure）**：数据库访问、外部API调用、文件处理等

系统同时遵循**接口隔离原则**，各模块通过明确定义的接口交互，支持独立开发和测试。

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端（浏览器/移动端）                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 答题页面  │  │ 错题本   │  │ 学习分析  │  │ 在线考试  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 收藏夹   │  │ 题目纠错  │  │ 题目备注  │  │ AI提示   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
┌───────────────────────────┼─────────────────────────────────────┐
│                     Nginx（反向代理/静态资源）                     │
│                     :80/:443 → :8000                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                  Gunicorn + FastAPI（应用服务器）                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │ 用户模块 │ │ 题库模块 │ │ 答题模块 │ │ 考试模块 │ │ 分析模块 │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│  │ 纠错模块 │ │ 备注模块 │ │ 收藏模块 │ │ AI模块  │             │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
┌─────────▼──────┐ ┌───────▼───────┐ ┌───────▼───────┐
│ PostgreSQL/     │ │  AI模型服务    │ │  文件存储      │
│ SQLite          │ │  (外部API)    │ │  (导出/上传)   │
└────────────────┘ └───────────────┘ └───────────────┘
```

### 1.3 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 前端框架 | Vue3 + TypeScript | 组合式API适合复杂交互，TypeScript保障类型安全，生态成熟 |
| UI组件库 | Element Plus | Vue3生态最成熟的组件库，支持响应式和国际化 |
| 后端框架 | FastAPI | 异步高性能，自动生成OpenAPI文档，Pydantic类型验证 |
| ORM | SQLAlchemy 2.0 | Python生态最成熟的ORM，支持异步，兼容SQLite和PostgreSQL |
| 认证方案 | JWT（JSON Web Token） | 无状态认证，适合前后端分离架构，支持移动端 |
| 图表库 | ECharts | 功能丰富，支持移动端触摸交互，中文文档完善 |
| 状态管理 | Pinia | Vue3官方推荐，TypeScript支持好，API简洁 |
| 构建工具 | Vite | 开发启动快，HMR高效，Vue3官方推荐 |

## 2. 技术选型

### 2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue3 | 3.4+ | 前端框架，组合式API |
| TypeScript | 5.0+ | 类型安全 |
| Vite | 5.0+ | 构建工具 |
| Pinia | 2.1+ | 状态管理 |
| Vue Router | 4.2+ | 路由管理 |
| Element Plus | 2.4+ | UI组件库 |
| ECharts | 5.4+ | 数据可视化图表 |
| Axios | 1.6+ | HTTP客户端 |
| vue-pdf-embed | 4.0+ | PDF预览 |
| Service Worker | - | 离线缓存（PWA） |

### 2.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 运行时 |
| FastAPI | 0.104+ | Web框架 |
| Uvicorn | 0.24+ | ASGI服务器（开发） |
| Gunicorn | 21.2+ | WSGI服务器（生产，配合uvicorn worker） |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.12+ | 数据库迁移 |
| Pydantic | 2.4+ | 数据验证和序列化 |
| python-jose | 3.3+ | JWT编解码 |
| passlib | 1.7+ | 密码哈希（bcrypt） |
| openpyxl | 3.1+ | Excel文件解析 |
| reportlab | 4.0+ | PDF导出 |
| python-docx | 1.1+ | Word导出 |
| httpx | 0.25+ | 异步HTTP客户端（调用AI API） |
| pytest | 7.4+ | 单元测试 |

### 2.3 数据库选型

| 环境 | 数据库 | 理由 |
|------|--------|------|
| 开发 | SQLite 3 | 零配置，文件级数据库，开发便捷 |
| 生产 | PostgreSQL 15+ | 支持并发、JSON字段、全文搜索，性能稳定 |
| 缓存 | Redis 7+（可选） | 会话缓存、热点数据缓存，提升性能 |

### 2.4 部署技术栈

| 技术 | 用途 |
|------|------|
| Docker | 容器化封装 |
| Docker Compose | 多容器编排 |
| Nginx | 反向代理、静态资源服务、SSL终止 |
| Gunicorn | 应用服务器（多worker进程） |
| GitHub Actions | CI/CD流水线 |
| Let's Encrypt / Certbot | SSL证书自动签发 |

## 3. 组件设计

### 3.1 前端组件

#### 3.1.1 页面组件结构

```
src/
├── views/                    # 页面组件
│   ├── auth/                 # 认证页面
│   │   ├── LoginView.vue
│   │   └── RegisterView.vue
│   ├── quiz/                 # 答题页面
│   │   ├── QuizHomeView.vue      # 答题首页（模式选择）
│   │   ├── QuizSessionView.vue   # 答题会话页面
│   │   └── QuizResultView.vue    # 答题结果页面
│   ├── exam/                 # 在线考试页面
│   │   ├── ExamListView.vue      # 考试列表
│   │   ├── ExamSessionView.vue   # 考试答题页面
│   │   └── ExamResultView.vue    # 考试结果页面
│   ├── errorbook/            # 错题本页面
│   │   ├── ErrorBookView.vue     # 错题本列表
│   │   └── ErrorBookPracticeView.vue  # 错题练习
│   ├── favorite/             # 收藏夹页面
│   │   └── FavoriteView.vue
│   ├── analysis/             # 学习分析页面
│   │   ├── AnalysisView.vue      # 分析总览
│   │   └── HistoryView.vue       # 历史记录
│   ├── correction/           # 题目纠错页面
│   │   ├── MyCorrectionsView.vue # 我的纠错
│   │   └── CorrectionAdminView.vue  # 纠错管理（管理员）
│   ├── note/                 # 题目备注页面
│   │   └── NoteListView.vue      # 备注列表
│   └── admin/                # 管理页面
│       ├── DashboardView.vue     # 管理面板
│       └── QuestionBankView.vue  # 题库管理
├── components/               # 通用组件
│   ├── question/             # 题目相关组件
│   │   ├── QuestionCard.vue      # 题目卡片
│   │   ├── SingleChoice.vue      # 单选题组件
│   │   ├── MultiChoice.vue       # 多选题组件
│   │   ├── JudgeChoice.vue       # 判断题组件
│   │   └── QuestionFilter.vue    # 题目筛选器
│   ├── quiz/                 # 答题相关组件
│   │   ├── AnswerProgress.vue    # 答题进度条
│   │   ├── TimerDisplay.vue      # 计时器
│   │   └── AnswerSummary.vue     # 答题总结
│   ├── chart/                # 图表组件
│   │   ├── AccuracyTrendChart.vue
│   │   └── KnowledgeRadarChart.vue
│   ├── common/               # 公共组件
│   │   ├── AppHeader.vue
│   │   ├── AppFooter.vue
│   │   ├── MobileNav.vue         # 移动端导航
│   │   └── EmptyState.vue
│   ├── note/                 # 备注组件
│   │   └── NoteEditor.vue        # 备注编辑器
│   └── correction/           # 纠错组件
│       └── CorrectionForm.vue    # 纠错表单
├── stores/                   # Pinia状态仓库
│   ├── auth.ts
│   ├── quiz.ts
│   ├── exam.ts
│   ├── errorBook.ts
│   ├── favorite.ts
│   └── analysis.ts
├── composables/              # 组合式函数
│   ├── useResponsive.ts          # 响应式布局
│   ├── useSwipe.ts               # 滑动手势
│   └── useOffline.ts             # 离线缓存
└── api/                      # API调用层
    ├── auth.ts
    ├── quiz.ts
    ├── exam.ts
    ├── question.ts
    ├── errorBook.ts
    ├── favorite.ts
    ├── analysis.ts
    ├── correction.ts
    ├── note.ts
    └── ai.ts
```

#### 3.1.2 响应式设计策略

采用**移动优先（Mobile-First）**的响应式设计：

- **断点定义**：
  - `sm`: 640px（大屏手机）
  - `md`: 768px（平板竖屏）
  - `lg`: 1024px（平板横屏/小桌面）
  - `xl`: 1280px（桌面）

- **布局策略**：
  - 移动端：单列布局，底部导航栏，全屏答题
  - 平板：双列布局，侧边导航
  - 桌面：多列布局，顶部导航，侧边栏信息面板

- **触控优化**：
  - 最小触控区域 44×44px
  - 答题选项间距加大（移动端 12px → 16px）
  - 支持左右滑动手势切换题目

### 3.2 后端组件

#### 3.2.1 模块结构

```
app/
├── main.py                   # FastAPI应用入口
├── config.py                 # 配置管理
├── database.py               # 数据库连接和会话管理
├── dependencies.py           # 依赖注入（认证、权限等）
├── models/                   # SQLAlchemy数据模型
│   ├── user.py
│   ├── question.py
│   ├── quiz_session.py
│   ├── answer_record.py
│   ├── error_book.py
│   ├── favorite.py
│   ├── correction.py
│   ├── note.py
│   ├── exam.py
│   └── ai_hint.py
├── schemas/                  # Pydantic请求/响应模式
│   ├── user.py
│   ├── question.py
│   ├── quiz.py
│   ├── exam.py
│   ├── error_book.py
│   ├── favorite.py
│   ├── correction.py
│   ├── note.py
│   ├── analysis.py
│   └── ai.py
├── routers/                  # API路由
│   ├── auth.py
│   ├── questions.py
│   ├── quiz.py
│   ├── exam.py
│   ├── error_book.py
│   ├── favorites.py
│   ├── corrections.py
│   ├── notes.py
│   ├── analysis.py
│   ├── ai_hint.py
│   └── admin.py
├── services/                 # 业务逻辑服务
│   ├── auth_service.py
│   ├── question_service.py
│   ├── quiz_service.py          # 出题策略 + 判题逻辑
│   ├── exam_service.py
│   ├── error_book_service.py
│   ├── favorite_service.py
│   ├── correction_service.py
│   ├── note_service.py
│   ├── analysis_service.py      # 统计分析 + 导出
│   ├── ai_service.py            # AI提示（策略模式）
│   └── export_service.py        # PDF/Word导出
├── strategies/               # 策略模式（出题策略）
│   ├── base_strategy.py
│   ├── random_strategy.py
│   ├── knowledge_strategy.py
│   ├── difficulty_strategy.py
│   └── mixed_strategy.py
├── importers/                # 题库导入
│   └── excel_importer.py
├── middleware/               # 中间件
│   ├── auth_middleware.py
│   └── rate_limit_middleware.py
└── utils/                    # 工具函数
    ├── security.py              # JWT + 密码哈希
    └── pagination.py            # 分页工具
```

#### 3.2.2 核心服务接口

**出题策略接口（策略模式）**：
```
BaseQuestionStrategy
  ├── generate_questions(pool: QuestionPool, count: int, filters: FilterParams) -> list[Question]
  ├── RandomStrategy: 从全题库随机抽取
  ├── KnowledgeStrategy: 按知识点范围抽取
  ├── DifficultyStrategy: 按难度等级抽取
  └── MixedStrategy: 混合条件抽取
```

**AI提示服务接口（策略模式，支持模型插拔）**：
```
BaseAIHintService
  ├── generate_hint(question: Question, level: HintLevel) -> HintResult
  ├── OpenAIHintService: 基于OpenAI API
  └── CustomHintService: 基于自定义模型API
```

### 3.3 组件交互图

**答题流程交互序列**：

```
用户                前端(Vue3)           后端(FastAPI)         数据库
 │                    │                     │                    │
 │──选择答题模式──→   │                     │                    │
 │                    │──POST /api/quiz──→  │                    │
 │                    │                     │──查询题目池──→     │
 │                    │                     │←──题目列表────     │
 │                    │                     │──策略出题──→       │
 │                    │←──答题会话ID────     │                    │
 │←──展示第一题───   │                     │                    │
 │                    │                     │                    │
 │──提交答案──→       │                     │                    │
 │                    │──POST /api/quiz/    │                    │
 │                    │   {session_id,      │                    │
 │                    │    question_id,     │                    │
 │                    │    answer}──→       │                    │
 │                    │                     │──判题+记录──→      │
 │                    │                     │←──判题结果────     │
 │                    │←──{correct,解析}──   │                    │
 │←──显示结果───     │                     │                    │
```

## 4. 数据模型设计

### 4.1 概念模型

系统核心实体及关系：
- **用户（User）**：1:N → 答题记录、错题本、收藏、备注、纠错
- **题目（Question）**：1:N → 选项（Option）、纠错记录
- **答题会话（QuizSession）**：1:N → 答题记录（AnswerRecord）
- **考试（Exam）**：1:N → 考试参与（ExamParticipation）

### 4.2 逻辑模型

#### User（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 用户ID |
| username | String(50) | UNIQUE, NOT NULL | 用户名 |
| email | String(100) | UNIQUE | 邮箱（可选） |
| password_hash | String(128) | NOT NULL | 加盐哈希密码 |
| role | Enum | NOT NULL, DEFAULT='user' | 角色：admin/user |
| is_active | Boolean | DEFAULT=True | 是否激活 |
| created_at | DateTime | NOT NULL | 创建时间 |
| updated_at | DateTime | NOT NULL | 更新时间 |

#### Question（题目表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 题目ID |
| content | Text | NOT NULL | 题目内容 |
| question_type | Enum | NOT NULL | 题型：single/multi/judge |
| difficulty | Enum | NOT NULL, DEFAULT='medium' | 难度：easy/medium/hard |
| knowledge_point | String(100) | NOT NULL | 知识点标签 |
| correct_answer | String(200) | NOT NULL | 正确答案（JSON格式存选项ID） |
| explanation | Text | | 答案解析 |
| source_id | Integer | | 原始Excel行号（用于溯源） |
| is_active | Boolean | DEFAULT=True | 是否启用 |
| created_at | DateTime | NOT NULL | 创建时间 |
| updated_at | DateTime | NOT NULL | 更新时间 |

#### Option（选项表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 选项ID |
| question_id | Integer | FK→Question.id, NOT NULL | 所属题目 |
| label | String(10) | NOT NULL | 选项标签（A/B/C/D） |
| content | Text | NOT NULL | 选项内容 |
| sort_order | Integer | NOT NULL | 排序序号 |

#### QuizSession（答题会话表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 会话ID |
| user_id | Integer | FK→User.id, NOT NULL | 用户 |
| mode | Enum | NOT NULL | 模式：single/mixed/knowledge/difficulty |
| total_count | Integer | NOT NULL | 总题数 |
| correct_count | Integer | DEFAULT=0 | 正确数 |
| status | Enum | NOT NULL, DEFAULT='in_progress' | 状态：in_progress/completed/abandoned |
| time_spent | Integer | DEFAULT=0 | 总用时（秒） |
| started_at | DateTime | NOT NULL | 开始时间 |
| completed_at | DateTime | | 完成时间 |

#### AnswerRecord（答题记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 记录ID |
| session_id | Integer | FK→QuizSession.id, NOT NULL | 答题会话 |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| user_answer | String(200) | NOT NULL | 用户答案（JSON格式） |
| is_correct | Boolean | NOT NULL | 是否正确 |
| time_spent | Integer | | 本题用时（秒） |
| answered_at | DateTime | NOT NULL | 作答时间 |

#### ErrorBookItem（错题本条目表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 条目ID |
| user_id | Integer | FK→User.id, NOT NULL | 用户 |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| user_answer | String(200) | | 用户错误答案 |
| personal_note | Text | | 个人笔记 |
| mastery_status | Enum | DEFAULT='not_mastered' | 掌握状态：not_mastered/partially/mastered |
| error_count | Integer | DEFAULT=1 | 答错次数 |
| last_error_at | DateTime | NOT NULL | 最近答错时间 |
| created_at | DateTime | NOT NULL | 首次加入时间 |

#### Favorite（收藏表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 收藏ID |
| user_id | Integer | FK→User.id, NOT NULL | 用户 |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| created_at | DateTime | NOT NULL | 收藏时间 |

**UNIQUE约束**: (user_id, question_id)

#### Correction（纠错报告表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 纠错ID |
| user_id | Integer | FK→User.id, NOT NULL | 提交用户 |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| correction_type | Enum | NOT NULL | 类型：content/option/answer/explanation/other |
| description | Text | NOT NULL | 纠错描述 |
| suggestion | Text | | 修正建议 |
| status | Enum | NOT NULL, DEFAULT='pending' | 状态：pending/approved/rejected |
| admin_comment | Text | | 管理员审核意见 |
| reviewed_by | Integer | FK→User.id | 审核管理员 |
| reviewed_at | DateTime | | 审核时间 |
| created_at | DateTime | NOT NULL | 提交时间 |

#### Note（题目备注表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 备注ID |
| user_id | Integer | FK→User.id, NOT NULL | 用户（私有） |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| content | Text | NOT NULL | 备注内容（富文本） |
| created_at | DateTime | NOT NULL | 创建时间 |
| updated_at | DateTime | NOT NULL | 更新时间 |

**UNIQUE约束**: (user_id, question_id)

#### Exam（考试表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 考试ID |
| title | String(200) | NOT NULL | 考试名称 |
| description | Text | | 考试说明 |
| start_time | DateTime | NOT NULL | 开始时间 |
| end_time | DateTime | NOT NULL | 结束时间 |
| time_limit | Integer | NOT NULL | 时间限制（分钟） |
| question_config | JSON | NOT NULL | 题目配置（题型、数量、知识点） |
| created_by | Integer | FK→User.id, NOT NULL | 创建管理员 |
| is_active | Boolean | DEFAULT=True | 是否启用 |
| created_at | DateTime | NOT NULL | 创建时间 |

#### ExamParticipation（考试参与表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 参与ID |
| exam_id | Integer | FK→Exam.id, NOT NULL | 考试 |
| user_id | Integer | FK→User.id, NOT NULL | 用户 |
| score | Float | | 成绩得分 |
| correct_count | Integer | | 正确数 |
| total_count | Integer | | 总题数 |
| time_spent | Integer | | 用时（秒） |
| submitted_at | DateTime | | 交卷时间 |

**UNIQUE约束**: (exam_id, user_id)

#### ExamAnswer（考试答题记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 记录ID |
| participation_id | Integer | FK→ExamParticipation.id, NOT NULL | 考试参与 |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| user_answer | String(200) | | 用户答案 |
| is_correct | Boolean | | 是否正确 |

#### AIHintRecord（AI提示记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 记录ID |
| user_id | Integer | FK→User.id, NOT NULL | 用户 |
| question_id | Integer | FK→Question.id, NOT NULL | 题目 |
| hint_level | Enum | NOT NULL | 级别：light/medium/deep |
| hint_content | Text | NOT NULL | 提示内容 |
| created_at | DateTime | NOT NULL | 请求时间 |

#### SystemConfig（系统配置表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 配置ID |
| key | String(100) | UNIQUE, NOT NULL | 配置键 |
| value | Text | NOT NULL | 配置值 |
| description | String(200) | | 配置说明 |
| updated_at | DateTime | NOT NULL | 更新时间 |

### 4.3 ER图

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│   User   │     │ Question │     │  Option  │
│──────────│     │──────────│     │──────────│
│ id (PK)  │     │ id (PK)  │     │ id (PK)  │
│ username │     │ content  │     │question_id│──FK→Question
│ email    │     │ type     │     │ label    │
│ pass_hash│     │ difficulty│    │ content  │
│ role     │     │ knowledge│     └──────────┘
│ is_active│     │ answer   │
└────┬─────┘     │explanation│
     │           └────┬─────┘
     │                │
     │    ┌───────────┼───────────┐───────────┐───────────┐
     │    │           │           │           │           │
┌────▼────┐ ┌────────▼──┐ ┌─────▼─────┐ ┌───▼───────┐ ┌▼──────────┐
│QuizSession│ │ErrorBook  │ │ Favorite  │ │ Correction│ │   Note    │
│──────────│ │──────────│ │──────────│ │──────────│ │──────────│
│ id (PK)  │ │ id (PK)  │ │ id (PK)  │ │ id (PK)  │ │ id (PK)  │
│ user_id  │ │ user_id  │ │ user_id  │ │ user_id  │ │ user_id  │
│ mode     │ │question_id│ │question_id│ │question_id│ │question_id│
│ status   │ │mastery    │ │           │ │ type     │ │ content  │
└────┬─────┘ └──────────┘ └──────────┘ │ status   │ └──────────┘
     │                                    └──────────┘
┌────▼──────┐
│AnswerRecord│     ┌──────────┐     ┌──────────────┐
│──────────│     │   Exam   │     │ExamParticipation│
│ id (PK)  │     │──────────│     │──────────────│
│session_id│     │ id (PK)  │     │ id (PK)      │
│question_id│    │ title    │     │ exam_id      │──FK→Exam
│ answer   │     │ time_limit│    │ user_id      │──FK→User
│is_correct│     │ config   │     │ score        │
└──────────┘     └────┬─────┘     └──────┬───────┘
                       │                   │
                  ┌────▼──────┐     ┌─────▼──────┐
                  │ (题目通过  │     │ ExamAnswer │
                  │  config   │     │──────────│
                  │  关联)    │     │participation_id│
                  └──────────┘     │question_id │
                                   │is_correct │
                                   └──────────┘

┌──────────────┐     ┌──────────────┐
│ AIHintRecord │     │ SystemConfig │
│──────────────│     │──────────────│
│ id (PK)      │     │ id (PK)      │
│ user_id      │     │ key          │
│ question_id  │     │ value        │
│ hint_level   │     └──────────────┘
│ hint_content │
└──────────────┘
```

## 5. API设计

### 5.1 API概览

| 模块 | 路由前缀 | 说明 |
|------|---------|------|
| 认证 | `/api/auth` | 注册、登录、登出、修改密码 |
| 题库 | `/api/questions` | 题目查询、统计、导入（管理员） |
| 答题 | `/api/quiz` | 创建会话、提交答案、获取结果 |
| 考试 | `/api/exams` | 考试CRUD、参加考试、交卷 |
| 错题本 | `/api/error-book` | 错题CRUD、重做、统计 |
| 收藏 | `/api/favorites` | 收藏/取消、列表、练习 |
| 纠错 | `/api/corrections` | 提交纠错、审核（管理员） |
| 备注 | `/api/notes` | 备注CRUD、列表 |
| 分析 | `/api/analysis` | 掌握度、建议、历史、导出 |
| AI提示 | `/api/ai-hint` | 请求提示、提示记录 |
| 管理 | `/api/admin` | 题库导入、系统配置、统计 |

### 5.2 接口详细设计

#### 5.2.1 认证接口

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/api/auth/register` | 用户注册 | `{username, password, email?}` | `{user, token}` |
| POST | `/api/auth/login` | 用户登录 | `{username, password}` | `{user, token}` |
| POST | `/api/auth/logout` | 用户登出 | - | `{message}` |
| PUT | `/api/auth/password` | 修改密码 | `{old_password, new_password}` | `{message}` |
| GET | `/api/auth/me` | 获取当前用户 | - | `{user}` |

#### 5.2.2 题库接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/questions` | 分页查询题目（支持题型/知识点/难度筛选） | 所有 |
| GET | `/api/questions/{id}` | 获取题目详情（含选项、纠错历史） | 所有 |
| GET | `/api/questions/stats` | 获取题库统计信息 | 所有 |
| GET | `/api/questions/knowledge-points` | 获取所有知识点列表 | 所有 |
| POST | `/api/admin/questions/import` | 上传Excel导入题库 | 管理员 |

#### 5.2.3 答题接口

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/api/quiz/sessions` | 创建答题会话 | `{mode, count, question_types?, knowledge_points?, difficulty?}` |
| GET | `/api/quiz/sessions/{id}` | 获取答题会话详情 | - |
| GET | `/api/quiz/sessions/{id}/current` | 获取当前题目 | - |
| POST | `/api/quiz/sessions/{id}/answer` | 提交答案 | `{question_id, answer}` |
| GET | `/api/quiz/sessions/{id}/result` | 获取答题结果 | - |
| GET | `/api/quiz/sessions/incomplete` | 获取未完成的答题会话 | - |
| PUT | `/api/quiz/sessions/{id}/abandon` | 放弃答题会话 | - |

#### 5.2.4 考试接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/exams` | 创建考试 | 管理员 |
| GET | `/api/exams` | 获取考试列表 | 所有 |
| GET | `/api/exams/{id}` | 获取考试详情 | 所有 |
| POST | `/api/exams/{id}/enter` | 进入考试 | 所有 |
| POST | `/api/exams/{id}/answer` | 提交考试答案 | 所有 |
| POST | `/api/exams/{id}/submit` | 交卷 | 所有 |
| GET | `/api/exams/{id}/result` | 获取考试结果 | 所有 |
| GET | `/api/exams/{id}/statistics` | 获取考试统计 | 管理员 |
| GET | `/api/exams/my-history` | 我的考试历史 | 所有 |

#### 5.2.5 错题本接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/error-book` | 获取错题列表（支持筛选排序分页） |
| PUT | `/api/error-book/{id}` | 编辑错题记录（笔记、掌握状态） |
| DELETE | `/api/error-book/{id}` | 删除错题记录 |
| POST | `/api/error-book/practice` | 错题重做（选定题目或随机抽取） |
| GET | `/api/error-book/stats` | 错题统计（按知识点） |

#### 5.2.6 收藏接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/favorites` | 收藏题目 `{question_id}` |
| DELETE | `/api/favorites/{question_id}` | 取消收藏 |
| GET | `/api/favorites` | 收藏列表（支持筛选排序分页） |
| POST | `/api/favorites/practice` | 收藏题目练习 |

#### 5.2.7 纠错接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/corrections` | 提交纠错报告 | 所有 |
| GET | `/api/corrections/my` | 我的纠错记录 | 所有 |
| GET | `/api/corrections/pending` | 待审核纠错列表 | 管理员 |
| PUT | `/api/corrections/{id}/review` | 审核纠错（通过/驳回） | 管理员 |
| GET | `/api/questions/{id}/corrections` | 题目纠错历史 | 所有 |

#### 5.2.8 备注接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/notes` | 添加/更新备注 `{question_id, content}` |
| DELETE | `/api/notes/{id}` | 删除备注 |
| GET | `/api/notes` | 备注列表（支持筛选排序分页） |
| GET | `/api/notes/question/{question_id}` | 获取某题备注 |

#### 5.2.9 学习分析接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/analysis/mastery` | 知识点掌握度分析 |
| GET | `/api/analysis/weak-points` | 薄弱知识点分析 |
| GET | `/api/analysis/recommendations` | 练习建议 |
| GET | `/api/analysis/progress` | 学习进度 |
| GET | `/api/analysis/history` | 答题历史（支持日期范围筛选） |
| GET | `/api/analysis/trend` | 正确率趋势数据 |
| GET | `/api/analysis/export/pdf` | 导出PDF |
| GET | `/api/analysis/export/word` | 导出Word |

#### 5.2.10 AI提示接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai-hint/request` | 请求AI提示 `{question_id, level}` |
| GET | `/api/ai-hint/usage` | 提示使用统计 |
| GET | `/api/ai-hint/remaining/{question_id}` | 剩余提示次数 |

#### 5.2.11 管理接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/admin/config` | 获取系统配置 | 管理员 |
| PUT | `/api/admin/config` | 更新系统配置 | 管理员 |
| GET | `/api/admin/dashboard` | 管理面板数据 | 管理员 |
| GET | `/api/health` | 健康检查 | 无需认证 |

## 6. 安全设计

### 6.1 认证与授权

- **认证机制**：JWT（HS256算法），access_token有效期2小时，refresh_token有效期24小时
- **密码存储**：bcrypt加盐哈希，cost factor=12
- **权限控制**：基于角色的访问控制（RBAC），两个角色：
  - `admin`：题库管理、纠错审核、考试管理、系统配置
  - `user`：答题、错题本、收藏、备注、纠错提交、AI提示
- **API保护**：所有 `/api/*` 接口（除 `/api/auth/login`、`/api/auth/register`、`/api/health`）需携带有效JWT
- **CORS配置**：生产环境仅允许同源请求，开发环境允许localhost

### 6.2 数据安全

- **SQL注入防护**：SQLAlchemy ORM参数化查询，禁止拼接SQL
- **XSS防护**：前端Vue3模板自动转义，备注富文本使用DOMPurify消毒
- **CSRF防护**：JWT存储于httpOnly cookie或Authorization header，不使用cookie认证
- **敏感数据**：.env文件存储密钥和数据库连接串，.gitignore排除
- **速率限制**：登录接口5次/分钟，AI提示接口10次/分钟，全局100次/分钟
- **输入验证**：Pydantic模型严格验证所有请求参数，限制字符串长度

## 7. 部署架构

### 7.1 容器化设计

**Docker Compose服务编排**：

```
┌─────────────────────────────────────────────┐
│              Docker Compose                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  nginx   │  │  backend │  │    db    │  │
│  │  :80/443 │←→│  :8000   │←→│  :5432   │  │
│  │          │  │ (FastAPI) │  │(PostgreSQL)│ │
│  └──────────┘  └──────────┘  └──────────┘  │
│       │                                      │
│       │  ┌──────────┐                        │
│       └→│ /static  │  (前端构建产物)         │
│         │ /media   │  (上传文件)             │
│         └──────────┘                        │
└─────────────────────────────────────────────┘
```

**Dockerfile设计**：
- **前端**：多阶段构建，node:18-alpine构建 → nginx:alpine服务
- **后端**：python:3.11-slim基础镜像，pip安装依赖，非root用户运行
- **数据库**：postgres:15-alpine，数据卷持久化

### 7.2 网络架构

```
Internet → [Firewall] → Nginx(:443 HTTPS)
                         ├── /api/* → Gunicorn(:8000) → FastAPI
                         ├── /static/* → 前端静态文件
                         └── /media/* → 上传文件目录
```

- Nginx配置：SSL终止、gzip压缩、静态文件缓存（7天）、API代理
- Gunicorn配置：4 worker进程（uvicorn worker class），每worker最大1000连接

### 7.3 CI/CD流程

**GitHub Actions流水线**：

```
代码推送/PR
    │
    ▼
┌──────────────┐
│  Lint检查     │  (ruff + eslint)
└──────┬───────┘
       │
┌──────▼───────┐
│  单元测试     │  (pytest + vitest)
└──────┬───────┘
       │
┌──────▼───────┐
│  构建前端     │  (vite build)
└──────┬───────┘
       │
┌──────▼───────┐
│  构建Docker   │  (docker build)
└──────┬───────┘
       │
   [仅main分支]
       │
┌──────▼───────┐
│  部署到服务器  │  (docker-compose up)
└──────┬───────┘
       │
┌──────▼───────┐
│  健康检查     │  (curl /api/health)
└──────────────┘
```

**分支策略**：
- `main`：生产稳定版本，仅通过PR合并
- `develop`：开发集成分支，日常开发合并目标
- `feature/*`：功能开发分支，从develop创建
- `hotfix/*`：紧急修复分支，从main创建
- `release/*`：发布准备分支，从develop创建

**版本管理**：
- 语义化版本号：MAJOR.MINOR.PATCH
- Git Tag标注每个发布版本
- CHANGELOG.md自动生成（基于commit message convention）
- commit message格式：`type(scope): description`（type: feat/fix/docs/refactor/test）
