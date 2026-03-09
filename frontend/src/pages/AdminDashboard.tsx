import { useEffect, useState } from "react";
import { Navbar } from "../components/layout/Navbar";
import { AdminServices } from "../apis/service/admin/admin.service";
import { SuperAdminServices } from "../apis/service/admin/super.admin.service";
import type {
  AdminAnalyticsResponse,
  UserAdminResponse,
  ChatHistoryResponse,
} from "../apis/types";
import { useAppSelector } from "../store";
import { AdminAnalyticsSection } from "../components/admin/AdminAnalyticsSection";
import { UserManagementSection } from "../components/admin/UserManagementSection";
import { DataManagementSection } from "../components/admin/DataManagementSection";
import { HumanQueriesSection } from "../components/admin/HumanQueriesSection";
import { AdminManagementSection } from "../components/admin/AdminManagementSection";

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

      <div className="grid grid-cols-1 gap-8">
        {/* Analytics Section */}
        <AdminAnalyticsSection
          analytics={analytics}
          isSuperAdmin={isSuperAdmin}
        />

        {/* User Management Section */}
        <UserManagementSection
          users={users}
          isSuperAdmin={isSuperAdmin}
          onToggleStatus={handleToggleStatus}
          onDeleteUser={handleDeleteUser}
          onAdminRoleChange={handleAdminRoleChange}
        />

        {/* Data Management Section (Super Admin Only) */}
        {isSuperAdmin && (
          <DataManagementSection
            sectorName={sectorName}
            companyName={companyName}
            industryId={industryId}
            formMessage={formMessage}
            onSectorNameChange={setSectorName}
            onCompanyNameChange={setCompanyName}
            onIndustryIdChange={setIndustryId}
            onCreateSector={handleCreateSector}
            onCreateCompany={handleCreateCompany}
          />
        )}

        {/* Human Queries Section */}
        <HumanQueriesSection
          chats={chats}
          selectedChat={selectedChat}
          onSelectChat={setSelectedChat}
        />
      </div>

      {isSuperAdmin && (
        <AdminManagementSection
          admins={admins}
          onAdminRoleChange={handleAdminRoleChange}
        />
      )}
    </div>
  );
}
