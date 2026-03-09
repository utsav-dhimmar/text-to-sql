import { Moon, Sun, User as UserIcon, ArrowLeft } from "lucide-react";
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
                <Button
                    onClick={handleToggleTheme}
                    variant="outline"
                    fullWidth={false}
                    className="flex items-center gap-2"
                >
                    {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
                    <span className="hidden sm:inline">Theme</span>
                </Button>
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
