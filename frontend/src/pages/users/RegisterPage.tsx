import React from 'react';
import { useState } from 'react';
import type { UserCreate } from "../../types"
import { createUser } from "../../api/common_api";
import { useNavigate } from 'react-router-dom';

function RegisterPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [successmsg, setSuccessmsg] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError('');
        try {
            await createUser(email,password);
            setSuccessmsg('用户创建成功，三秒后跳转到登录页');
            setEmail('');
            setPassword('');
            setConfirmPassword('');
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } catch (error) {
            console.error('Error creating user:', error);
            setError(error instanceof Error ? error.message : 'Failed to create user');
        } finally {
            setLoading(false);
        }
    };

    const handleBackToLogin = () => {
        navigate('/login');
    };

    return (
        <div style={{ maxWidth: 360, margin: '80px auto', fontFamily: 'sans-serif' }}>
            <h2>注册 SYManage</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: 12 }}>
                    <label>邮箱</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{ display: 'block', width: '100%' }}
                        required
                        disabled={loading}
                    />
                </div>
                <div style={{ marginBottom: 12 }}>
                    <label>密码</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{ display: 'block', width: '100%' }}
                        required
                        disabled={loading}
                    />
                </div>
                <div style={{ marginBottom: 12 }}>
                    <label>确认密码</label>
                    <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        style={{ display: 'block', width: '100%' }}
                        required
                        disabled={loading}
                    />
                </div>
                <button type="submit" disabled={loading}>
                    {loading ? '注册中...' : '注册'}
                </button>
            </form>

            <button onClick={handleBackToLogin} style={{ marginTop: 8 }}>
                返回登录
            </button>

            {error && <p style={{ color: 'red' }}>{error}</p>}
            {successmsg && <p style={{ color: 'green' }}>{successmsg}</p>}
        </div>
    );
}

export default RegisterPage;