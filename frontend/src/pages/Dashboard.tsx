import { ChatBox } from "../components/chat/ChatBox";
import { Navbar } from "../components/layout/Navbar";

export default function Dashboard() {
  return (
    <div className="min-h-screen p-8  mx-auto dark:bg-gray-950 dark:text-white transition-colors">
      <Navbar title="Dashboard" />

      <ChatBox />
    </div>
  );
}
