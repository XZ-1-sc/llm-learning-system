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
6. 使用 `GET /diagnostics/{diagnostic_id}/learning-plan` 查看结合每周可用时间安排的练习任务。
