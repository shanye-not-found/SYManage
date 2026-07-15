import { useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';

function App() {
    const { currentUser, logout } = useAuth();   // 从 Context 取,不再自己管

    // 没登录 → 显示登录页
    if (!currentUser) {
        return <LoginPage />;
    }

    // 登录了 → 显示欢迎页
    return (
        <div>
            <h1>欢迎，{currentUser.username}！</h1>
            <button onClick={logout}>注销</button>
            <button onClick={() => console.log('查看白名单')}>查看白名单</button>
        </div>

    );
}

export default App;
