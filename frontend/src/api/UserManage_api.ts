import type { PermissionUpdate , WhitelistPublic , WhitelistCreate, HandoverTableCreate , HandoverTablePublic, PermissionUpdatePublic} from "../types.ts";
import { request } from "./common_api.ts"

export async function get_whitelist(): Promise<WhitelistPublic[]> {
    const token = localStorage.getItem("token");
    if (!token ){
        throw new Error("Unauthorized"); // Handle unauthorized access
    }
    return await request<WhitelistPublic[]>(`users/whitelist`, "GET");
}

export async function create_whitelist(whitelist: WhitelistCreate): Promise<WhitelistPublic> {

    const token = localStorage.getItem("token");
    
    if ( !token ){
        throw new Error("Unauthorized"); // Handle unauthorized access
    }

    return await request<WhitelistPublic>(`users/add_whitelist`, "POST", 
        { "Authorization": `Bearer ${ token }` }, whitelist);

}

export async function create_whitelist_multiple(whitelist: WhitelistCreate[]): Promise<WhitelistPublic[]> {
    const token = localStorage.getItem("token");
    
    if ( !token ){
        throw new Error("Unauthorized"); // Handle unauthorized access
    }
    
    return await request<WhitelistPublic[]>(`users/add_whitelist_multiple`, "POST", 
        { "Authorization": `Bearer ${ token }` }, whitelist);

}

export async function create_handover_table(handover_table: HandoverTableCreate): Promise<HandoverTablePublic | PermissionUpdatePublic> {
    const token = localStorage.getItem("token");
    
    if ( !token ){
        throw new Error("Unauthorized"); // Handle unauthorized access
    }
    return await request<HandoverTablePublic>(`users/gen_handover_table`, "POST", 
        { "Authorization": `Bearer ${ token }` }, handover_table);

}

export async function update_permission(update_table: PermissionUpdate): Promise<PermissionUpdatePublic> {
    const token = localStorage.getItem("token");
    
    if ( !token ){
        throw new Error("Unauthorized"); // Handle unauthorized access
    }
    return await request<PermissionUpdatePublic>(`users/handover_permission`, "POST", 
        { "Authorization": `Bearer ${ token }` }, update_table);
}
