# 密评题库答题系统

基于5075道密评题库的在线答题学习平台，支持多种答题模式、AI智能辅导、错题本、收藏、学习分析、在线考试等功能。

## 在线演示

- **访问地址**: http://132.226.89.192
- **默认账号**: admin / admin123

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vite + Element Plus + Pinia + Axios |
| 后端 | Python FastAPI + SQLAlchemy 2.0 + Pydantic + JWT |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| 部署 | Docker + Nginx |
| AI | OpenAI / DeepSeek / 智谱 / 通义千问 / Google Gemini 等 |

## 功能特性

### 核心功能
- 🎯 **多种答题模式**: 随机练习、知识点练习、难度练习、单题模式
- 📝 **在线考试**: 自定义题型数量、计时、自动评分、成绩统计
- 📚 **错题本**: 自动收集、重做练习、掌握状态管理、正确后自动移除
- ⭐ **收藏夹**: 收藏题目、批量练习
- 📊 **学习分析**: 掌握度统计、薄弱项分析、练习建议、进度追踪
- 📜 **答题历史**: 完整记录，支持PDF/Word导出

### AI智能辅导
- 🤖 **多模型支持**: OpenAI、DeepSeek、智谱GLM、通义千问、Google Gemini、Moonshot、百度文心、华为盘古
- 💡 **三级提示**: 轻度提示(知识点方向)、中度提示(解题思路)、深度解析(详细分析)
- 💬 **多轮对话**: 与AI深入讨论题目，追问细节
- ⚙️ **灵活配置**: 管理员可配置API、模型、提示词模板

### 其他功能
- 🔍 **题目搜索**: 模糊搜索题目、答案、解析
- ✏️ **题目备注**: 个人笔记，私有存储
- 📤 **题库管理**: Excel导入、统计概览
- 🔐 **用户系统**: 注册、登录、修改密码

## 快速开始

### 方式一：Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/zack98-sketch/miping-quiz-website.git
cd miping-quiz-website

# 启动服务
docker compose up --build -d

# 访问
# 前端: http://localhost
# 后端API: http://localhost:8000/docs
```

### 方式二：本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npm run dev
```

### 方式三：一键启动

```bash
./start.sh
```

## 题库导入

### 方式一：管理界面导入
1. 登录管理员账号
2. 进入「管理」页面
3. 选择Excel文件上传

### 方式二：命令行导入
```bash
cd backend
python3 -c "
from app.database import init_db, get_db
from app.importers.excel_importer import import_excel
init_db()
db = next(get_db())
import_excel('题库.xlsx', db)
"
```

## 项目结构

```
miping/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── models/          # 数据模型 (14张表)
│   │   │   ├── user.py      # 用户
│   │   │   ├── question.py  # 题目、选项
│   │   │   ├── quiz_session.py  # 答题会话
│   │   │   ├── error_book.py    # 错题本
│   │   │   ├── favorite.py      # 收藏
│   │   │   ├── note.py          # 备注
│   │   │   ├── correction.py    # 纠错
│   │   │   ├── exam.py          # 考试
│   │   │   └── ai_hint.py       # AI提示记录
│   │   ├── schemas/         # Pydantic验证
│   │   ├── routers/         # API路由 (11个模块)
│   │   │   ├── auth.py      # 认证
│   │   │   ├── questions.py # 题库
│   │   │   ├── quiz.py      # 答题
│   │   │   ├── error_book.py
│   │   │   ├── favorites.py
│   │   │   ├── notes.py
│   │   │   ├── analysis.py
│   │   │   ├── exam.py
│   │   │   ├── ai_hint.py   # AI提示
│   │   │   └── admin.py
│   │   └── importers/       # Excel导入
│   ├── data/                # 数据库文件
│   └── requirements.txt
├── frontend/                # Vue3前端
│   └── src/
│       ├── views/           # 页面组件 (13个)
│       │   ├── auth/        # 登录、注册
│       │   ├── quiz/        # 答题首页、答题、结果
│       │   ├── errorbook/   # 错题本
│       │   ├── favorite/    # 收藏夹
│       │   ├── analysis/    # 学习分析、历史
│       │   ├── exam/        # 考试列表、考试
│       │   ├── note/        # 备注
│       │   ├── correction/  # 纠错
│       │   └── admin/       # 管理面板
│       ├── stores/          # Pinia状态管理
│       ├── api/             # API调用
│       └── router/          # 路由配置
├── docs/                    # 文档
│   ├── spec.md              # 需求规格
│   ├── design.md            # 技术设计
│   └── tasks.md             # 编码任务
├── docker-compose.yml
├── nginx.conf
└── start.sh
```

## 题库统计

| 类型 | 数量 |
|------|------|
| 总题数 | 5075 |
| 单选题 | 1747 |
| 多选题 | 1738 |
| 判断题 | 1590 |
| 知识点 | 33个分类 |

## AI配置说明

管理员可在「管理」页面配置AI服务：

1. 选择AI服务商（OpenAI、DeepSeek等）
2. 输入API Key
3. 配置API地址（可选，留空使用默认）
4. 设置模型名称
5. 自定义提示词模板
6. 设置每日使用限制

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |

## 环境变量

```bash
# 后端
DATABASE_URL=sqlite:///./data/quiz.db
JWT_SECRET_KEY=your-secret-key
AI_API_KEY=your-ai-api-key
AI_API_ENDPOINT=https://api.openai.com/v1/chat/completions
```

## License

MIT
