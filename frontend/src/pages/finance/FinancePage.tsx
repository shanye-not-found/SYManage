import React from 'react';
import { useState ,useEffect } from 'react';
import { getBalance } from '../../api/finance_api'; // Import the getBalance function from the financeApi module

function FinancePage() { 
    const [balance, setBalance] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [curr_treasurer, setCurr_treasurer] = useState('');
    const [last_update, setLast_update] = useState('');

    useEffect(() => {
        setLoading(true);

        getBalance().then((data) => {
            setBalance(data.balance);
            setCurr_treasurer(data.current_treasurer_name);
            setLast_update(data.last_updated_at);
            setLoading(false);
        }).catch((err) => {
            setError(err.message);
            setLoading(false);
        }).finally(() => {
            setLoading(false);
        });
    }, []);

    if (loading) {
        return <div>加载中...</div>;
    }

    if (error) {
        return <div>错误: {error}</div>;
    }
    
    return (
        <div>
            <h1>财务管理</h1>
            <div>
                <p>当前余额: ¥{balance}</p>
                <p>当前财务部长: {curr_treasurer}</p>
                <p>最后更新时间: {last_update}</p>
            </div>
        </div>
    );
}
export default FinancePage;

