import { useStats } from "@/hooks/use-dashboard";
import { Layout } from "@/components/Layout";
import { StatCard } from "@/components/StatCard";
import { Users, Link2, Radio, Clock, Activity, ArrowUpRight } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

const mockChartData = [
  { name: 'Mon', links: 400 },
  { name: 'Tue', links: 300 },
  { name: 'Wed', links: 550 },
  { name: 'Thu', links: 450 },
  { name: 'Fri', links: 600 },
  { name: 'Sat', links: 800 },
  { name: 'Sun', links: 750 },
];

export default function Dashboard() {
  const { data: stats, isLoading } = useStats();

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const days = Math.floor(hours / 24);
    return days > 0 ? `${days}d ${hours % 24}h` : `${hours}h`;
  };

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <motion.h2 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl font-bold font-display"
            >
              Overview
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-muted-foreground mt-1"
            >
              Monitor your bot's performance and statistics
            </motion.p>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-sm font-medium text-green-500">Live Updates</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={isLoading ? "..." : stats?.totalUsers.toLocaleString() || "0"}
            icon={Users}
            delay={0}
          />
          <StatCard
            title="Active Links"
            value={isLoading ? "..." : stats?.totalLinks.toLocaleString() || "0"}
            icon={Link2}
            trend="+12%"
            trendUp={true}
            delay={1}
          />
          <StatCard
            title="Channels"
            value={isLoading ? "..." : stats?.totalChannels.toLocaleString() || "0"}
            icon={Radio}
            delay={2}
          />
          <StatCard
            title="System Uptime"
            value={isLoading ? "..." : formatUptime(stats?.uptime || 0)}
            icon={Clock}
            delay={3}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2 bg-card border border-border rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="font-bold text-lg">Link Generation Activity</h3>
                <p className="text-sm text-muted-foreground">Links generated over the last 7 days</p>
              </div>
              <div className="p-2 bg-secondary rounded-lg">
                <Activity className="w-5 h-5 text-muted-foreground" />
              </div>
            </div>
            
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockChartData}>
                  <XAxis 
                    dataKey="name" 
                    stroke="#52525b" 
                    fontSize={12} 
                    tickLine={false} 
                    axisLine={false} 
                  />
                  <YAxis 
                    stroke="#52525b" 
                    fontSize={12} 
                    tickLine={false} 
                    axisLine={false} 
                    tickFormatter={(value) => `${value}`} 
                  />
                  <Tooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ backgroundColor: '#09090b', border: '1px solid #27272a', borderRadius: '8px' }}
                  />
                  <Bar 
                    dataKey="links" 
                    fill="#3b82f6" 
                    radius={[4, 4, 0, 0]} 
                    barSize={40}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-br from-blue-600 to-purple-700 rounded-2xl p-6 text-white relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-white/10 blur-3xl pointer-events-none"></div>
            
            <h3 className="text-xl font-bold mb-2 relative z-10">Quick Actions</h3>
            <p className="text-blue-100 text-sm mb-6 relative z-10">
              Manage your bot directly from the dashboard.
            </p>

            <div className="space-y-3 relative z-10">
              <button className="w-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/10 rounded-xl p-3 text-left transition-colors flex items-center justify-between group">
                <span className="font-medium">Broadcast Message</span>
                <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
              <button className="w-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/10 rounded-xl p-3 text-left transition-colors flex items-center justify-between group">
                <span className="font-medium">Add New Channel</span>
                <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
              <button className="w-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/10 rounded-xl p-3 text-left transition-colors flex items-center justify-between group">
                <span className="font-medium">Bot Settings</span>
                <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
}
