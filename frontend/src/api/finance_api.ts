import React from "react";
import { request } from "./common_api.ts"
import type { FinanceRecordCreate, FinanceRecordPublic, BalancePublic } from "../types";

export async function getBalance() {
    const token = localStorage.getItem("token");
    if (!token) {
        throw new Error("No token found");
    }

    const response = await request<BalancePublic>("finance/balance", "GET",
        {"Authorization": `Bearer ${ token }` }
    );
    return response; // Assuming the response is a string representing the balance
}

export async function getFinanceRecords() {
    const token = localStorage.getItem("token");
    if (!token) {
        throw new Error("No token found");
    }
    const response = await request<FinanceRecordPublic[]>("finance/finance_record", "GET",
        {"Authorization": `Bearer ${ token }` }
    );
    return response; // Assuming the response is an array of transaction objects
}

export async function createFinanceRecord(record: FinanceRecordCreate) {
    const token = localStorage.getItem("token");
    if (!token) {
        throw new Error("No token found");
    }
    const response = await request<FinanceRecordPublic>("finance/finance_record", "POST",
        {"Authorization": `Bearer ${ token }` },
        record
    );
    return response; // Assuming the response is a transaction object
}
