# AI Vision Web 后端

FastAPI + SQLite 后端，为前端提供用户认证、图片上传、AI 图像分析、历史记录和模型配置接口。

## 技术栈

- Python 3.10+
- FastAPI
- SQLite
- SQLAlchemy
- JWT Bearer Token

## 本地启动

进入项目目录：

```powershell
cd PROJECT/backend
```

创建虚拟环境并安装依赖：

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

复制环境变量文件：

```powershell
copy .env.example .env
```

启动服务：

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务地址：`http://127.0.0.1:8000`

Swagger 文档：`http://127.0.0.1:8000/docs`

## 环境变量

`.env.example` 中提供了示例配置：

```env
JWT_SECRET=replace-with-a-random-secret
DEFAULT_AI_BASE_URL=https://your-provider.example/v1
DEFAULT_AI_API_KEY=your-api-key
DEFAULT_AI_MODEL=your-vision-model
```

说明：

- `JWT_SECRET`：JWT 签名密钥，部署时必须替换。
- `DEFAULT_AI_BASE_URL`：默认 AI 服务地址，可不填。
- `DEFAULT_AI_API_KEY`：默认 AI API Key，可不填。
- `DEFAULT_AI_MODEL`：默认视觉模型名，可不填。

如果默认 AI 配置为空，用户也可以登录后通过 `/api/ai-configs` 保存自己的模型配置。

## 前端联调约定

前端请求基地址：

```js
const API_BASE = 'http://127.0.0.1:8000'
```

除登录接口外，受保护接口都需要请求头：

```http
Authorization: Bearer <access_token>
```

上传图片接口返回的 `url` 是相对路径，展示图片时需要拼接：

```js
const imageUrl = `${API_BASE}${image.url}`
```

后端已开启 CORS，前端本地开发可以直接跨域请求。

## 接口概览

详细请求体和响应示例见 [API.md](API.md)。

### 认证

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录，表单提交 |
| GET | `/api/auth/me` | 获取当前用户 |

登录接口使用 `application/x-www-form-urlencoded`，不是 JSON：

```js
const body = new URLSearchParams({ username, password })
const res = await fetch(`${API_BASE}/api/auth/login`, {
  method: 'POST',
  body,
})
const { access_token } = await res.json()
```

### 图片

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/images` | 上传图片，字段名 `file` |
| GET | `/api/images` | 图片列表 |
| GET | `/api/images/{image_id}` | 图片详情 |
| DELETE | `/api/images/{image_id}` | 删除图片 |

支持 JPG、PNG、GIF、WEBP，最大 10MB。

### AI 配置

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/ai-configs` | 新建模型配置 |
| GET | `/api/ai-configs` | 配置列表 |
| GET | `/api/ai-configs/{config_id}` | 配置详情 |
| PUT | `/api/ai-configs/{config_id}` | 更新配置 |
| DELETE | `/api/ai-configs/{config_id}` | 删除配置 |

`api_key` 只写入，不会在查询响应中返回。

### 图像分析

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/analysis` | 发起 AI 分析 |
| GET | `/api/analysis` | 分析历史 |
| GET | `/api/analysis/{analysis_id}` | 分析详情 |
| PUT | `/api/analysis/{analysis_id}` | 更新分析结果 |
| DELETE | `/api/analysis/{analysis_id}` | 删除分析记录 |

发起分析示例：

```json
{
  "image_id": 1,
  "analysis_type": "all",
  "ai_config_id": 1
}
```

`analysis_type` 可选值：`all`、`describe`、`tags`、`scene`、`prompt`。

## 测试

安装开发依赖后运行：

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest tests -q
```

测试不会调用外部 AI 模型，也不会消耗 API Key。

## 不要提交的文件

以下内容已在 `.gitignore` 中忽略：

- `.env`
- `venv/`
- `.pytest_cache/`
- `data/*.db`
- `data/uploads/`
- `*.log`
