import React from 'react';  // 使用 React 18.2.0
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom';
function LoginForm() {  
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();  // 使用 useNavigate 来导航到其他页面

    async function handleLogin(e: React.SubmitEvent<HTMLFormElement>) {
            e.preventDefault();
            try {
                await login(email, password);
                navigate('/navpage');
            } catch (error) {
                setError(error instanceof Error ? error.message : '登录失败')
            }
        }

    function handleRegister() {
        navigate('/register');  // 导航到注册页面
    }
    return (
        <div style={{ maxWidth: 360, margin: '80px auto', fontFamily: 'sans-serif' }}>
            <h2>登录 SYManage</h2>
            <form onSubmit={handleLogin}>
                <div style={{ marginBottom: 12 }}>
                    <label>邮箱</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{ display: 'block', width: '100%' }}
                    />
                </div>
                <div style={{ marginBottom: 12 }}>
                    <label>密码</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{ display: 'block', width: '100%' }}
                    />
                </div>
                <button type="submit">登录</button>
            </form>
            <button onClick={handleRegister}>注册</button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    )
}

export default LoginForm;