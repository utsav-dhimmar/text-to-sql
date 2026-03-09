import { Ban, CheckCircle, Search, Trash2, UserCog } from "lucide-react";
import type { UserAdminResponse } from "../../apis/types";
import { Button } from "../ui";

interface UserManagementSectionProps {
  users: UserAdminResponse[];
  isSuperAdmin: boolean;
  onToggleStatus: (userId: string, currentStatus: string) => void;
  onDeleteUser: (userId: string) => void;
  onAdminRoleChange: (userId: string, role: string) => void;
}

export function UserManagementSection({
  users,
  isSuperAdmin,
  onToggleStatus,
  onDeleteUser,
  onAdminRoleChange,
}: UserManagementSectionProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden flex flex-col">
      <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
        <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
          <Search className="text-blue-500" size={20} />
          User Management
        </h2>
        <span className="text-sm text-gray-500 dark:text-zinc-400">
          {users.length} Users
        </span>
      </div>
      <div className="overflow-y-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 dark:bg-zinc-800/50 sticky top-0 z-10">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 dark:text-zinc-400 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 dark:text-zinc-400 uppercase tracking-wider">
                Role
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
            {users.map((user) => (
              <tr
                key={user.id}
                className="hover:bg-gray-50 dark:hover:bg-zinc-800/30 transition-colors"
              >
                <td className="px-6 py-4 dark:text-zinc-300 font-medium truncate max-w-[150px]">
                  {user.email}
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`px-2 py-1 rounded-md text-xs font-medium ${
                      user.role === "admin"
                        ? "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
                        : user.role === "superadmin"
                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                          : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                    }`}
                  >
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`flex items-center gap-1.5 text-xs font-medium ${
                      user.status === "active"
                        ? "text-green-600 dark:text-green-400"
                        : "text-red-600 dark:text-red-400"
                    }`}
                  >
                    {user.status === "active" ? (
                      <CheckCircle size={14} />
                    ) : (
                      <Ban size={14} />
                    )}
                    {user.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    {isSuperAdmin && user.role !== "superadmin" && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() =>
                          onAdminRoleChange(
                            user.id,
                            user.role === "admin" ? "user" : "admin",
                          )
                        }
                        title={
                          user.role === "admin"
                            ? "Demote to User"
                            : "Promote to Admin"
                        }
                        className="h-8 w-8 rounded-lg"
                      >
                        <UserCog size={14} className="text-slate-500" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => onToggleStatus(user.id, user.status)}
                      title={
                        user.status === "active" ? "Ban User" : "Unban User"
                      }
                      className="h-8 w-8 rounded-lg"
                    >
                      {user.status === "active" ? (
                        <Ban size={14} className="text-orange-500" />
                      ) : (
                        <CheckCircle size={14} className="text-green-500" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => onDeleteUser(user.id)}
                      title="Delete User"
                      className="h-8 w-8 rounded-lg hover:bg-red-50 hover:border-red-200 dark:hover:bg-red-900/20 dark:hover:border-red-800"
                    >
                      <Trash2 size={14} className="text-red-500" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
