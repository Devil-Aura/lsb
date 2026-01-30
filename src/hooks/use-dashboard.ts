import { useQuery } from "@tanstack/react-query";
import { api, type StatsResponse } from "@shared/routes";
import { channels as channelsSchema, botSettings as settingsSchema } from "@shared/schema";

export function useStats() {
  return useQuery({
    queryKey: [api.stats.get.path],
    queryFn: async () => {
      const res = await fetch(api.stats.get.path);
      if (!res.ok) throw new Error("Failed to fetch stats");
      return api.stats.get.responses[200].parse(await res.json());
    },
    refetchInterval: 30000, // Refresh every 30s
  });
}

export function useChannels() {
  return useQuery({
    queryKey: [api.channels.list.path],
    queryFn: async () => {
      const res = await fetch(api.channels.list.path);
      if (!res.ok) throw new Error("Failed to fetch channels");
      return api.channels.list.responses[200].parse(await res.json());
    },
  });
}

export function useSettings() {
  return useQuery({
    queryKey: [api.settings.list.path],
    queryFn: async () => {
      const res = await fetch(api.settings.list.path);
      if (!res.ok) throw new Error("Failed to fetch settings");
      return api.settings.list.responses[200].parse(await res.json());
    },
  });
}
