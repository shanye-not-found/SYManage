import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext'

function LoginForm() {  
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    async function handleLogin(e: React.SubmitEvent<HTMLFormElement>) {
            e.preventDefault();
            try {
                await login(email, password);
            } catch (error) {
                setError(error instanceof Error ? error.message : '登录失败')
            }
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
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    )
}

export default LoginForm;