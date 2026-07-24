import { useAuth } from '../contexts/AuthContext'
import { Link } from 'react-router-dom'
import React from 'react'

function NavPage() {
    const { currentUser, logout } = useAuth()
    
    return (
        <div>
            <h1>欢迎，{currentUser?.username}！</h1>
            <button onClick={logout}>注销</button>
            <Link to="/usermanage">人员管理</Link>
            <Link to='/finance'>财务管理</Link>
        </div>
    )
}

export default NavPage