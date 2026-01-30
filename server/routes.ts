import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { startBot } from "./bot";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // API Routes for Dashboard
  app.get(api.stats.get.path, async (req, res) => {
    const totalUsers = await storage.getUserCount();
    const totalChannels = await storage.getChannelCount();
    const totalLinks = await storage.getActiveLinkCount();
    
    res.json({
      totalUsers,
      totalChannels,
      totalLinks,
      uptime: process.uptime()
    });
  });

  app.get(api.channels.list.path, async (req, res) => {
    const channels = await storage.getChannels();
    res.json(channels);
  });

  app.get(api.settings.list.path, async (req, res) => {
    // This is just a placeholder endpoint for settings
    const settings = await storage.getBotSettings();
    res.json(Object.values(settings));
  });

  // Start the Telegram Bot
  startBot().catch(console.error);

  return httpServer;
}
