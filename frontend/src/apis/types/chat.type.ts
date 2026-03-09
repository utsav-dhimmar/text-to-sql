export interface ChatHistoryCreate {
    human_query: string;
    session_id?: string;
    sql_generated?: string;
    result_summary?: string;
}

export interface ChatHistoryResponse {
    id: string;
    user_id: string;
    human_query: string;
    sql_generated?: string;
    result_summary?: string;
    created_at: string;
}

export interface QueryResponse {
    status: "answer" | "clarification_needed" | "out_of_scope" | "error";
    data?: any[];
    message?: string;
    session_id: string;
    cached: boolean;
    remaining_requests?: number;
}
