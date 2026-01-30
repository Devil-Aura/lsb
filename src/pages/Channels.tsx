import { useChannels } from "@/hooks/use-dashboard";
import { Layout } from "@/components/Layout";
import { Radio, ExternalLink, ShieldCheck, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";

export default function Channels() {
  const { data: channels, isLoading } = useChannels();

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold font-display">Connected Channels</h2>
          <p className="text-muted-foreground mt-1">Manage the Telegram channels connected to your bot.</p>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-card border border-border rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {channels?.map((channel, index) => (
              <motion.div
                key={channel.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="group bg-card hover:bg-muted/30 border border-border rounded-2xl p-6 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-1"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-300">
                    <Radio className="w-6 h-6" />
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium border ${
                    channel.hasInvitePermission 
                      ? "bg-green-500/10 text-green-500 border-green-500/20" 
                      : "bg-red-500/10 text-red-500 border-red-500/20"
                  }`}>
                    {channel.hasInvitePermission ? "Active" : "No Permission"}
                  </div>
                </div>

                <h3 className="font-bold text-lg mb-1">{channel.name}</h3>
                <p className="text-sm text-muted-foreground font-mono mb-6">
                  ID: {channel.telegramChannelId}
                </p>

                <div className="flex flex-col gap-2">
                  <div className="flex items-center text-sm text-muted-foreground">
                    {channel.hasInvitePermission ? (
                      <ShieldCheck className="w-4 h-4 mr-2 text-green-500" />
                    ) : (
                      <ShieldAlert className="w-4 h-4 mr-2 text-red-500" />
                    )}
                    <span>Admin Rights Verified</span>
                  </div>
                  
                  {channel.primaryLink && (
                    <a 
                      href={channel.primaryLink} 
                      target="_blank" 
                      rel="noreferrer"
                      className="mt-2 text-sm text-primary hover:underline flex items-center"
                    >
                      View Channel <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  )}
                </div>
              </motion.div>
            ))}

            {(!channels || channels.length === 0) && (
              <div className="col-span-full py-12 text-center border-2 border-dashed border-border rounded-2xl bg-card/50">
                <Radio className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-20" />
                <h3 className="text-lg font-medium">No channels found</h3>
                <p className="text-muted-foreground max-w-sm mx-auto mt-2">
                  Add channels using the Telegram bot commands to see them here.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
