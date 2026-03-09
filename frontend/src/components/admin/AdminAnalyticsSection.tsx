import { BarChart3, Shield } from "lucide-react";
import type { AdminAnalyticsResponse } from "../../apis/types";

interface AdminAnalyticsSectionProps {
  analytics: AdminAnalyticsResponse | null;
  isSuperAdmin: boolean;
}

export function AdminAnalyticsSection({
  analytics,
  isSuperAdmin,
}: AdminAnalyticsSectionProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
        <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
          <BarChart3 className="text-emerald-500" size={20} />
          Platform Analytics
        </h2>
        {isSuperAdmin && (
          <span className="text-xs font-semibold uppercase tracking-wider text-red-500 flex items-center gap-2">
            <Shield size={14} />
            Super Admin
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-6">
        {[
          { label: "Total Users", value: analytics?.total_users ?? 0 },
          { label: "Active Users", value: analytics?.active_users ?? 0 },
          { label: "Banned Users", value: analytics?.banned_users ?? 0 },
          { label: "Total Admins", value: analytics?.total_admins ?? 0 },
          { label: "Total Queries", value: analytics?.total_queries ?? 0 },
        ].map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-gray-200 dark:border-zinc-800 p-4 bg-white/70 dark:bg-zinc-950/40"
          >
            <p className="text-xs uppercase tracking-widest text-gray-500 dark:text-zinc-500">
              {metric.label}
            </p>
            <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-zinc-100">
              {metric.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
