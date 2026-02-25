# AI CADQuery 🤖🎨

用自然语言设计 3D 模型，生成工程级 CAD 文件。

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com)
[![CADQuery](https://img.shields.io/badge/CADQuery-2.7-orange)](https://cadquery.readthedocs.io)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org)

## 项目介绍

AI CADQuery 是一个 AI 驱动的参数化 CAD 建模平台。用户只需用自然语言描述想要的零件，系统就能自动生成可编辑的 3D 模型，并导出为 STL（3D 打印）或 Python 源码格式。

### 核心功能

- 📝 **自然语言建模** - 用中文或英文描述零件，AI 自动生成 CAD 代码
- 🔧 **参数化设计** - 实时调整尺寸参数，即时预览效果
- 🔍 **3D 预览** - 基于 Three.js 的在线 3D 查看器
- 💾 **多格式导出** - 支持 STL（3D 打印）、STEP（专业 CAD）、Python 源码
- 🐳 **一键部署** - Docker Compose 快速启动

## 技术栈

| 层级 | 技术 |
|-----|------|
| 前端 | React + TypeScript + TailwindCSS + Three.js |
| 后端 | FastAPI + Python 3.11 |
| CAD 引擎 | CADQuery 2.7 (基于 OpenCASCADE) |
| AI 模型 | OpenAI GPT-4 / Claude / 自定义 LLM |
| 部署 | Docker + Docker Compose |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker (可选)

### 本地开发

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/ai-cadquery.git
cd ai-cadquery
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key
```

3. **启动后端**
```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

4. **启动前端**
```bash
cd frontend
npm install
npm start
```

5. **访问应用**
打开浏览器访问 http://localhost:3000

### Docker 部署

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 一键启动
docker-compose up -d

# 访问 http://localhost
```

## 使用示例

### 示例 1：螺丝支架
```
设计一个 M4 螺丝的固定支架，长 50mm，宽 30mm，
厚度 5mm，中间开 4.5mm 的通孔，四角倒角 2mm
```

### 示例 2：电子外壳
```
设计一个 Arduino Uno 的外壳，长 70mm，宽 55mm，
高度 30mm，壁厚 2mm，顶部开口
```

### 示例 3：机械零件
```
设计一个齿轮，模数 1，齿数 20，厚度 10mm，
中心孔直径 8mm
```

## 项目结构

```
ai-cadquery/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py      # API 入口
│   │   └── ...
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React 前端
│   ├── src/
│   ├── public/
│   └── Dockerfile
├── worker/               # CADQuery 执行器 (可选)
├── docker-compose.yml    # Docker 部署配置
├── nginx.conf           # 反向代理配置
└── README.md
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看自动生成的 API 文档。

### 主要接口

- `POST /api/generate` - 提交生成任务
- `GET /api/tasks/{task_id}` - 查询任务状态
- `GET /api/models/{model_id}/download?format=stl` - 下载 STL 文件

## 配置说明

### LLM 配置

支持 OpenAI、Claude 或兼容 OpenAI API 的自定义模型：

```env
# OpenAI
OPENAI_API_KEY=sk-xxx

# 或自定义 API
LLM_API_URL=https://your-api.com/v1
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4
```

## 开发计划

- [x] 基础文本生成 CAD 代码
- [x] 3D 预览 (STL 加载)
- [x] 参数化调整
- [ ] 对话式迭代修改
- [ ] 模型库/历史记录
- [ ] 用户认证
- [ ] 云端部署

## 许可证

MIT License

## 致谢

- [CADQuery](https://cadquery.readthedocs.io/) - 强大的参数化 CAD 库
- [Three.js](https://threejs.org/) - WebGL 3D 渲染
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
