"""
CADQuery Worker - 执行 CADQuery 代码生成 3D 模型
"""
import os
import sys
import json
import tempfile
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/app')

import cadquery as cq
from cadquery import exporters

DATA_DIR = "/app/data/models"
os.makedirs(DATA_DIR, exist_ok=True)

def execute_cadquery_code(code: str, model_id: str) -> dict:
    """
    执行 CADQuery Python 代码，生成 STL 和 STEP 文件
    
    Args:
        code: CADQuery Python 代码
        model_id: 模型 ID
    
    Returns:
        {
            "success": bool,
            "stl_path": str,
            "step_path": str,
            "error": str
        }
    """
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
            # 尝试其他常见变量名
            for var_name in ['model', 'part', 'shape', 'workplane']:
                if var_name in namespace:
                    result = namespace[var_name]
                    break
        
        if result is None:
            return {
                "success": False,
                "error": "No result variable found in code"
            }
        
        # 导出文件
        stl_path = os.path.join(DATA_DIR, f"{model_id}.stl")
        step_path = os.path.join(DATA_DIR, f"{model_id}.step")
        
        # 导出 STL
        exporters.export(result, stl_path, exporters.ExportTypes.STL)
        
        # 导出 STEP
        exporters.export(result, step_path, exporters.ExportTypes.STEP)
        
        return {
            "success": True,
            "stl_path": stl_path,
            "step_path": step_path
        }
        
    except Exception as e:
        error_msg = f"Error executing CADQuery code: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    finally:
        # 清理临时文件
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)

def process_task(task_data: dict) -> dict:
    """处理生成任务"""
    model_id = task_data.get('model_id')
    code = task_data.get('code')
    
    if not model_id or not code:
        return {
            "success": False,
            "error": "Missing model_id or code"
        }
    
    print(f"Processing task for model: {model_id}")
    result = execute_cadquery_code(code, model_id)
    
    return result

if __name__ == "__main__":
    # 测试代码
    test_code = '''
import cadquery as cq

# 创建一个简单的支架
length = 50
width = 30
thickness = 5
hole_dia = 4.5

result = (cq.Workplane("XY")
    .box(length, width, thickness)
    .faces(">Z").workplane()
    .hole(hole_dia)
    .edges().chamfer(2)
)
'''
    
    result = execute_cadquery_code(test_code, "test_model")
    print(json.dumps(result, indent=2))
