export type Permission =
  | 'superadmin'
  | 'president'
  | 'vice_president'
  | 'cocktail_minister'
  | 'tea_minister'
  | 'treasurer'
  | 'manager'

export type Token = {
    access_token: string
    token_type: string
}

export type CurrentUser = {
    id: number
    username: string
    email: string
    permission: Permission

}
