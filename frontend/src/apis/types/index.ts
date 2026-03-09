export interface UserResponse {
  id: string;
  email: string;
  role: string;
  status: string;
}

export interface UserAdminResponse extends UserResponse {
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserResponse;
}

export interface MessageResponse {
  message: string;
}

export interface ChatHistoryResponse {
  id: string;
  user_id: string;
  human_query: string;
  sql_generated?: string;
  result_summary?: string;
  created_at: string;
}

export interface DatasetResponse {
  id: string;
  name: string;
  source: string;
  table_name: string;
  row_count: number;
  status: string;
  uploaded_by?: string;
  created_at: string;
}

export interface QueryResponse {
  status: string;
  data?: any[];
  message?: string;
  session_id: string;
  cached: boolean;
  remaining_requests?: number;
}

export interface AuditLogResponse {
  id: string;
  actor_id: string;
  action: string;
  target_id?: string;
  created_at: string;
}

export interface AdminAnalyticsResponse {
  total_users: number;
  active_users: number;
  banned_users: number;
  total_admins: number;
  total_queries: number;
}

export interface SectorResponse {
  sector_id: number;
  sector_name: string;
}

export interface CompanyResponse {
  company_id: number;
  company_name: string;
  industry_id: number;
}
