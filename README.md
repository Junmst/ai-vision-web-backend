# AI Vision Web 智能图片分析平台

## 一、项目简介

`AI Vision Web` 是一个基于 Web 的全栈图片分析系统。用户可以在浏览器中完成注册、登录、上传图片、查看图片列表、调用 AI 模型进行图片分析、查看分析历史，以及配置自己的 AI 接口。

本项目的核心特色是在传统图片管理功能的基础上，接入了 OpenAI 兼容接口，使系统能够对上传图片进行智能描述、标签提取、场景识别和 Prompt 反推，形成一个完整可运行、可部署、可演示的 Web 应用。

系统整体采用前后端分离架构：

- **前端**：Vue 3 + Vite
- **后端**：FastAPI + SQLAlchemy
- **数据库**：SQLite
- **部署**：Nginx + Uvicorn

---

## 二、项目目录结构

```text
PROJECT/
├── frontend/                  # 前端项目（Vue 3 + Vite）
├── backend/                   # 后端项目（FastAPI + SQLite）
├── README.md                  # 项目总说明（本文件）
├── 后端架构说明.md            # 后端答辩说明
└── 课程设计说明书_报告正文.md  # 课程设计说明书正文草稿
```

---

## 三、主要功能

本系统实现了以下核心功能：

1. **用户注册与登录**
   - 支持新用户注册
   - 支持账号密码登录
   - 使用 JWT 进行身份认证

2. **图片上传与管理**
   - 支持上传 JPG / PNG / GIF / WEBP 图片
   - 支持查看图片列表和图片详情
   - 支持删除图片

3. **AI 图片分析**
   - 支持图片描述
   - 支持关键词标签提取
   - 支持场景识别
   - 支持 Prompt 反推
   - 支持综合分析

4. **AI 配置管理**
   - 支持用户配置自己的 AI 平台地址
   - 支持配置 API Key、模型名称
   - 支持 Bearer Token 与 API-Key 两种鉴权模式

5. **分析记录管理**
   - 支持保存每次分析的结果
   - 支持查看历史分析记录

---

## 四、小组成员及分工

> 说明：本节为占位内容，提交前必须替换为真实小组成员、学号和分工信息。

| 成员 | 学号 | 分工 |
|------|------|------|
| 待填写成员1 | 待填写 | 前端页面设计、交互实现、前后端联调 |
| 待填写成员2 | 待填写 | 后端接口开发、数据库设计、部署与测试 |

如果老师要求更细粒度分工，也可补充：


- 需求分析与选题：两人共同完成
- 系统设计与技术选型：两人共同完成
- 文档撰写与答辩准备：两人共同完成

---

## 五、环境要求

### 1. 前端环境

- Node.js **18+**（推荐 Node.js 20）
- npm **9+**

### 2. 后端环境

- Python **3.10+**
- pip
- Windows / Linux / macOS 均可运行

### 3. 可选部署环境

- Nginx
- Linux 服务器（用于生产部署）

---

## 六、依赖安装

### 1. 前端依赖安装

进入前端目录：

```powershell
cd PROJECT/frontend
```

安装依赖：

```powershell
npm install
```

### 2. 后端依赖安装

进入后端目录：

```powershell
cd PROJECT/backend
```

创建虚拟环境：

```powershell
python -m venv venv
```

安装依赖：

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 七、启动命令

### 1. 启动后端

进入后端目录：

```powershell
cd PROJECT/backend
```

复制环境变量模板：

```powershell
copy .env.example .env
```

启动 FastAPI 服务：

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：

- 后端接口地址：`http://127.0.0.1:8000`
- Swagger 文档地址：`http://127.0.0.1:8000/docs`

### 2. 启动前端

进入前端目录：

```powershell
cd PROJECT/frontend
```

启动开发服务器：

```powershell
npm run dev
```

启动后访问前端页面（以终端输出为准，通常为）：

- `http://127.0.0.1:5173`

---

## 八、环境变量说明

后端 `.env.example` 中提供了示例配置，常用字段如下：

```env
JWT_SECRET=replace-with-a-random-secret
DEFAULT_AI_BASE_URL=https://your-provider.example/v1
DEFAULT_AI_API_KEY=your-api-key
DEFAULT_AI_MODEL=your-vision-model
```

说明：

- `JWT_SECRET`：JWT 签名密钥，部署时建议修改
- `DEFAULT_AI_BASE_URL`：默认 AI 平台地址
- `DEFAULT_AI_API_KEY`：默认 AI Key
- `DEFAULT_AI_MODEL`：默认模型名

如果默认 AI 配置留空，用户也可以在系统登录后通过“AI 配置”页面自行填写自己的接口信息。

---

## 九、数据库与文件说明

本项目使用 SQLite 作为数据库，数据库文件默认位于：

```text
PROJECT/backend/data/app.db
```

上传图片默认保存在：

```text
PROJECT/backend/data/uploads/
```

说明：

- 图片文件本地落盘保存
- 图片元信息、用户信息、分析记录、AI 配置保存在 SQLite 中

---

## 十、测试与演示建议

建议按以下顺序进行项目演示：

1. 打开前端首页
2. 注册新用户
3. 登录系统
4. 上传一张本地图片
5. 查看图片列表
6. 进入 AI 配置页面填写 API 配置
7. 返回首页点击“分析”按钮
8. 展示分析结果与历史记录

这样可以完整体现本项目的前端、后端、数据库和 AI 集成能力。

---

## 十一、项目说明

- 本项目为 Web 应用综合设计课程项目
- 项目源码包含前端与后端完整实现
- 支持本地运行与服务器部署
- 已根据课程任务要求补充报告与答辩说明文档

---

## 十二、补充说明

### 1. 不建议提交的内容

提交仓库时建议忽略以下内容：

- `.env`
- `venv/`
- `.pytest_cache/`
- `data/uploads/`
- `data/*.db`
- 前端 `node_modules/`
- 各类日志文件

### 2. 课程答辩重点

本项目答辩时建议重点说明：

- 前后端分离架构
- 用户认证流程（JWT）
- 图片上传流程
- AI 调用流程
- 用户自定义 API 配置机制
- 数据库设计与多用户数据隔离

---

## 十三、相关文档

项目中还包含以下文档：

- `后端架构说明.md`：详细后端架构和接口流程说明
- `课程设计说明书_报告正文.md`：课程设计说明书正文

