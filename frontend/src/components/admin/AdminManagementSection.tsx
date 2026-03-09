import { UserCog } from "lucide-react";
import type { UserAdminResponse } from "../../apis/types";
import { Button } from "../ui";

interface AdminManagementSectionProps {
  admins: UserAdminResponse[];
  onAdminRoleChange: (userId: string, role: string) => void;
}

export function AdminManagementSection({
  admins,
  onAdminRoleChange,
}: AdminManagementSectionProps) {
  return (
    <div className="mt-8 bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
        <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
          <UserCog className="text-rose-500" size={20} />
          Admin Management
        </h2>
        <span className="text-sm text-gray-500 dark:text-zinc-400">
          {admins.length} Admins
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 dark:bg-zinc-800/50">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 dark:text-zinc-400 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 dark:text-zinc-400 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 dark:text-zinc-400 uppercase tracking-wider text-right">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-zinc-800">
            {admins.map((admin) => (
              <tr key={admin.id}>
                <td className="px-6 py-4 dark:text-zinc-300 font-medium">
                  {admin.email}
                </td>
                <td className="px-6 py-4">
                  <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                    {admin.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onAdminRoleChange(admin.id, "user")}
                    className="rounded-lg"
                  >
                    Demote to User
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
