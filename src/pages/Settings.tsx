import { useSettings } from "@/hooks/use-dashboard";
import { Layout } from "@/components/Layout";
import { Settings as SettingsIcon, Image as ImageIcon, MessageSquare, Link as LinkIcon } from "lucide-react";
import { motion } from "framer-motion";

export default function Settings() {
  const { data: settings, isLoading } = useSettings();

  const getIcon = (key: string) => {
    if (key.includes('image')) return ImageIcon;
    if (key.includes('text') || key.includes('caption')) return MessageSquare;
    return SettingsIcon;
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold font-display">Bot Settings</h2>
          <p className="text-muted-foreground mt-1">
            Current configuration values. Manage these via the bot admin panel.
          </p>
        </div>

        {isLoading ? (
          <div className="space-y-4">
             {[1, 2, 3, 4].map(i => (
               <div key={i} className="h-20 bg-card border border-border rounded-xl animate-pulse" />
             ))}
          </div>
        ) : (
          <div className="grid gap-4">
            {settings?.map((setting, index) => {
              const Icon = getIcon(setting.key);
              // Safe parsing of JSON value
              const displayValue = typeof setting.value === 'object' 
                ? JSON.stringify(setting.value, null, 2)
                : String(setting.value);

              return (
                <motion.div
                  key={setting.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="bg-card border border-border rounded-xl p-5 flex items-start gap-4 hover:border-primary/50 transition-colors"
                >
                  <div className="p-3 rounded-lg bg-secondary">
                    <Icon className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-foreground capitalize">
                        {setting.key.replace(/_/g, ' ')}
                      </h4>
                      <span className="text-xs text-muted-foreground font-mono px-2 py-1 bg-secondary rounded">
                        {setting.key}
                      </span>
                    </div>
                    <pre className="text-sm text-muted-foreground font-mono bg-black/20 p-3 rounded-lg overflow-x-auto">
                      {displayValue}
                    </pre>
                  </div>
                </motion.div>
              );
            })}

            {(!settings || settings.length === 0) && (
              <div className="py-12 text-center border-2 border-dashed border-border rounded-2xl bg-card/50">
                <SettingsIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-20" />
                <h3 className="text-lg font-medium">No custom settings</h3>
                <p className="text-muted-foreground mt-2">
                  Default values are currently being used.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
