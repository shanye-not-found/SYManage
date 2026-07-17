import React from 'react';
import { useState ,useEffect } from 'react';
import { get_whitelist } from '../api/UserManage_api';
import type { WhitelistPublic } from '../types';
import UserCard from '../components/UserCard'
import AddWhitelistModal from './AddWhitelistModal';

function UserManagePage() {
    const [whitelists, setWhitelists] = useState<WhitelistPublic[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showAddModal, setShowAddModal] = useState(false); // 控制添加白名单模态框的显示与隐藏
    

    useEffect(() => {
        // 获取用户列表
        setLoading(true);
        setError(null); // 清空之前的错误
        get_whitelist().then((whitelists) => {
            const fwl = whitelists.filter((whitelist) => whitelist.username !== "superadmin"); // 过滤掉已退休的用户
            setWhitelists(fwl);
        }).catch((error) => {
            console.error('获取白名单失败:', error);
            setError(error?.message || '获取用户列表失败，请稍后重试');
        }).finally(() => {
            setLoading(false);
        });
    }, []);

    function renderContent(){
    
        if (loading){
            return <div>Loading...</div>;
        }
        if (error) {
            return <div style={{ color: 'red' }}>Error: {error}</div>;
        }
        if (whitelists.length === 0) {
            return <div>No users found.</div>;
        }
        return(
        <ul>
            {whitelists.map((whitelist) => (
                <UserCard key = {whitelist.email} whitelist={whitelist} />
            ))}
        </ul>
        )
    }

    function Buttons(){
        return (
            <div>
                <button onClick={() => setShowAddModal(true)}>添加白名单</button>
                <div>任职交接</div>
                <div>退休</div>
                <div>删除（Superadmin）</div>
            </div>

        )
    }


    function onCloseModal(){
        setShowAddModal(false);
    }

    function onSubmitOne(whitelist: WhitelistPublic){
        setWhitelists(prev => [...prev, whitelist])
    }
    function onSubmitMultiple(whitelistList: WhitelistPublic[]){
        setWhitelists(prev => [...prev, ...whitelistList])
    }




    return (
        <div>
            {renderContent()}
            {Buttons()}
            <AddWhitelistModal isOpen={showAddModal} onClose={onCloseModal} onSubmit={onSubmitOne} onSubmitMultiple={onSubmitMultiple} />

        </div>

    );
}
export default UserManagePage;