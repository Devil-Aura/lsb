import { db } from "./db";
import {
  users, admins, channels, links, botSettings, broadcasts,
  type User, type InsertUser,
  type Admin, type InsertAdmin,
  type Channel, type InsertChannel,
  type Link, type InsertLink,
  type BotSetting, type InsertBotSetting
} from "@shared/schema";
import { eq, sql, desc, and, gt } from "drizzle-orm";

export interface IStorage {
  // Users
  getUser(telegramId: number): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(telegramId: number, user: Partial<InsertUser>): Promise<User>;
  getAllUsers(): Promise<User[]>; // For broadcast
  getUserCount(): Promise<number>;

  // Admins
  getAdmin(telegramId: number): Promise<Admin | undefined>;
  addAdmin(admin: InsertAdmin): Promise<Admin>;
  removeAdmin(telegramId: number): Promise<void>;
  getAllAdmins(): Promise<Admin[]>;

  // Channels
  createChannel(channel: InsertChannel): Promise<Channel>;
  getChannels(): Promise<Channel[]>;
  getChannelById(id: number): Promise<Channel | undefined>;
  getChannelByTelegramId(telegramId: number): Promise<Channel | undefined>;
  getChannelByName(name: string): Promise<Channel | undefined>;
  searchChannels(query: string): Promise<Channel[]>;
  deleteChannel(id: number): Promise<void>;
  getChannelCount(): Promise<number>;

  // Links
  createLink(link: InsertLink): Promise<Link>;
  getLinkByToken(token: string): Promise<Link | undefined>;
  revokeLink(token: string): Promise<void>;
  getActiveLinkCount(): Promise<number>;

  // Settings
  getBotSettings(): Promise<Record<string, any>>;
  updateBotSetting(key: string, value: any): Promise<BotSetting>;
  getSetting(key: string): Promise<any>;

  // Broadcasts (optional, mainly for stats)
  logBroadcast(type: string, content: any): Promise<void>;
}

export class DatabaseStorage implements IStorage {
  async getUser(telegramId: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.telegramId, telegramId));
    return user;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }

  async updateUser(telegramId: number, updates: Partial<InsertUser>): Promise<User> {
    const [user] = await db.update(users)
      .set(updates)
      .where(eq(users.telegramId, telegramId))
      .returning();
    return user;
  }

  async getAllUsers(): Promise<User[]> {
    return await db.select().from(users);
  }

  async getUserCount(): Promise<number> {
    const [result] = await db.select({ count: sql<number>`count(*)` }).from(users);
    return Number(result.count);
  }

  // Admins
  async getAdmin(telegramId: number): Promise<Admin | undefined> {
    const [admin] = await db.select().from(admins).where(eq(admins.telegramId, telegramId));
    return admin;
  }

  async addAdmin(insertAdmin: InsertAdmin): Promise<Admin> {
    const [admin] = await db.insert(admins).values(insertAdmin).returning();
    return admin;
  }

  async removeAdmin(telegramId: number): Promise<void> {
    await db.delete(admins).where(eq(admins.telegramId, telegramId));
  }

  async getAllAdmins(): Promise<Admin[]> {
    return await db.select().from(admins);
  }

  // Channels
  async createChannel(insertChannel: InsertChannel): Promise<Channel> {
    const [channel] = await db.insert(channels).values(insertChannel).returning();
    return channel;
  }

  async getChannels(): Promise<Channel[]> {
    return await db.select().from(channels).orderBy(desc(channels.addedAt));
  }

  async getChannelById(id: number): Promise<Channel | undefined> {
    const [channel] = await db.select().from(channels).where(eq(channels.id, id));
    return channel;
  }

  async getChannelByTelegramId(telegramId: number): Promise<Channel | undefined> {
    const [channel] = await db.select().from(channels).where(eq(channels.telegramChannelId, telegramId));
    return channel;
  }

  async getChannelByName(name: string): Promise<Channel | undefined> {
    // Exact match case insensitive
    const [channel] = await db.select().from(channels)
      .where(sql`lower(${channels.name}) = lower(${name})`);
    return channel;
  }

  async searchChannels(query: string): Promise<Channel[]> {
    return await db.select().from(channels)
      .where(sql`lower(${channels.name}) LIKE lower(${`%${query}%`})`);
  }

  async deleteChannel(id: number): Promise<void> {
    await db.delete(channels).where(eq(channels.id, id));
  }

  async getChannelCount(): Promise<number> {
    const [result] = await db.select({ count: sql<number>`count(*)` }).from(channels);
    return Number(result.count);
  }

  // Links
  async createLink(insertLink: InsertLink): Promise<Link> {
    const [link] = await db.insert(links).values(insertLink).returning();
    return link;
  }

  async getLinkByToken(token: string): Promise<Link | undefined> {
    const [link] = await db.select().from(links).where(eq(links.token, token));
    return link;
  }

  async revokeLink(token: string): Promise<void> {
    await db.update(links).set({ isRevoked: true }).where(eq(links.token, token));
  }

  async getActiveLinkCount(): Promise<number> {
    const [result] = await db.select({ count: sql<number>`count(*)` }).from(links)
      .where(eq(links.isRevoked, false));
    return Number(result.count);
  }

  // Settings
  async getBotSettings(): Promise<Record<string, any>> {
    const allSettings = await db.select().from(botSettings);
    const settingsMap: Record<string, any> = {};
    for (const s of allSettings) {
      settingsMap[s.key] = s.value;
    }
    return settingsMap;
  }

  async updateBotSetting(key: string, value: any): Promise<BotSetting> {
    // Check if exists
    const [existing] = await db.select().from(botSettings).where(eq(botSettings.key, key));
    if (existing) {
      const [updated] = await db.update(botSettings)
        .set({ value, updatedAt: new Date() })
        .where(eq(botSettings.key, key))
        .returning();
      return updated;
    } else {
      const [inserted] = await db.insert(botSettings)
        .values({ key, value })
        .returning();
      return inserted;
    }
  }

  async getSetting(key: string): Promise<any> {
    const [setting] = await db.select().from(botSettings).where(eq(botSettings.key, key));
    return setting?.value;
  }

  async logBroadcast(type: string, content: any): Promise<void> {
    await db.insert(broadcasts).values({ type, content, duration: null });
  }
}

export const storage = new DatabaseStorage();
