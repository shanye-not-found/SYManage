import React from 'react';
import { useState ,useEffect } from 'react';
import { get_whitelist } from '../../api/UserManage_api';
import type { WhitelistPublic } from '../../types';
import UserCard from '../../components/UserCard'
import AddWhitelistModal from './AddWhitelistModal';
import HandoverModal from './HandoverModal';
import { useAuth } from '../../contexts/AuthContext';
function UserManagePage() {
    const now = new Date(); 
    const nowYear = now.getFullYear(); 
    const [whitelists, setWhitelists] = useState<WhitelistPublic[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showAddModal, setShowAddModal] = useState(false); // 控制添加白名单模态框的显示与隐藏
    const [showHandover, setShowHandover] = useState(false); // 控制任职交接模态框的显示与隐藏
    // 8 月后进入新学年，初始页要 +1，否则会少显示一年
    const [nowPage, setCurrentPage] = useState(now.getMonth() >= 7 ? nowYear - 1: nowYear);

    function getWhitelist(){
        setLoading(true);
        setError(null); // 清空之前的错误
        get_whitelist().then((whitelists) => {
            const fwl = whitelists.filter((whitelist) => whitelist.username !== "superadmin" );
            setWhitelists(fwl);
        }).catch((error) => {
            console.error('获取白名单失败:', error);
            setError(error?.message || '获取用户列表失败，请稍后重试');
        }).finally(() => {
            setLoading(false);
        });
    }
    
    useEffect(() => {
        // 只负责拉数据；过滤是派生数据，在 render 时直接算
        getWhitelist();
    }, []);

    // 派生数据：按当前学年页过滤，whitelists 或 nowPage 变化时自动重算
    const endYear = new Date(nowPage, 7, 1);
    const startYear = new Date(nowPage - 1, 7, 1);
    const showWhitelists = whitelists.filter((whitelist) => {
        const createDate = new Date(whitelist.created_at);
        const retiredDate = whitelist.retired_at ? new Date(whitelist.retired_at) : null;
        return createDate < endYear && (!retiredDate || retiredDate >= startYear);
    });
    
// 这个也要改
    function renderContent(){
    
        if (loading){
            return <div>Loading...</div>;
        }
        if (error) {
            return <div style={{ color: 'red' }}>Error: {error}</div>;
        }
        if (showWhitelists.length === 0) {
            return <div>该学年无成员。</div>;
        }
        return(
        <ul>
            {showWhitelists.map((whitelist) => (
                <UserCard key = {whitelist.email} whitelist={whitelist} />
            ))}
        </ul>
        )
    }
    function handleLeftChange(){
        const changePage = nowPage - 1;
        if (changePage >= 2024){
            setCurrentPage(changePage); // 防止页面超出范围
        }else{
            setCurrentPage(nowYear); // 防止页面超出范围
        }
    
    }
    function handleRightChange(){
        const changePage = nowPage + 1;
        if (changePage <= nowYear){
            setCurrentPage(changePage);
        }else{
            setCurrentPage(2024); // 防止页面超出范围
        }
    }
    function Buttons(){
        const { currentUser } = useAuth(); // 获取当前用户

        // 权限控制：只有 superadmin 和 president 可以添加白名单
        const canAddWhitelist = currentUser?.permission === 'superadmin' ||
                               currentUser?.permission === 'president';

        // 权限控制：只有 superadmin、president、treasurer 可以进行任职交接
        const canHandover = currentUser?.permission === 'superadmin' ||
                           currentUser?.permission === 'president' ||
                           currentUser?.permission === 'treasurer';

        return (
            <div>
                {canAddWhitelist && (
                    <button onClick={() => setShowAddModal(true)}>添加白名单</button>
                )}
                {canHandover && (
                    <button onClick={() => setShowHandover(true)}>任职交接</button>
                )}
                <div>退休</div>
                <div>删除（Superadmin）</div>
                <button onClick={() => handleLeftChange()}>左键</button>
                <span>{nowPage - 1}-{nowPage} 学年</span>
                <button onClick={() => handleRightChange()}>右键</button>
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
    function onCloseHandover(){
        setShowHandover(false);
        getWhitelist(); // 重新拉数据；showWhitelists 会自动重算
    }

    return (
        <div>
            {renderContent()}
            {Buttons()}
            <AddWhitelistModal isOpen={showAddModal} onClose={onCloseModal} onSubmit={onSubmitOne} onSubmitMultiple={onSubmitMultiple} />
            {showHandover && <HandoverModal onCloseHandover={onCloseHandover} />}
        </div>

    );
}
export default UserManagePage;