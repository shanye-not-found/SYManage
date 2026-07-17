import type { WhitelistPublic , WhitelistCreate } from "../types.ts";
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
