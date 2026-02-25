# AI CADQuery - 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品名称
AI CADQuery - 智能参数化 CAD 建模平台

### 1.2 产品定位
面向工程师和创客的 AI 驱动 CAD 建模工具。通过自然语言描述生成工程级 3D 模型，降低 CAD 使用门槛，提高设计效率。

### 1.3 核心价值主张
- **零门槛建模**：无需学习复杂 CAD 软件，用自然语言描述即可生成模型
- **工程级输出**：基于 CADQuery 生成精确参数化模型，支持 STEP/STL 导出
- **快速迭代**：对话式修改，实时预览，参数可调

---

## 2. 目标用户

| 用户类型 | 痛点 | 使用场景 |
|---------|------|---------|
| 机械工程师 | 重复设计简单零件浪费时间 | 快速生成支架、外壳、夹具 |
| 电子工程师 | 不会 CAD，需要外壳设计 | 为 PCB 设计定制外壳 |
| 3D 打印爱好者 | 找不到现成模型 | 按需生成可打印零件 |
| 学生/教育 | CAD 软件学习曲线陡峭 | 快速验证设计想法 |

---

## 3. 功能需求

### 3.1 核心功能

#### 3.1.1 文本生成模型 (MVP 核心)
- 用户输入自然语言描述
- AI 生成 CADQuery Python 代码
- 系统执行代码生成 3D 模型
- 展示预览和可下载文件

**示例交互：**
```
用户：设计一个 M4 螺丝的固定支架，长 50mm，宽 30mm，厚度 5mm，
      中间开 4.5mm 的通孔，四角倒角 2mm

AI：生成 CADQuery 代码 → 渲染 3D → 展示预览
```

#### 3.1.2 参数化调整
- 自动提取关键参数（长度、宽度、孔径等）
- 生成滑块控件实时调整
- 调整后重新生成模型

#### 3.1.3 对话式迭代
- 基于现有模型继续修改
- 支持增量更新
- 历史版本对比

**示例：**
```
用户：把厚度改成 8mm，孔径改成 5mm
AI：更新代码 → 重新渲染 → 展示新模型
```

#### 3.1.4 文件导出
- STEP 格式（用于专业 CAD 软件）
- STL 格式（用于 3D 打印）
- CADQuery Python 源码（可二次开发）

### 3.2 辅助功能

#### 3.2.1 模型库
- 保存历史生成的模型
- 分类标签（支架、外壳、连接件等）
- 公开分享/私密保存

#### 3.2.2 模板市场
- 预设常用模板（Arduino 外壳、Raspberry Pi 支架等）
- 社区共享模板
- 基于模板快速修改

#### 3.2.3 模型预览
- Three.js 3D 查看器
- 旋转、缩放、剖面查看
- 尺寸标注显示

---

## 4. 技术架构

### 4.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Frontend)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   React UI   │  │  Three.js    │  │  Monaco      │       │
│  │   聊天界面    │  │  3D 预览     │  │  代码编辑器   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 网关 (Nginx)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端 (Backend)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   FastAPI    │  │   Celery     │  │   Redis      │       │
│  │   REST API   │  │  任务队列    │  │   缓存       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                          │
│  │  SQLAlchemy  │  │   OpenAI/    │                          │
│  │   SQLite/    │  │   Claude API │                          │
│  │   PostgreSQL │  │   LLM 调用   │                          │
│  └──────────────┘  └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    模型生成服务 (Worker)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   CADQuery   │  │   FreeCAD    │  │   OpenCASCADE│       │
│  │   Python     │  │   后端       │  │   几何内核   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 技术栈

| 层级 | 技术选型 | 说明 |
|-----|---------|------|
| 前端 | React + TypeScript + TailwindCSS | 现代 UI 框架 |
| 3D 渲染 | Three.js + React Three Fiber | WebGL 3D 展示 |
| 后端 | FastAPI (Python) | 高性能异步 API |
| 任务队列 | Celery + Redis | 异步模型生成 |
| 数据库 | SQLite (开发) / PostgreSQL (生产) | 模型存储 |
| CAD 引擎 | CADQuery + FreeCAD | 参数化建模 |
| LLM | OpenAI GPT-4 / Claude | 代码生成 |
| 部署 | Docker + Docker Compose | 一键部署 |

### 4.3 目录结构

```
ai-cadquery/
├── docker-compose.yml          # 一键部署配置
├── Dockerfile                  # 主服务镜像
├── Dockerfile.worker           # 模型生成 worker 镜像
├── nginx.conf                  # 反向代理配置
├──
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── models/            # 数据模型
│   │   ├── routers/           # API 路由
│   │   │   ├── generation.py  # 生成相关 API
│   │   │   ├── models.py      # 模型管理 API
│   │   │   └── templates.py   # 模板 API
│   │   ├── services/          # 业务逻辑
│   │   │   ├── llm.py         # LLM 调用服务
│   │   │   ├── cadquery.py    # CADQuery 执行服务
│   │   │   └── exporter.py    # 文件导出服务
│   │   └── tasks.py           # Celery 异步任务
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # React 组件
│   │   │   ├── Chat/          # 聊天界面
│   │   │   ├── Viewer3D/      # 3D 预览器
│   │   │   ├── ParameterPanel/# 参数面板
│   │   │   └── ModelLibrary/  # 模型库
│   │   ├── services/          # API 调用
│   │   ├── store/             # 状态管理
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── worker/                     # 模型生成 Worker
│   ├── app/
│   │   ├── cadquery_runner.py # CADQuery 执行器
│   │   ├── exporters/         # 导出器
│   │   └── utils.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── shared/                     # 共享资源
    ├── prompts/               # LLM Prompt 模板
    │   ├── system_prompt.txt
    │   └── cadquery_examples/
    └── templates/             # 预设模板
```

---

## 5. API 设计

### 5.1 核心接口

#### POST /api/generate
生成 CAD 模型

```json
{
  "prompt": "设计一个 M4 螺丝的固定支架...",
  "conversation_id": "conv_123",  // 可选，用于连续对话
  "template_id": "temp_456"       // 可选，基于模板
}
```

响应：
```json
{
  "task_id": "task_789",
  "status": "queued",
  "estimated_time": 30
}
```

#### GET /api/tasks/{task_id}
查询任务状态

```json
{
  "task_id": "task_789",
  "status": "completed",  // queued/processing/completed/failed
  "result": {
    "model_id": "model_abc",
    "preview_url": "/api/models/model_abc/preview",
    "parameters": {
      "length": {"value": 50, "min": 10, "max": 100, "unit": "mm"},
      "width": {"value": 30, "min": 10, "max": 80, "unit": "mm"}
    },
    "code": "import cadquery as cq...",
    "downloads": {
      "step": "/api/models/model_abc/download?format=step",
      "stl": "/api/models/model_abc/download?format=stl",
      "python": "/api/models/model_abc/download?format=py"
    }
  }
}
```

#### POST /api/models/{model_id}/regenerate
基于参数重新生成

```json
{
  "parameters": {
    "length": 60,
    "hole_diameter": 5
  }
}
```

---

## 6. LLM Prompt 设计

### 6.1 System Prompt

```
你是一个专业的 CAD 工程师，擅长使用 CADQuery Python 库创建精确的 3D 模型。

你的任务是将用户的自然语言描述转换为可执行的 CADQuery Python 代码。

规则：
1. 只输出有效的 Python 代码，使用 CADQuery 库
2. 代码必须完整可运行，包含所有必要的 import
3. 使用 cq.Workplane() 开始建模
4. 关键尺寸必须参数化（定义为变量）
5. 添加注释说明关键步骤
6. 最后必须返回 result 对象，包含 model 和 parameters

输出格式：
```python
import cadquery as cq

# 参数定义
length = 50  # mm
width = 30   # mm
...

# 建模逻辑
model = cq.Workplane("XY")...

# 返回结果
result = {
    "model": model,
    "parameters": {
        "length": {"value": length, "min": 10, "max": 100, "unit": "mm"},
        ...
    }
}
```

常见 CADQuery 操作：
- 草图：.box(), .circle(), .rect()
- 拉伸：.extrude()
- 切割：.cut(), .cutThruAll()
- 倒角：.edges().chamfer()
- 圆角：.edges().fillet()
- 变换：.translate(), .rotate()
```

### 6.2 示例库

在 `shared/prompts/cadquery_examples/` 中存放常见零件示例：
- bracket_simple.py
- enclosure_box.py
- gear_spur.py
- mounting_plate.py

---

## 7. 部署方案

### 7.1 Docker Compose 配置

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=/api

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=sqlite:///data/app.db
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CELERY_BROKER_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
      - ./shared:/app/shared
    depends_on:
      - redis

  worker:
    build: ./worker
    environment:
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./shared:/app/shared
    depends_on:
      - redis
    # 需要图形库支持
    devices:
      - /dev/dri:/dev/dri

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 7.2 一键部署命令

```bash
# 1. 克隆仓库
git clone https://github.com/yourname/ai-cadquery.git
cd ai-cadquery

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 3. 启动服务
docker-compose up -d

# 4. 访问
open http://localhost
```

---

## 8. 开发计划 (MVP)

### Week 1: 核心功能
- [ ] 后端 API 框架搭建
- [ ] LLM 调用服务
- [ ] CADQuery 执行器
- [ ] 基础前端界面

### Week 2: 功能完善
- [ ] 3D 预览器
- [ ] 参数滑块
- [ ] 文件导出
- [ ] 对话历史

### Week 3: 优化部署
- [ ] Docker 容器化
- [ ] 异步任务队列
- [ ] 性能优化
- [ ] 文档完善

---

## 9. 商业模式

### 9.1 免费版
- 每月 20 次生成
- 基础模型库
- 社区模板

### 9.2 付费版 ($9.9/月)
- 无限生成
- 高级模板
- API 访问
- 优先支持

### 9.3 企业版
- 私有部署
- 定制模型
- SSO 集成
- SLA 保障

---

## 10. 风险评估

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| LLM 生成代码不稳定 | 高 | 增加代码校验、沙箱执行 |
| CADQuery 复杂几何支持有限 | 中 | 逐步增强、引导用户预期 |
| 3D 渲染性能问题 | 中 | 使用 WebGL、模型简化 |
| 竞品追赶 | 低 | 快速迭代、社区建设 |

---

**文档版本**: v1.0  
**创建日期**: 2026-02-25  
**作者**: Leko (PM)
