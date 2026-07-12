import type { CurrentUser } from './types';
import { useState, useEffect } from 'react';
import { login ,logout, getCurrentUser } from './api';

function App() {
    const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    // 每次组件挂载时，触发一次
    useEffect(() => {
        getCurrentUser().then((user) => {
            setCurrentUser(user);
        }).catch((error) => {
            logout();
        });
    }, []);



    async function handleLogin(e: React.SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        try {
            await login(email, password);
            getCurrentUser().then((user) => {
                setCurrentUser(user);
            }).catch((error) => {
                logout();
            });
        } catch (error) {
            setError(error instanceof Error ? error.message : '登录失败')
        }
    }

    async function handleLogout() {
        await logout();
        setCurrentUser(null);
        setEmail('');
        setPassword('');
    }
    
    if (currentUser){
        return(
            <div>
                <h1>欢迎，{currentUser.username}！</h1>
                <button onClick={handleLogout}>注销</button>
            </div>
        )
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

export default App;