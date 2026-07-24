export type Permission =
  | 'superadmin'
  | 'president'
  | 'vice_president'
  | 'cocktail_minister'
  | 'tea_minister'
  | 'treasurer'
  | 'bar_manager'
  | 'tea_manager'
  | 'finance_manager'

export type Token = {
    access_token: string
    token_type: string
}

export type CurrentUser = {
    id: string
    username: string
    email: string
    permission: Permission
}

export type WhitelistPublic = {
    id: string
    username: string
    email: string
    permission: Permission
    wechat_account: string
    retired: boolean | null
    created_at: string
    retired_at: string | null
    retired_description: string | null
    highest_permission: Permission
}

export type WhitelistCreate = {
    username: string
    email: string
    permission: Permission
    wechat_account: string
    retired: boolean 
}
export type UserCreate = {
    email: string
    password: string
}

export type HandoverTableCreate = {
    from_user_email: string
    to_user_email: string
    target_permission: Permission
    self_permission: Permission
}

export type HandoverTablePublic = {
    token: string
    to_user_name: string
    target_permission: Permission
    self_permission: Permission
}


export type PermissionUpdate={    
    low_user_email:string,
    token: string
}

export type PermissionUpdatePublic={
    high_username: string | null,
    low_username: string
    target_permission: Permission
    self_permission: Permission
}

export type FinanceDirection = 'income' | 'expense'

export type FinanceRecordCreate = {
    direction: FinanceDirection
    amount: string
    description: string
    created_by_email: string
}

export type FinanceRecordPublic = {
    direction: FinanceDirection
    amount: string
    created_by_username: string
    is_deleted: boolean
    description: string
    created_at: string
    current_treasurer_name: string
}

export type BalancePublic = {
    balance: string
    current_treasurer_name: string
    last_updated_at: string
}
