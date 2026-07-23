    // username: string;
    // email: string;
    // permission: Permission;
    // wechat_account: string;
    // retired: boolean;

import React, { useState } from 'react';
import type { Permission , WhitelistCreate , WhitelistPublic } from '../types';
import { create_whitelist , create_whitelist_multiple } from '../api/UserManage_api';

// 批量添加的 JSON 示例，用反引号(模板字符串)才能跨多行、内部还能带双引号。
// 顶格写，避免前导缩进空格被算进 placeholder。
const JSON_PLACEHOLDER = `[
  {
    "username": "一个名字",
    "email": "120090135@link.cuhk.edu.cn",
    "permission": "bar_manager",
    "wechat_account": "wxid_alex992",
    "retired": false
  },
  {
    "username": "另一个名字",
    "email": "121090135@link.cuhk.edu.cn",
    "permission": "cocktail_minister",
    "wechat_account": "elena_wechat",
    "retired": false
  },
  {
    "username": "不重复的名字",
    "email": "122090135@link.cuhk.edu.cn",
    "permission": "tea_minister",
    "wechat_account": "li_shunxi_1960",
    "retired": true
  }
]`;

// 给多模态 AI 的提示词：让它把任意成员数据整理成上面 JSON_PLACEHOLDER 的模板。
// 注意：内容里刻意不使用反引号，避免和这个模板字符串的定界符冲突。
const prompts = `# 角色
你是一个数据录入助手。我会给你一份包含社团成员信息的数据（可能是图片、截图、表格或纯文本）。你的任务是把其中每个人的信息，严格转换成下面规定的 JSON 模板格式，并在最后报告数据中可能存在的错误。

# 输出的 JSON 模板（严格遵守）
输出必须是一个 JSON 数组，数组里每个元素是一个对象，对象只能包含以下 5 个字段，顺序、拼写、大小写都要完全一致。模板如下（仅示例一个元素）：

[
  {
    "username": "一个名字",
    "email": "120090135@link.cuhk.edu.cn",
    "permission": "bar_manager",
    "wechat_account": "wxid_alex992",
    "retired": false
  }
]

# 各字段的规则
- username（字符串）：成员姓名。不能重复——数组内每个 username 必须唯一。
- email（字符串）：成员邮箱，必须是合法的邮箱格式（形如 xxx@xxx.xxx）。不能重复——数组内每个 email 必须唯一。
- permission（字符串）：成员权限，只能从下面这几个值里取，必须完全按英文小写和下划线拼写，不要翻译、不要自创：
  - bar_manager（调酒部管理）
  - tea_manager（茶艺部管理）
  如果原始数据里写的是中文职位，请按上面的对照关系映射成对应的英文值。
- wechat_account（字符串）：微信号。
- retired（布尔值）：是否已退休，只能是 true 或 false（不加引号的 JSON 布尔值，不是字符串 "true"）。如果原始数据没有说明，默认填 false。
# 硬性要求
1. 输出的 JSON 必须能被 JSON.parse 直接解析：用双引号、不要有多余逗号、不要有注释。
2. 不要增加模板以外的任何字段，也不要漏字段。
3. 即使某条数据有问题，也要尽量按你的最佳猜测填进 JSON，然后在报告里指出问题，不要直接丢弃这条数据。

# 输出格式
请按下面两部分输出：

## 第一部分：JSON 数据
直接给出上面规则下的 JSON 数组。

## 第二部分：错误与风险报告
用列表逐条说明你在转换过程中发现的可能出错的地方，例如：
- 缺失字段：某人没有微信号 / 没有邮箱等。
- 邮箱格式不合法或看起来像识别错误（比如 O 和 0、l 和 1 混淆）。
- permission 无法对应到 5 个合法值之一（比如原始数据写的是“财务部长/社长”这类当前不支持从这里录入的职位）。
- 重复：出现了重复的 username 或重复的 email。
- 你对某个字段做了猜测或默认填值（比如 retired 没写、职位靠上下文推断）的地方，也要标出来，方便人工复核。
如果没有发现任何问题，就写“未发现明显问题”。

# 待处理的数据
（把要识别的图片 / 表格 / 文字放在这里）`;

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (whitelist: WhitelistPublic) => void;
    onSubmitMultiple: (whitelistList: WhitelistPublic[]) => void;
};

function AddWhitelistModal({ isOpen, onClose, onSubmit , onSubmitMultiple }: Props) {
    if (isOpen === false){return null;}
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [permission, setPermission] = useState<Permission>('bar_manager');
    const [wechat_account, setWechatAccount] = useState('');
    const [retired, setRetired] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [submittingOne, setSubmittingOne] = useState(false);
    const [submittingMultiple, setSubmittingMultiple] = useState(false);
    const [jsonInput, setJsonInput] = useState('');


    const setAnythingNull = () => {
        setUsername('');
        setEmail('');
        setPermission('bar_manager');
        setWechatAccount('');
        setRetired(false);
    };



    const handleSubmitOne = async (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        if (!username || !email || !permission || !wechat_account) {
            setError('所有字段都必须填写');
            return;
        }
        if (submittingOne) return;
        setSubmittingOne(true);
        const whitelist: WhitelistCreate = {
            username,
            email,
            permission,
            wechat_account,
            retired,
        };

        try {
            const response = await create_whitelist(whitelist);
            onSubmit(response);
            setAnythingNull();
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Create whitelist failed');
        } finally {
            setSubmittingOne(false);
        }
    };

    const handleSubmitMultiple = async (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        if (!jsonInput) {
            setError('JSON 输入不能为空');
            return;
        }
        setSubmittingMultiple(true);
        const whitelistList: WhitelistCreate[] = JSON.parse(jsonInput);
        whitelistList.forEach(whitelist => {
        if (!['bar_manager', 'tea_manager', 'finance_manager'].includes(whitelist.permission)) {
                setError('越权警告！');
                return;
            }
        })
        try {
            const responses = await create_whitelist_multiple(whitelistList);
            onSubmitMultiple(responses);
            setJsonInput(''); // 清空输入框
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Create whitelist failed');
        } finally {
            setSubmittingMultiple(false);
        }
    };

    const handleCopyPrompt = () => {
        const content = jsonInput; // 获取当前输入的 JSON 数据
        navigator.clipboard.writeText(prompts+'\n\n'+content);
    };


    

    return (
        <div className="modal">
            <form onSubmit={handleSubmitOne}>
                <h2>添加白名单（社长和财务部长应前往任职交接）</h2>
                
                {error && <div style={{color: 'red'}}>{error}</div>}
                
                <div>
                    <label>用户名：</label>
                    <input 
                        type="text" 
                        value={username} 
                        onChange={e => setUsername(e.target.value)} 
                        required 
                    />
                </div>
                
                <div>
                    <label>邮箱：</label>
                    <input 
                        type="email" 
                        value={email} 
                        onChange={e => setEmail(e.target.value)} 
                        required 
                    />
                </div>
                
                <div>
                    <label>微信号：</label>
                    <input 
                        type="text" 
                        value={wechat_account} 
                        onChange={e => setWechatAccount(e.target.value)} 
                        required 
                    />
                </div>
                
                <div>
                    <label>权限：</label>
                    <select 
                        value={permission} 
                        onChange={e => setPermission(e.target.value as Permission)}
                    >
                        <option value="bar_manager">调酒部管理</option>
                        <option value="tea_manager">茶艺部管理</option>
                        <option value="finance_manager">财务部管理</option>
                    </select>
                </div>
                
                <div>
                    <label>
                        <input 
                            type="checkbox" 
                            checked={retired} 
                            onChange={e => setRetired(e.target.checked)} 
                        />
                        已退休
                    </label>
                </div>
                
                <div>
                    <button type="submit" disabled={submittingOne}>
                        {submittingOne ? '提交中...' : '提交'}
                    </button>
                </div>
            </form>

            <form onSubmit={handleSubmitMultiple}>
                <h2>批量添加白名单</h2>
                
                {error && <div style={{color: 'red'}}>{error}</div>}
                
                <div>
                    <label>你应该传入一个 JSON 数据：</label>
                    <textarea 
                        value={jsonInput}
                        onChange={e => setJsonInput(e.target.value)}
                        placeholder={JSON_PLACEHOLDER}
                        rows={12}
                        style={{width: '100%', fontFamily: 'monospace', fontSize: '13px'}}
                        required
                    />
                    <small style={{color: '#666'}}>
                        粘贴 JSON 数组。每个对象需包含: username, email, permission, wechat_account, retired
                    </small>
                </div>
                
                <div>
                    <button type="submit" disabled={submittingMultiple}>
                        {submittingMultiple ? '提交中...' : '批量添加'}
                    </button>
                </div>
            </form>
            <a 
            href="https://chat.z.ai/"
            target="_blank" 
            rel="noopener noreferrer"
            >
                <button onClick={handleCopyPrompt} >复制提示词并跳转到 AI</button>
            </a>
            <button onClick={onClose}>关闭</button>
        </div>
    )

}

export default AddWhitelistModal;