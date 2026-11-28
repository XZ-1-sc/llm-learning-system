# 大模型应用工程化个性化学习系统

面向大模型应用开发初学者的个性化学习系统。当前支持创建和查询学习者画像、获取学情测验题目、提交答卷并查询诊断结果。画像和诊断结果保存在 PostgreSQL 中。

## 本地启动（Windows PowerShell）

需要 Python 3.10 和运行中的 Docker Desktop。以下命令均在项目根目录执行。

1. 创建虚拟环境并安装依赖。已有 `.venv` 时可跳过第一条。

   ```powershell
   python -m venv .venv
   & .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
   ```

2. 如果根目录没有 `.env`，将 `.env.example` 复制为 `.env`，填写自己的 `POSTGRES_PASSWORD`。已有 `.env` 时保留原文件。

3. 启动数据库。

   ```powershell
   docker compose up -d db
   ```

4. 数据库就绪后，依次创建画像表 `learner_profiles` 和诊断结果表 `diagnostic_results`。逐条执行，确认前一条成功再执行下一条。如果某张表已经建好，跳过对应命令。

   ```powershell
   Get-Content -Raw -Encoding UTF8 .\backend\schema.sql | docker compose exec -T db psql -U llm_user -d llm_learning -v ON_ERROR_STOP=1 --single-transaction -f -
   Get-Content -Raw -Encoding UTF8 .\backend\diagnostics_schema.sql | docker compose exec -T db psql -U llm_user -d llm_learning -v ON_ERROR_STOP=1 --single-transaction -f -
   ```

5. 启动后端。

   ```powershell
   & .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
   ```

打开 [健康检查](http://127.0.0.1:8001/health)，预期返回 `{"status":"ok"}`。在 [接口文档](http://127.0.0.1:8001/docs) 中可按以下顺序验证学情诊断流程。

1. 使用 `POST /profiles` 创建画像，记下返回的画像编号。
2. 使用 `GET /diagnostics/questions` 获取题目和选项。
3. 使用 `POST /diagnostics` 提交画像编号 `profile_id` 和答卷，记下返回的诊断编号 `id`。
4. 使用 `GET /diagnostics/{diagnostic_id}` 读取该诊断记录，核对分数和错题编号。
5. 使用 `GET /diagnostics/{diagnostic_id}/recommendations` 查看对应的练习建议。
6. 使用 `GET /diagnostics/{diagnostic_id}/learning-plan` 查看结合每周可用时间安排的练习任务，每项任务的 `resources` 列出了对应的官方资料。
7. 使用 `GET /learning-resources` 查看官方学习资料，或加上 `?topic=python`、`?topic=llm`、`?topic=rag` 按主题筛选。
8. 使用 `GET /learning-resources/search?q=RAG` 搜索资料。用空格分隔多个关键词时，每个词都需要匹配。没有匹配项时返回空列表。
9. 使用 `GET /knowledge/search?q=append` 检索知识片段。结果包含片段编号、正文和官方来源。直接匹配没有结果时，检索器会尝试改写已登记的常见说法，例如将“列表尾部”转换为“列表末尾”。
10. 使用 `POST /rag/context` 预览 RAG 上下文，例如提交 `{"question":"append 会修改原列表吗？","search_query":"append 列表"}`。返回带片段编号的 `context` 和 `citations`，供后续生成使用。找不到片段时返回 `insufficient_evidence`，正文和引用均为空。
11. 配置模型后，把同一个请求提交到 `POST /rag/answer`。它只将问题和检索片段发给模型，返回答案与实际引用的原文链接。证据不足时返回 `insufficient_evidence`。

### 模型配置

在本地 `.env` 中填写 `OPENAI_API_KEY` 和 `OPENAI_MODEL`，再重启后端。`OPENAI_BASE_URL` 默认是 `https://api.openai.com/v1`。使用兼容服务时，选择支持 Chat Completions JSON 模式和 `max_completion_tokens` 的模型，并填写该服务的 API 根地址。密钥保存在本地 `.env`。

`/rag/answer` 找不到片段时不会请求模型。有片段但未配置模型时返回 `503`，模型请求失败或返回了无效引用时返回 `502`。

### 离线检索评测

在项目根目录运行以下命令，无需启动后端、数据库或配置模型密钥。

```powershell
& .\.venv\Scripts\python.exe -X utf8 -m evaluation.evaluate_retrieval
```

样例和人工标注的相关片段编号保存在 `evaluation/retrieval_cases.json`。脚本报告片段召回率、无答案时正确返回空列表的比例，以及结果完全匹配的比例，并列出发生漏检或多返回的用例。这组小样例用于建立检索基线，模型答案的质量需要另行评测。
