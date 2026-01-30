import { pgTable, text, serial, integer, boolean, timestamp, jsonb, bigint } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === TABLE DEFINITIONS ===

// Users table (for stats and broadcasts)
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  telegramId: bigint("telegram_id", { mode: "number" }).notNull().unique(),
  username: text("username"),
  firstName: text("first_name"),
  lastName: text("last_name"),
  joinedAt: timestamp("joined_at").defaultNow(),
});

// Admins table
export const admins = pgTable("admins", {
  id: serial("id").primaryKey(),
  telegramId: bigint("telegram_id", { mode: "number" }).notNull().unique(),
  username: text("username"),
  name: text("name"),
  addedAt: timestamp("added_at").defaultNow(),
});

// Channels table
export const channels = pgTable("channels", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(), // Anime Name
  telegramChannelId: bigint("telegram_channel_id", { mode: "number" }).notNull().unique(),
  primaryLink: text("primary_link"), // Permanent link
  hasInvitePermission: boolean("has_invite_permission").default(false),
  addedAt: timestamp("added_at").defaultNow(),
});

// Links table (for generated token links)
export const links = pgTable("links", {
  id: serial("id").primaryKey(),
  token: text("token").notNull().unique(),
  type: text("type").notNull(), // 'request' or 'direct'
  channelId: integer("channel_id").references(() => channels.id),
  generatedLink: text("generated_link"), // The actual telegram invite link
  createdAt: timestamp("created_at").defaultNow(),
  expiresAt: timestamp("expires_at"), // When the generated link should be revoked
  isRevoked: boolean("is_revoked").default(false),
});

// Bot Settings (for customization)
export const botSettings = pgTable("bot_settings", {
  id: serial("id").primaryKey(),
  key: text("key").notNull().unique(), // e.g., 'start_image', 'caption', 'button_text'
  value: jsonb("value").notNull(), // Stores structure like { url: '...', text: '...' }
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Broadcasts (optional log)
export const broadcasts = pgTable("broadcasts", {
  id: serial("id").primaryKey(),
  content: jsonb("content").notNull(),
  type: text("type").notNull(), // 'normal', 'pin', 'temp'
  duration: text("duration"), // for temp broadcasts
  createdAt: timestamp("created_at").defaultNow(),
});

// === RELATIONS ===
export const linksRelations = relations(links, ({ one }) => ({
  channel: one(channels, {
    fields: [links.channelId],
    references: [channels.id],
  }),
}));

// === SCHEMAS ===
export const insertUserSchema = createInsertSchema(users).omit({ id: true, joinedAt: true });
export const insertAdminSchema = createInsertSchema(admins).omit({ id: true, addedAt: true });
export const insertChannelSchema = createInsertSchema(channels).omit({ id: true, addedAt: true });
export const insertLinkSchema = createInsertSchema(links).omit({ id: true, createdAt: true });
export const insertBotSettingSchema = createInsertSchema(botSettings).omit({ id: true, updatedAt: true });

// === TYPES ===
export type User = typeof users.$inferSelect;
export type Admin = typeof admins.$inferSelect;
export type Channel = typeof channels.$inferSelect;
export type Link = typeof links.$inferSelect;
export type BotSetting = typeof botSettings.$inferSelect;

export type InsertUser = z.infer<typeof insertUserSchema>;
export type InsertAdmin = z.infer<typeof insertAdminSchema>;
export type InsertChannel = z.infer<typeof insertChannelSchema>;
export type InsertLink = z.infer<typeof insertLinkSchema>;
export type InsertBotSetting = z.infer<typeof insertBotSettingSchema>;

export type StatsResponse = {
  totalUsers: number;
  totalChannels: number;
  totalLinks: number;
  uptime: number;
};
