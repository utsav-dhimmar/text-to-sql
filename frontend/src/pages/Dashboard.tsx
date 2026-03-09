import { Moon, Sun, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AuthService } from "../apis/service/auth.service";
import { ChatBox } from "../components/chat/ChatBox";
import { Button } from "../components/ui";
import { useAppDispatch, useAppSelector } from "../store";
import { logout } from "../store/slices/authSlice";
import { toggleTheme } from "../store/slices/themeSlice";

export default function Dashboard() {
  const { theme } = useAppSelector(state => state.theme);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await AuthService.logout();
    } catch (err) {
      console.error("Logout failed:", err);
    } finally {
      dispatch(logout());
      navigate("/login");
    }
  };

  const handleToggleTheme = () => {
    dispatch(toggleTheme());
  };

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto dark:bg-gray-950 dark:text-white transition-colors">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex gap-4">
          <Button
            onClick={handleToggleTheme}
            variant="outline"
            size="icon"
            fullWidth={false}
          >
            {theme === "light" ? (
              <Moon size={20} />
            ) : (
              <Sun size={20} />
            )}
          </Button>
          <Button
            onClick={() => navigate("/profile")}
            variant="outline"
            fullWidth={false}
            className="flex items-center gap-2"
          >
            <User size={18} />
            Profile
          </Button>
          <Button
            onClick={handleLogout}
            variant="outline"
            fullWidth={false}
          >
            Logout
          </Button>
        </div>
      </div>

      {/*<div className="bg-white dark:bg-gray-900 shadow rounded-lg p-6 border dark:border-gray-800">
        <h2 className="text-xl font-semibold mb-4">User Profile</h2>
        {user ? (
          <div className="space-y-2">
            <p>
              <span className="font-medium">Email:</span> {user.email}
            </p>
            <p>
              <span className="font-medium">Role:</span> {user.role}
            </p>
            <p>
              <span className="font-medium">Status:</span> {user.status}
            </p>
            <p>
              <span className="font-medium">ID:</span> {user.id}
            </p>
          </div>
        ) : (
          <p>No user data found.</p>
        )}
      </div>*/}

      <ChatBox />
    </div>
  );
}
