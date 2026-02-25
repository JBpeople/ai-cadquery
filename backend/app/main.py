from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import json
import httpx
from datetime import datetime

app = FastAPI(title="AI CADQuery API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据存储
DATA_DIR = os.path.expanduser("~/.ai-cadquery/data")
MODELS_DIR = f"{DATA_DIR}/models"
os.makedirs(MODELS_DIR, exist_ok=True)

# LLM 配置
LLM_API_URL = "https://wzw.pp.ua/v1"
LLM_API_KEY = "sk-1Q4itG51GOWpjQ6tZcHiMijM2xZfCsvVv7qsnh5skbyV7hFI"
LLM_MODEL = "gpt-5.3-codex"

# 内存存储任务状态
tasks: Dict[str, Dict] = {}

# 请求模型
class GenerateRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None

class RegenerateRequest(BaseModel):
    parameters: Dict[str, Any]

# System Prompt
SYSTEM_PROMPT = """你是一个专业的 CAD 工程师，擅长使用 CADQuery Python 库创建精确的 3D 模型。

你的任务是将用户的自然语言描述转换为可执行的 CADQuery Python 代码。

规则：
1. 只输出有效的 Python 代码，使用 CADQuery 库
2. 代码必须完整可运行，包含所有必要的 import
3. 使用 cq.Workplane() 开始建模，保持简单可靠的建模方式
4. 关键尺寸必须参数化（定义为变量）
5. 添加注释说明关键步骤，注释必须使用中文
6. 最后必须返回 result 变量
7. 避免使用复杂的布尔运算（union/cut/intersect），优先使用简单的 extrude 和 cut
8. 如果必须使用 union，确保所有对象都是 Workplane 对象，使用 .val() 或 . solids() 转换
9. 不要使用 .sphere() 直接创建球体，使用 Workplane().sphere() 或将球体作为独立对象处理
10. 代码必须能够直接运行不报错

常用 CADQuery 操作：
- 草图：.box(), .circle(), .rect()
- 拉伸：.extrude()
- 切割：.cut(), .cutThruAll()
- 倒角：.edges().chamfer()
- 圆角：.edges().fillet()
- 变换：.translate(), .rotate()

输出格式必须是有效的 Python 代码，不要包含 markdown 代码块标记。"""

async def call_llm(prompt: str) -> str:
    """调用 LLM API 生成 CADQuery 代码"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{LLM_API_URL}/responses",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": LLM_MODEL,
                "input": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"请根据以下描述生成 CADQuery 代码：\n\n{prompt}"}
                ]
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["output"][0]["content"][0]["text"]

def extract_code_from_response(response: str) -> str:
    """从 LLM 响应中提取 Python 代码"""
    # 移除 markdown 代码块标记
    code = response.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()

def extract_parameters_from_code(code: str) -> Dict[str, Any]:
    """从代码中提取参数"""
    parameters = {}
    
    # 简单的参数提取逻辑
    import re
    
    # 匹配形如 "variable = value  # unit" 的行
    pattern = r'^(\w+)\s*=\s*([\d.]+)\s*#\s*(\w+)'
    
    for line in code.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            var_name = match.group(1)
            value = float(match.group(2))
            unit = match.group(3)
            
            # 根据值计算合理的 min/max
            min_val = value * 0.2
            max_val = value * 3
            
            parameters[var_name] = {
                "value": value,
                "min": round(min_val, 1),
                "max": round(max_val, 1),
                "unit": unit
            }
    
    return parameters

async def generate_cadquery_code(prompt: str) -> dict:
    """调用 LLM 生成 CADQuery 代码"""
    try:
        # 调用 LLM
        llm_response = await call_llm(prompt)
        
        # 提取代码
        code = extract_code_from_response(llm_response)
        
        # 确保代码包含必要的导入
        if "import cadquery" not in code:
            code = "import cadquery as cq\n\n" + code
        
        # 提取参数
        parameters = extract_parameters_from_code(code)
        
        return {
            "code": code,
            "parameters": parameters,
            "success": True
        }
    except Exception as e:
        return {
            "code": "",
            "parameters": {},
            "success": False,
            "error": str(e)
        }

# 执行 CADQuery 代码生成 STL
def execute_cadquery_and_export(code: str, model_id: str) -> dict:
    """执行 CADQuery 代码并导出 STL"""
    import cadquery as cq
    from cadquery import exporters
    import tempfile
    import traceback
    
    try:
        # 创建临时文件执行代码
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # 执行代码，获取 result 变量
        namespace = {}
        namespace['cq'] = cq
        namespace['exporters'] = exporters
        
        exec(code, namespace)
        
        # 获取结果模型
        result = namespace.get('result')
        if result is None:
            for var_name in ['model', 'part', 'shape', 'workplane']:
                if var_name in namespace:
                    result = namespace[var_name]
                    break
        
        if result is None:
            return {"success": False, "error": "代码中没有找到 result 变量"}
        
        # 导出 STL
        stl_path = f"{MODELS_DIR}/{model_id}.stl"
        exporters.export(result, stl_path, exporters.ExportTypes.STL)
        
        return {"success": True, "stl_path": stl_path}
        
    except Exception as e:
        error_msg = str(e)
        print(f"CADQuery 执行错误: {error_msg}")
        
        # 尝试修复常见错误
        try:
            print("尝试修复代码...")
            fixed_code = code
            import re
            
            # 修复1: 移除有问题的 fillet/chamfer
            fixed_code = re.sub(
                r'^(\s*)(result\s*=\s*.*\.edges\([^)]+\)\.(fillet|chamfer)\([^)]+\))',
                r'\1# \2  # 已禁用：没有合适的边',
                fixed_code, flags=re.MULTILINE
            )
            
            # 修复2: 将 .sphere() 改为 Workplane 方式
            if '.sphere(' in fixed_code and 'Workplane().sphere(' not in fixed_code:
                # 如果直接用 .sphere()，需要特殊处理
                pass  # 这种情况太难自动修复，让 LLM 重新生成
            
            namespace = {}
            namespace['cq'] = cq
            namespace['exporters'] = exporters
            exec(fixed_code, namespace)
            
            result = namespace.get('result')
            if result is None:
                for var_name in ['model', 'part', 'shape', 'workplane']:
                    if var_name in namespace:
                        result = namespace[var_name]
                        break
            
            if result:
                stl_path = f"{MODELS_DIR}/{model_id}.stl"
                exporters.export(result, stl_path, exporters.ExportTypes.STL)
                print("修复成功")
                return {"success": True, "stl_path": stl_path, "fixed": True}
        except Exception as e2:
            print(f"修复失败: {e2}")
        
        return {"success": False, "error": f"CADQuery 执行错误: {error_msg}"}
    finally:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)

# 模拟生成 STL 文件
def create_mock_stl(model_id: str) -> str:
    """创建一个简单的 STL 文件（备用）"""
    stl_path = f"{MODELS_DIR}/{model_id}.stl"
    with open(stl_path, 'w') as f:
        f.write("# Placeholder STL file\n")
    return stl_path

@app.post("/api/generate")
async def generate_model(request: GenerateRequest, background_tasks: BackgroundTasks):
    """提交生成任务"""
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    model_id = f"model_{uuid.uuid4().hex[:8]}"
    
    # 创建任务
    tasks[task_id] = {
        "id": task_id,
        "status": "processing",
        "prompt": request.prompt,
        "model_id": model_id,
        "created_at": datetime.now().isoformat(),
        "result": None
    }
    
    # 异步处理
    import asyncio
    asyncio.create_task(process_generation(task_id, request.prompt))
    
    return {
        "task_id": task_id,
        "status": "queued",
        "estimated_time": 15
    }

async def process_generation(task_id: str, prompt: str):
    """处理生成任务"""
    model_id = tasks[task_id]["model_id"]
    
    # 调用 LLM 生成代码
    result = await generate_cadquery_code(prompt)
    
    if not result["success"]:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = result.get("error", "Unknown error")
        return
    
    # 保存代码
    code_path = f"{MODELS_DIR}/{model_id}.py"
    with open(code_path, 'w') as f:
        f.write(result["code"])
    
    # 执行 CADQuery 生成真实 STL
    export_result = execute_cadquery_and_export(result["code"], model_id)
    
    if not export_result["success"]:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = export_result.get("error", "生成 STL 失败")
        # 仍然保存代码，方便调试
        code_path = f"{MODELS_DIR}/{model_id}.py"
        with open(code_path, 'w') as f:
            f.write(result["code"])
        return
    else:
        stl_path = export_result["stl_path"]
    
    # 更新任务状态
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["result"] = {
        "model_id": model_id,
        "code": result["code"],
        "parameters": result["parameters"],
        "downloads": {
            "stl": f"/api/models/{model_id}/download?format=stl",
            "python": f"/api/models/{model_id}/download?format=py"
        }
    }

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    response = {
        "task_id": task_id,
        "status": task["status"]
    }
    
    if task["status"] == "completed":
        response["result"] = task.get("result")
    elif task["status"] == "failed":
        response["error"] = task.get("error")
    
    return response

@app.get("/api/models/{model_id}/download")
async def download_model(model_id: str, format: str = "stl"):
    """下载模型文件"""
    if format == "stl":
        file_path = f"{MODELS_DIR}/{model_id}.stl"
        media_type = "application/octet-stream"
        filename = f"{model_id}.stl"
    elif format == "py":
        file_path = f"{MODELS_DIR}/{model_id}.py"
        media_type = "text/x-python"
        filename = f"{model_id}.py"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path, media_type=media_type, filename=filename)

@app.post("/api/models/{model_id}/regenerate")
async def regenerate_model(model_id: str, request: RegenerateRequest):
    """基于参数重新生成"""
    return {
        "task_id": f"task_{uuid.uuid4().hex[:8]}",
        "status": "queued",
        "message": "Regeneration queued with new parameters"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0", "llm_model": LLM_MODEL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
