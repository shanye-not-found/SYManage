import React from 'react';
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import type { Permission } from '../types';
import { create_handover_table } from '../api/UserManage_api';
import type { HandoverTableCreate, HandoverTablePublic,  } from '../types';

type HandoverModalProps = {
    onCloseHandover: () => void;
    onSubmitUpdate: () => void;
}


function HandoverModal({ onCloseHandover, onSubmitUpdate }: HandoverModalProps) {
    const { currentUser } = useAuth();

    // 需要填的就是to的邮箱，自己的权限和对方的权限
    const [toEmail, setToEmail] = useState('');
    const [targetPermission, setTargetPermission] = useState<Permission>('bar_manager');
    const [error, setError] = useState('');
    const [resmsg, setResmsg] = useState('');
    const [loading, setLoading] = useState(false); // 添加加载状态变量
    const [token, setToken] = useState('');

    function showeOptions(permission: Permission) {
        if (permission === "superadmin" || permission === "president"){
            return(
                <select
                    value={targetPermission}
                    onChange={e => setTargetPermission(e.target.value as Permission)}
                >
                    <option value="president">社长</option>
                    <option value="treasurer">财务部长</option>
                    <option value="vice_president">副社长</option>
                    <option value="cocktail_minister">调酒部长</option>
                    <option value="tea_minister">茶艺部长</option>
                    <option value="bar_manager">调酒部管理</option>
                    <option value="tea_manager">茶艺部管理</option>
                </select>
            )
        }else if (permission === "treasurer"){
            return(
                <select
                    value={targetPermission}
                    onChange={e => setTargetPermission(e.target.value as Permission)}
                >
                    <option value="treasurer">财务部长</option>
                </select>
            )
        }
    }
    function copyToken() {
        if (token) {
            navigator.clipboard.writeText(token);
            alert('Token copied to clipboard!'); // 提示用户复制成功
        }
    }
    if (currentUser !== null) {
        const [selfPermission, setSelfPermission] = useState<Permission>(currentUser.permission);
            const handleSubmit = async (e: React.SubmitEvent) => {
                e.preventDefault();
                if (!toEmail) {
                    setError('Email is required.');
                    return;
                }
                if (loading){
                    return; // 防止重复提交
                }
                setError(''); // 清空错误信息
                setResmsg(''); // 清空响应信息
                setLoading(true); // 设置加载状态为true

                const new_table: HandoverTableCreate = {
                    from_user_email: currentUser.email,
                    to_user_email: toEmail,
                    target_permission: targetPermission,
                    self_permission: selfPermission,
                };
                try {
                    const response = await create_handover_table(new_table);
                    if ('token' in response) {
                        // 这里 TS 会把 response 收窄成 HandoverTablePublic
                        setToken(response.token);
                        const msg = '您已成功生成交接表，请再次确认交接信息:\n交接人姓名：' + response.to_user_name + '\n将要赋予对方的权限：' + response.target_permission + '\n原高层管理将要获得的权限：' + response.self_permission + "\n\n交接秘钥："+ token+"\n点击复制秘钥以复制";
                        setResmsg(msg);
                    }else{
                        const msg = '您已成功更改权限！请再次确认交接信息:\n原高层管理姓名：' + response.high_username+ '\n交接人姓名：'+ response.low_username + '\n赋予对方的权限：' + response.target_permission + '\n原高层管理将要获得的权限：' + response.self_permission;
                        setResmsg(msg);
                    }

                }catch (error) {
                    setError(error instanceof Error ? error.message : 'Failed to create handover table.');
                }finally {
                    setLoading(false); // 设置加载状态为false
                }
            };
            return (
                <div className="modal">
                    <form onSubmit={handleSubmit}>
                        <h2>任职交接</h2>

                        {error && <div style={{ color: 'red' }}>{error}</div>}

                        <div>
                            <label>交接人邮箱：</label>
                            <input
                                type="email"
                                value={toEmail}
                                onChange={e => setToEmail(e.target.value)}
                                placeholder="对方的邮箱"
                                required
                            />
                        </div>

                        <div>
                            <label>赋予对方的权限：</label>
                            {showeOptions(selfPermission)}
                        </div>

                        <div>
                            <label>原高层管理将要获得的权限：</label>
                            <select
                                value={selfPermission}
                                onChange={e => setSelfPermission(e.target.value as Permission)}
                            >
                                <option value="bar_manager">调酒部管理</option>
                                <option value="tea_manager">茶艺部管理</option>
                            </select>
                        </div>

                        <div>
                            <button type="submit" disabled={loading}>
                                {loading ? '生成中...' : '生成交接表'}
                            </button>
                        </div>
                    </form>

                    {resmsg && (
                        <div style={{ whiteSpace: 'pre-wrap', color: 'green' }}>
                            {resmsg}
                        </div>
                    )}

                    <button onClick={onCloseHandover}>关闭</button>
                    <button onClick={copyToken}>复制秘钥</button>
                </div>
            );

        }
    }
export default HandoverModal;



