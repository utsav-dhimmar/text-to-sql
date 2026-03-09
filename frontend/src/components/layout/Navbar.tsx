import {
    Moon,
    Sun,
    User as UserIcon,
    ArrowLeft,
    Shield,
    MessageSquare,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "../ui";
import { useAppDispatch, useAppSelector } from "../../store";
import { toggleTheme } from "../../store/slices/themeSlice";
import { logout } from "../../store/slices/authSlice";
import { AuthService } from "../../apis/service/auth.service";

interface NavbarProps {
    title: string;
    showBackButton?: boolean;
    titleRight?: React.ReactNode;
}

export function Navbar({ title, showBackButton, titleRight }: NavbarProps) {
    const { theme } = useAppSelector((state) => state.theme);
    const { user } = useAppSelector((state) => state.auth);
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

    const isAdmin = user?.role === "admin" || user?.role === "superadmin";

    return (
        <div className="flex justify-between items-center mb-8 flex-wrap gap-4">
            <div className="flex items-center gap-4">
                {showBackButton && (
                    <Button
                        onClick={() => navigate(-1)}
                        variant="outline"
                        size="icon"
                        className="rounded-full"
                        fullWidth={false}
                    >
                        <ArrowLeft size={20} />
                    </Button>
                )}
                <h1 className="text-2xl sm:text-3xl font-bold dark:text-white">{title}</h1>
                {titleRight}
            </div>
            <div className="flex gap-4 items-center">
                {isAdmin && (
                    <Button
                        onClick={() => navigate("/")}
                        variant="outline"
                        fullWidth={false}
                        className="flex items-center gap-2 border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-900/10 text-emerald-600 dark:text-emerald-400"
                    >
                        <MessageSquare size={18} />
                        <span className="hidden sm:inline">Chat</span>
                    </Button>
                )}
                <Button
                    onClick={handleToggleTheme}
                    variant="outline"
                    fullWidth={false}
                    className="flex items-center gap-2"
                >
                    {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
                    <span className="hidden sm:inline">Theme</span>
                </Button>
                {isAdmin && (
                    <Button
                        onClick={() => navigate("/admin")}
                        variant="outline"
                        fullWidth={false}
                        className="flex items-center gap-2 border-indigo-200 dark:border-indigo-900 bg-indigo-50/50 dark:bg-indigo-900/10 text-indigo-600 dark:text-indigo-400"
                    >
                        <Shield size={18} />
                        <span className="hidden sm:inline">Admin</span>
                    </Button>
                )}
                <Button
                    onClick={() => navigate("/profile")}
                    variant="outline"
                    fullWidth={false}
                    className="flex items-center gap-2"
                >
                    <UserIcon size={18} />
                    <span className="hidden sm:inline">Profile</span>
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
    );
}
