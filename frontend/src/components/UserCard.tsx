import React from "react";
import type { WhitelistPublic } from "../types";

function UserCard({whitelist}:{whitelist: WhitelistPublic} ) {
    return (
        <li>
            <p>{whitelist.username}</p>
        </li>
    );
}
export default UserCard;