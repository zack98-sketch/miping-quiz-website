# 密评题库答题网站

基于5075道密评题库的在线答题学习平台，支持多种答题模式、错题本、收藏、学习分析、在线考试等功能。

## 技术栈

- **前端**: Vue3 + Vite + Element Plus + Pinia + Axios
- **后端**: Python FastAPI + SQLAlchemy + Pydantic + JWT
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **部署**: Docker + Nginx + Gunicorn

## 功能特性

- 随机出题 / 题型筛选 / 知识点筛选 / 难度筛选
- 四种答题模式：随机、知识点、难度、单题
- 实时判题，错题自动收集
- 错题本：查看、编辑、删除、重做、掌握状态
- 收藏夹：收藏题目、收藏练习
- 学习分析：掌握度、薄弱项、练习建议、进度追踪
- 答题历史：完整记录，支持PDF/Word导出
- 在线考试：创建考试、计时、交卷、成绩统计
- AI智能提示：三级提示，次数限制
- 题目纠错：提交纠错、管理员审核
- 题目备注：个人笔记，私有
- 管理面板：题库统计、Excel导入

## 快速开始

### 方式一：一键启动

```bash
cd /path/to/miping
./start.sh
```

### 方式二：分别启动

```bash
# 后端
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npx vite --host 0.0.0.0 --port 5173
```

### 方式三：Docker

```bash
docker-compose up --build
```

## 题库导入

```bash
cd backend
python3 import_cli.py /path/to/题库.xlsx
```

## 访问地址

- 前端页面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 默认管理员: admin / admin123

## 项目结构

```
miping/
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── models/   # 数据模型(14张表)
│   │   ├── schemas/  # Pydantic验证
│   │   ├── routers/  # API路由(11个模块)
│   │   └── importers/# Excel导入
│   └── data/         # 数据库文件
├── frontend/         # Vue3前端
│   └── src/
│       ├── views/    # 页面组件(13个)
│       ├── stores/   # Pinia状态
│       └── api/      # API调用
├── docker-compose.yml
├── nginx.conf
└── start.sh
```

## 题库统计

- 总题数: 5075
- 单选题: 1747 | 多选题: 1738 | 判断题: 1590
- 知识点: 33个分类

## License

MIT
