import { useEffect, useState } from "react";
import { Navbar } from "../components/layout/Navbar";
import { AdminServices } from "../apis/service/admin/admin.service";
import { SuperAdminServices } from "../apis/service/admin/super.admin.service";
import type {
  AdminAnalyticsResponse,
  UserAdminResponse,
  ChatHistoryResponse,
} from "../apis/types";
import { Button } from "../components/ui";
import { useAppSelector } from "../store";
import {
  Trash2,
  Ban,
  CheckCircle,
  Search,
  MessageSquare,
  ChevronRight,
  Shield,
  BarChart3,
  Building2,
  UserCog,
} from "lucide-react";

type AdminDashboardMode = "admin" | "superadmin";

interface AdminDashboardProps {
  mode?: AdminDashboardMode;
}

export default function AdminDashboard({
  mode = "admin",
}: AdminDashboardProps) {
  const authUser = useAppSelector((state) => state.auth.user);
  const isSuperAdmin = mode === "superadmin" || authUser?.role === "superadmin";
  const [users, setUsers] = useState<UserAdminResponse[]>([]);
  const [chats, setChats] = useState<ChatHistoryResponse[]>([]);
  const [selectedChat, setSelectedChat] = useState<ChatHistoryResponse | null>(
    null,
  );
  const [analytics, setAnalytics] = useState<AdminAnalyticsResponse | null>(
    null,
  );
  const [admins, setAdmins] = useState<UserAdminResponse[]>([]);
  const [sectorName, setSectorName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [industryId, setIndustryId] = useState<number | "">("");
  const [formMessage, setFormMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersData, chatsData, analyticsData] = await Promise.all([
        AdminServices.getUsers(),
        AdminServices.getAllChats(),
        AdminServices.getAnalytics(),
      ]);
      setUsers(usersData);
      setChats(chatsData);
      setAnalytics(analyticsData);
      if (isSuperAdmin) {
        const adminsData = await SuperAdminServices.getAdmins();
        setAdmins(adminsData);
      }
    } catch (err) {
      setError("Failed to fetch admin data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (userId: string, currentStatus: string) => {
    const newStatus = currentStatus === "active" ? "banned" : "active";
    try {
      const success = await AdminServices.updateUserStatus(userId, newStatus);
      if (success) {
        setUsers(
          users.map((u) => (u.id === userId ? { ...u, status: newStatus } : u)),
        );
      }
    } catch (err) {
      alert("Failed to update user status");
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this user? This action cannot be undone.",
      )
    )
      return;
    try {
      const success = await AdminServices.deleteUser(userId);
      if (success) {
        setUsers(users.filter((u) => u.id !== userId));
      }
    } catch (err) {
      alert("Failed to delete user");
    }
  };

  const handleCreateSector = async () => {
    setFormMessage(null);
    try {
      const sector = await AdminServices.createSector(sectorName);
      setFormMessage(`Sector created: ${sector.sector_name}`);
      setSectorName("");
    } catch (err: any) {
      setFormMessage(err?.response?.data?.detail || "Failed to create sector");
    }
  };

  const handleCreateCompany = async () => {
    setFormMessage(null);
    if (!industryId) {
      setFormMessage("Industry ID is required.");
      return;
    }
    try {
      const company = await AdminServices.createCompany(
        companyName,
        Number(industryId),
      );
      setFormMessage(`Company created: ${company.company_name}`);
      setCompanyName("");
      setIndustryId("");
    } catch (err: any) {
      setFormMessage(err?.response?.data?.detail || "Failed to create company");
    }
  };

  const handleAdminRoleChange = async (userId: string, role: string) => {
    try {
      const success = await SuperAdminServices.updateUserRole(userId, role);
      if (success) {
        const refreshed = await SuperAdminServices.getAdmins();
        setAdmins(refreshed);
      }
    } catch (err) {
      alert("Failed to update admin role");
    }
  };

  if (loading)
    return (
      <div className="p-8 text-center dark:text-white">
        Loading Admin Dashboard...
      </div>
    );
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 p-4 sm:p-8">
      <Navbar
        title={
          isSuperAdmin ? "Super Admin Dashboard" : "Admin Dashboard"
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Analytics Section */}
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden">
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

        {/* User Management Section */}
        <div className="lg:col-span-2  bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
            <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
              <Search className="text-blue-500" size={20} />
              User Management
            </h2>
            <span className="text-sm text-gray-500 dark:text-zinc-400">
              {users.length} Users
            </span>
          </div>
          <div className="overflow-y-auto max-h-[calc(100vh-300px)]">
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
                        {isSuperAdmin &&
                          user.role !== "superadmin" && (
                            <Button
                              variant="outline"
                              size="icon"
                              onClick={() =>
                                handleAdminRoleChange(
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
                          onClick={() =>
                            handleToggleStatus(user.id, user.status)
                          }
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
                          onClick={() => handleDeleteUser(user.id)}
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

        {/* Data Management Section */}
        <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
            <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
              <Building2 className="text-amber-500" size={20} />
              Data Management
            </h2>
          </div>
          <div className="p-6 space-y-6">
            <div>
              <p className="text-sm font-semibold text-gray-700 dark:text-zinc-300">
                Create Sector
              </p>
              <div className="mt-3 flex flex-col sm:flex-row gap-3">
                <input
                  value={sectorName}
                  onChange={(e) => setSectorName(e.target.value)}
                  placeholder="Sector name"
                  className="flex-1 rounded-lg border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-2 text-sm text-gray-700 dark:text-zinc-200"
                />
                <Button onClick={handleCreateSector} disabled={!sectorName}>
                  Add Sector
                </Button>
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-700 dark:text-zinc-300">
                Create Company
              </p>
              <div className="mt-3 grid grid-cols-1 sm:grid-cols-[1fr,150px,auto] gap-3">
                <input
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Company name"
                  className="rounded-lg border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-2 text-sm text-gray-700 dark:text-zinc-200"
                />
                <input
                  type="number"
                  min={1}
                  value={industryId}
                  onChange={(e) =>
                    setIndustryId(e.target.value ? Number(e.target.value) : "")
                  }
                  placeholder="Industry ID"
                  className="rounded-lg border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-2 text-sm text-gray-700 dark:text-zinc-200"
                />
                <Button
                  onClick={handleCreateCompany}
                  disabled={!companyName || !industryId}
                >
                  Add Company
                </Button>
              </div>
            </div>
            {formMessage && (
              <p className="text-sm text-indigo-500">{formMessage}</p>
            )}
          </div>
        </div>

        {/* Human Queries Section */}
        <div className="grid grid-rows-[1fr,auto] gap-6 max-h-[calc(100vh-200px)]">
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
              <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
                <MessageSquare className="text-indigo-500" size={20} />
                Human Queries
              </h2>
              <span className="text-sm text-gray-500 dark:text-zinc-400">
                {chats.length} Queries
              </span>
            </div>
            <div className="overflow-y-auto flex-1">
              <div className="divide-y divide-gray-200 dark:divide-zinc-800">
                {chats.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => setSelectedChat(chat)}
                    className={`w-full text-left p-4 hover:bg-gray-50 dark:hover:bg-zinc-800/30 transition-all flex items-start justify-between group ${
                      selectedChat?.id === chat.id
                        ? "bg-indigo-50/50 dark:bg-indigo-900/10 border-l-4 border-indigo-500"
                        : "border-l-4 border-transparent"
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-zinc-200 line-clamp-1">
                        {chat.human_query}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-zinc-500 mt-1">
                        {new Date(chat.created_at).toLocaleString()}
                      </p>
                    </div>
                    <ChevronRight
                      className={`text-gray-400 group-hover:translate-x-1 transition-transform ${selectedChat?.id === chat.id ? "text-indigo-500 translate-x-1" : ""}`}
                      size={16}
                    />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* AI Query Detail Display */}
          <div
            className={`bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden transition-all duration-300 ${selectedChat ? "opacity-100 translate-y-0" : "opacity-50 translate-y-4 pointer-events-none"}`}
          >
            <div className="p-6">
              <h3 className="text-lg font-bold dark:text-white mb-4 flex items-center gap-2">
                <div className="w-2 h-6 bg-indigo-500 rounded-full"></div>
                Generated AI Query
              </h3>
              {selectedChat ? (
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 dark:bg-zinc-800 rounded-lg border border-gray-200 dark:border-zinc-700">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                      Human Question
                    </p>
                    <p className="text-sm text-gray-700 dark:text-zinc-300 italic">
                      "{selectedChat.human_query}"
                    </p>
                  </div>
                  <div className="p-4 bg-zinc-900 dark:bg-black rounded-lg border border-zinc-700 overflow-x-auto">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">
                      Generated SQL
                    </p>
                    <pre className="text-sm text-emerald-400 font-mono leading-relaxed">
                      {selectedChat.sql_generated || "-- No SQL generated"}
                    </pre>
                  </div>
                  {selectedChat.result_summary && (
                    <div className="p-4 bg-gray-50 dark:bg-zinc-800 rounded-lg border border-gray-200 dark:border-zinc-700">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                        Summary Result
                      </p>
                      <p className="text-sm text-gray-700 dark:text-zinc-300">
                        {selectedChat.result_summary}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-12 flex flex-col items-center justify-center text-gray-400 dark:text-zinc-600">
                  <MessageSquare
                    size={48}
                    strokeWidth={1}
                    className="mb-4 opacity-20"
                  />
                  <p>Select a query to see the details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {isSuperAdmin && (
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
                        onClick={() => handleAdminRoleChange(admin.id, "user")}
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
      )}
    </div>
  );
}
