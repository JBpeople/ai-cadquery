import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Box, Grid, RoundedBox } from '@react-three/drei';
import * as THREE from 'three';
import './App.css';

// 3D 模型组件
function Model3D({ parameters }: { parameters: Record<string, any> }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
    }
  });

  // 根据参数调整大小
  const length = parameters?.length?.value ? parameters.length.value / 50 : 1;
  const width = parameters?.width?.value ? parameters.width.value / 50 : 0.6;
  const height = parameters?.thickness?.value ? parameters.thickness.value / 50 : 0.1;

  return (
    <RoundedBox 
      ref={meshRef} 
      args={[length, height, width]} 
      position={[0, height/2, 0]}
      radius={0.02}
    >
      <meshStandardMaterial color="#4f46e5" metalness={0.3} roughness={0.4} />
    </RoundedBox>
  );
}

// 主应用组件
function App() {
  const [prompt, setPrompt] = useState('');
  const [taskId, setTaskId] = useState('');
  const [status, setStatus] = useState<'idle' | 'submitting' | 'processing' | 'completed' | 'failed'>('idle');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [history, setHistory] = useState<string[]>([]);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // 提交生成任务
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setStatus('submitting');
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit task');
      }

      const data = await response.json();
      setTaskId(data.task_id);
      setStatus('processing');
      setHistory(prev => [...prev, prompt]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  };

  // 轮询任务状态
  useEffect(() => {
    if (!taskId || status !== 'processing') return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/tasks/${taskId}`);
        const data = await response.json();

        if (data.status === 'completed') {
          setStatus('completed');
          setResult(data.result);
          clearInterval(pollInterval);
        } else if (data.status === 'failed') {
          setStatus('failed');
          setError(data.error || 'Task failed');
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [taskId, status, API_URL]);

  // 快速选择历史
  const selectHistory = (item: string) => {
    setPrompt(item);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🎨 AI CADQuery</h1>
        <p>用自然语言设计 3D 模型 · 工程级 CAD 输出</p>
      </header>

      <main className="main">
        <div className="container">
          {/* 左侧：输入和历史 */}
          <div className="left-panel">
            <div className="input-section">
              <h3>描述你的设计</h3>
              <form onSubmit={handleSubmit}>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="例如：设计一个 M4 螺丝的固定支架，长 50mm，宽 30mm，厚度 5mm，中间开 4.5mm 的通孔..."
                  rows={5}
                  disabled={status === 'processing' || status === 'submitting'}
                />
                <button
                  type="submit"
                  disabled={status === 'processing' || status === 'submitting' || !prompt.trim()}
                >
                  {status === 'processing' ? '⏳ 生成中...' : 
                   status === 'submitting' ? '📤 提交中...' : 
                   '🚀 生成模型'}
                </button>
              </form>

              {error && <div className="error">❌ {error}</div>}

              {history.length > 0 && (
                <div className="history">
                  <h4>历史记录</h4>
                  <div className="history-list">
                    {history.slice(-5).map((item, idx) => (
                      <button 
                        key={idx} 
                        className="history-item"
                        onClick={() => selectHistory(item)}
                      >
                        {item.length > 30 ? item.substring(0, 30) + '...' : item}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 参数面板 */}
            {result?.parameters && Object.keys(result.parameters).length > 0 && (
              <div className="parameters-section">
                <h3>🔧 可调参数</h3>
                {Object.entries(result.parameters).map(([key, param]: [string, any]) => (
                  <div key={key} className="parameter-control">
                    <label>
                      <span className="param-name">{key}</span>
                      <span className="param-value">{param.value} {param.unit}</span>
                    </label>
                    <input
                      type="range"
                      min={param.min}
                      max={param.max}
                      step={(param.max - param.min) / 100}
                      value={param.value}
                      readOnly
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 右侧：预览和代码 */}
          <div className="right-panel">
            {/* 3D 预览 */}
            <div className="preview-panel">
              <h3>🔍 3D 预览</h3>
              <div className="canvas-container">
                <Canvas camera={{ position: [3, 3, 3], fov: 50 }}>
                  <ambientLight intensity={0.5} />
                  <directionalLight position={[10, 10, 5]} intensity={1} />
                  <Grid args={[10, 10]} cellSize={0.5} />
                  {status === 'completed' && result ? (
                    <Model3D parameters={result.parameters} />
                  ) : (
                    <>
                      <Box args={[1, 0.1, 0.6]} position={[0, 0.05, 0]}>
                        <meshStandardMaterial color="#ccc" wireframe />
                      </Box>
                      <Box args={[0.5, 0.5, 0.5]} position={[0, 0.25, 0]}>
                        <meshStandardMaterial color="#4f46e5" transparent opacity={0.3} />
                      </Box>
                    </>
                  )}
                  <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
                </Canvas>
                {status === 'processing' && (
                  <div className="loading-overlay">
                    <div className="spinner"></div>
                    <p>AI 正在生成模型...</p>
                  </div>
                )}
              </div>
            </div>

            {/* 代码显示 */}
            {result?.code && (
              <div className="code-section">
                <h3>📄 CADQuery 代码</h3>
                <pre><code>{result.code}</code></pre>
              </div>
            )}

            {/* 下载按钮 */}
            {result?.downloads && (
              <div className="downloads">
                <h3>💾 下载文件</h3>
                <div className="download-buttons">
                  <a 
                    href={`${API_URL}${result.downloads.stl}`} 
                    className="download-btn stl"
                    download
                  >
                    📦 下载 STL (3D打印)
                  </a>
                  <a 
                    href={`${API_URL}${result.downloads.python}`} 
                    className="download-btn python"
                    download
                  >
                    🐍 下载 Python 源码
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>AI CADQuery © 2026 · 智能参数化 CAD 建模平台 · Powered by CADQuery & LLM</p>
      </footer>
    </div>
  );
}

export default App;
