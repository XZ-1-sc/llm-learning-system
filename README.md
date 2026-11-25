# 大模型应用工程化个性化学习系统

面向大模型应用开发初学者的个性化学习系统。当前已实现学习者画像的创建与按编号查询，数据保存在 PostgreSQL 中。

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

4. 数据库就绪后，为新数据库创建画像表。已有 `learner_profiles` 表时跳过此步。

   ```powershell
   Get-Content -Raw -Encoding UTF8 .\backend\schema.sql | docker compose exec -T db psql -U llm_user -d llm_learning -v ON_ERROR_STOP=1
   ```

5. 启动后端。

   ```powershell
   & .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
   ```

打开 [健康检查](http://127.0.0.1:8001/health)，预期返回 `{"status":"ok"}`。通过 [接口文档](http://127.0.0.1:8001/docs) 可以测试 `POST /profiles` 和 `GET /profiles/{profile_id}`。