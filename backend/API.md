# 前端接口说明

本地开发基地址：`http://127.0.0.1:8000`。所有 JSON 请求使用 `Content-Type: application/json`；受保护接口加 `Authorization: Bearer <access_token>`。后端已启用 CORS。

## 通用约定

- 成功：`200`。
- 参数校验失败：`422`，错误在 `detail` 数组中。
- 业务失败：`400` / `401` / `404`，错误格式为 `{"detail":"错误说明"}`。
- 日期字段为 ISO 8601 字符串。
- 图片 `url` 是相对路径，页面展示时拼成 `${API_BASE}${image.url}`。

## 认证

### 注册

`POST /api/auth/register`

```json
{"username":"alice","password":"password123"}
```

响应：

```json
{"id":1,"username":"alice","created_at":"2026-07-11T14:00:00"}
```

用户名 3-64 字符，密码 6-128 字符。

### 登录

`POST /api/auth/login`

此接口是表单，不是 JSON：

```js
const body = new URLSearchParams({ username, password })
fetch(`${API_BASE}/api/auth/login`, { method: 'POST', body })
```

响应：

```json
{"access_token":"eyJ...","token_type":"bearer"}
```

保存 `access_token`，后续请求放在 `Authorization: Bearer ...`。

### 当前用户

`GET /api/auth/me`

响应与注册响应相同。

## 图片

### 上传图片

`POST /api/images`，`multipart/form-data`，字段名必须为 `file`。支持 JPG、PNG、GIF、WEBP，最大 10MB。

```js
const form = new FormData()
form.append('file', selectedFile)
fetch(`${API_BASE}/api/images`, {
  method: 'POST', headers: authHeaders, body: form
})
```

响应：

```json
{"id":1,"user_id":1,"filename":"cat.png","file_size":182894,"url":"/uploads/uuid.png","created_at":"2026-07-11T14:00:00"}
```

### 图片列表 / 单项 / 删除

- `GET /api/images`
- `GET /api/images/{image_id}`
- `DELETE /api/images/{image_id}`，响应 `{"message":"删除成功"}`

## AI 配置

每个用户可保存多个模型配置；当 `is_default` 为 `1` 时，会自动取消该用户其他配置的默认状态。`api_key` 只可写、永不返回。

### 新建

`POST /api/ai-configs`

```json
{"config_name":"我的视觉模型","provider":"cloud","base_url":"https://provider.example/v1","api_key":"sk-...","model_name":"vision-model","is_default":1}
```

### 查询 / 更新 / 删除

- `GET /api/ai-configs`
- `GET /api/ai-configs/{config_id}`
- `PUT /api/ai-configs/{config_id}`，仅传要修改的字段；更新 Key 时使用 `api_key`
- `DELETE /api/ai-configs/{config_id}`，响应 `{"message":"删除成功"}`

配置响应不含 API Key：

```json
{"id":1,"user_id":1,"config_name":"我的视觉模型","provider":"cloud","base_url":"https://provider.example/v1","model_name":"vision-model","is_default":1,"created_at":"2026-07-11T14:00:00"}
```

## 图像分析

### 发起分析

`POST /api/analysis`

```json
{"image_id":1,"analysis_type":"all","ai_config_id":1}
```

`ai_config_id` 可省略，省略后使用当前用户默认配置；两者都没有时使用服务器 `.env` 的默认模型。可用 `analysis_type`：`all`、`describe`、`tags`、`scene`、`prompt`。

响应：

```json
{"id":1,"user_id":1,"image_id":1,"provider":"cloud","model_name":"vision-model","analysis_type":"all","result_json":"{\"description\":\"...\",\"tags\":[\"...\"],\"scene\":\"...\",\"prompt\":\"...\"}","latency":3.21,"created_at":"2026-07-11T14:00:00"}
```

前端应使用 `JSON.parse(result_json)` 后展示四项字段。AI 服务未配置时为 `400`；模型请求失败时为 `500`。

### 分析历史与管理

- `GET /api/analysis`
- `GET /api/analysis/{analysis_id}`
- `PUT /api/analysis/{analysis_id}`，请求体 `{"result_json":"..."}`
- `DELETE /api/analysis/{analysis_id}`，响应 `{"message":"删除成功"}`
