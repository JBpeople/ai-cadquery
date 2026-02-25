"""
Celery Worker 主程序
"""
import os
import json
from celery import Celery
from app.cadquery_runner import process_task

# Redis 配置
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# 创建 Celery 应用
app = Celery('cadquery_worker', broker=redis_url, backend=redis_url)

@app.task
def generate_model_task(task_data_json: str):
    """Celery 任务：生成 CAD 模型"""
    task_data = json.loads(task_data_json)
    result = process_task(task_data)
    return json.dumps(result)

if __name__ == "__main__":
    # 启动 Worker
    app.worker_main(['-A', 'app.worker', 'worker', '--loglevel=info', '-Q', 'cadquery'])
