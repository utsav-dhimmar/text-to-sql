import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui";
import { useAppDispatch, useAppSelector } from "../store";
import { setUser } from "../store/slices/authSlice";
import { AuthService } from "../apis/service/auth.service";
import { ArrowLeft, User, Mail, Shield, CheckCircle, Loader2 } from "lucide-react";

export default function ProfilePage() {
  const { user } = useAppSelector((state) => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setIsRefreshing(true);
        const userData = await AuthService.getMe();
        dispatch(setUser(userData));
      } catch (error) {
        console.error("Failed to refresh user data:", error);
      } finally {
        setIsRefreshing(false);
      }
    };

    fetchUserData();
  }, [dispatch]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 sm:p-8 transition-colors">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              onClick={() => navigate("/")}
              variant="outline"
              size="icon"
              className="rounded-full"
              fullWidth={false}
            >
              <ArrowLeft size={20} />
            </Button>
            <h1 className="text-3xl font-bold dark:text-white">Profile</h1>
          </div>
          {isRefreshing && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="animate-spin" size={16} />
              Refreshing...
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-gray-900 shadow-sm border dark:border-gray-800 rounded-2xl overflow-hidden transition-colors">
          <div className="h-32 bg-gradient-to-r from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700"></div>
          
          <div className="px-6 pb-8">
            <div className="relative -mt-12 mb-6">
              <div className="inline-flex items-center justify-center p-1 bg-white dark:bg-gray-900 rounded-full border-4 border-white dark:border-gray-900 shadow-sm">
                <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center text-gray-400">
                  <User size={48} />
                </div>
              </div>
            </div>

            {user ? (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold dark:text-white mb-1">
                    User Information
                  </h2>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Manage your account details and preferences.
                  </p>
                </div>

                <div className="grid gap-4">
                  <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border dark:border-gray-700 transition-colors">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg mr-4">
                      <Mail size={20} />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Email Address
                      </p>
                      <p className="text-base font-semibold dark:text-gray-200">
                        {user.email}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border dark:border-gray-700 transition-colors">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg mr-4">
                      <Shield size={20} />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Account Role
                      </p>
                      <p className="text-base font-semibold dark:text-gray-200 capitalize">
                        {user.role}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border dark:border-gray-700 transition-colors">
                    <div className="p-2 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg mr-4">
                      <CheckCircle size={20} />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Account Status
                      </p>
                      <p className="text-base font-semibold dark:text-gray-200 capitalize">
                        {user.status}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border dark:border-gray-700 transition-colors">
                    <div className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg mr-4">
                      <Shield size={20} />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        User ID
                      </p>
                      <p className="text-xs font-mono dark:text-gray-200">
                        {user.id}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  No user information available. Please log in again.
                </p>
                <Button 
                  onClick={() => navigate("/login")} 
                  className="mt-4"
                  fullWidth={false}
                >
                  Go to Login
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
