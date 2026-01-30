import { Bot, session, InlineKeyboard, Context } from "grammy";
import { storage } from "./storage";
import { config } from "./config"; // Import centralized config
import { type User as DbUser } from "@shared/schema";
import { DateTime } from "luxon";

// Extended Context if needed
type MyContext = Context;

let bot: Bot<MyContext>;

export async function startBot() {
  if (!config.telegramBotToken) {
    console.warn("TELEGRAM_BOT_TOKEN is not set. Bot will not start.");
    return;
  }

  bot = new Bot<MyContext>(config.telegramBotToken);

  // --- Middleware ---
  // Log every request
  bot.use(async (ctx, next) => {
    // Register user if not exists
    if (ctx.from) {
      const existing = await storage.getUser(ctx.from.id);
      if (!existing) {
        await storage.createUser({
          telegramId: ctx.from.id,
          username: ctx.from.username || null,
          firstName: ctx.from.first_name,
          lastName: ctx.from.last_name || null,
        });
      }
    }
    await next();
  });

  // --- Helper Functions ---
  const deleteAfter = (ctx: Context, msgId: number, ms: number) => {
    setTimeout(async () => {
      try {
        await ctx.api.deleteMessage(ctx.chat!.id, msgId);
      } catch (e) {
        // Ignore if already deleted
      }
    }, ms);
  };

  // --- Commands ---

  bot.command("start", async (ctx) => {
    const payload = ctx.match;
    
    if (payload) {
      // Handle Token (Request/Direct Link)
      const link = await storage.getLinkByToken(payload);
      
      if (!link) {
        return ctx.reply("Invalid or expired link.");
      }

      if (link.isRevoked) {
        return ctx.reply("This link has expired/revoked.");
      }

      // Check if expired by time
      if (link.expiresAt && new Date() > link.expiresAt) {
        await storage.revokeLink(payload);
        return ctx.reply("This link has expired.");
      }

      const channel = await storage.getChannelById(link.channelId!);
      if (!channel) return ctx.reply("Channel not found.");

      // Logic: Send Image + Button
      const inviteLink = channel.primaryLink || "https://t.me/CrunchyRollChannel";

      // Send Image
      const settings = await storage.getBotSettings();
      const caption = settings['caption']?.text || "Please Join The Channel By Clicking The Link Or Button And This Link Will Expire within few minutes.";
      
      const msg1 = await ctx.reply("🔗 Channel Link 🔗\n\n" + inviteLink, {
        reply_markup: new InlineKeyboard().url(settings['button_text']?.text || "⛩️ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗇 ⛩️", inviteLink)
      });
      
      const msg2 = await ctx.reply(caption, { reply_to_message_id: msg1.message_id });

      // Delete after 30 mins
      deleteAfter(ctx, msg1.message_id, 30 * 60 * 1000);
      deleteAfter(ctx, msg2.message_id, 30 * 60 * 1000);
      return;
    }

    // Normal Start
    const msg = await ctx.reply(
      `Konnichiwa! 🤗\nMera Naam **Crunchyroll Link Provider** hai.\n\nMain aapko **anime channels** ki links provide karta hu, Iss Anime Ke Channel Se.\n\n🔹 Agar aapko kisi anime ki link chahiye,\n🔹 Ya channel ki link nahi mil rahi hai,\n🔹 Ya link expired ho gayi hai\n\nToh aap **@CrunchyRollChannel** se New aur working links le sakte hain.\n\nShukriya! ❤️`,
      { parse_mode: "Markdown" }
    );
    deleteAfter(ctx, msg.message_id, 15 * 60 * 1000);
  });

  bot.command("help", async (ctx) => {
    const msg = await ctx.reply(
      `**🆘 Help & Support**\nAgar aapko kisi bhi help ki zaroorat hai, toh humse yahan sampark karein:\n**@CrunchyRollHelper**\n\n**🎬 More Anime**\nAgar aap aur anime dekna chahte hain, toh yahan se dekh sakte hain:\n**@CrunchyRollChannel**\n\n**🤖 Bot Info**\nBot ki jaankari ke liye /about ya /info ka istemal karein.`,
      { parse_mode: "Markdown" }
    );
    deleteAfter(ctx, msg.message_id, 2 * 60 * 1000);
  });

  bot.command(["about", "info"], async (ctx) => {
    const startDate = DateTime.fromISO("2026-01-26");
    const diff = DateTime.now().diff(startDate, ["days"]).days;
    const age = Math.floor(diff) + " Day(s)";

    const msg = await ctx.reply(
      `About The Bot\n🤖 My Name :- <a href='https://telegra.ph/Crunchy-Roll-Vault-04-08'>Crunchyroll Link Provider</a>\nBot Age :- ${age} (26/01/2026)\nAnime Channel :- <a href='https://t.me/Crunchyrollchannel'>Crunchy Roll Channel</a>\nLanguage :- <a href='https://t.me/Crunchyrollchannel'>Node.js (Better than Python)</a>\nDeveloper: :- <a href='https://t.me/World_Fastest_Bots'>World Fastest Bots</a>\n\nThis Is Private/Paid Bot Provided By\n@World_Fastest_Bots.`,
      {
        parse_mode: "HTML",
        reply_markup: new InlineKeyboard()
          .url("📡 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆", "https://t.me/World_Fastest_Bots")
          .row()
          .url("World Fastest Bots", "https://t.me/World_Fastest_Bots")
      }
    );
    deleteAfter(ctx, msg.message_id, 60 * 1000);
  });

  bot.command("ping", async (ctx) => {
    const start = Date.now();
    const msg = await ctx.reply("Pong!");
    await ctx.api.editMessageText(ctx.chat.id, msg.message_id, `Pong! ${Date.now() - start}ms`);
  });

  bot.command("status", async (ctx) => {
    const userCount = await storage.getUserCount();
    const uptime = process.uptime();
    const d = Math.floor(uptime / (3600*24));
    const h = Math.floor(uptime % (3600*24) / 3600);
    const m = Math.floor(uptime % 3600 / 60);
    
    await ctx.reply(
      `⚙️ sʏsᴛᴇᴍ sᴛᴀᴛᴜs\n\n🖥 CPU: 12.3% | RAM: 45.0%\n⏱ ᴜᴘᴛɪᴍᴇ: ${d}d ${h}h ${m}m\n🕒 sᴛᴀʀᴛᴇᴅ: 2026-01-26\n⏰ ᴘᴇɴᴅɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛs: 0\n👥 Total Users: ${userCount}`
    );
  });

  // --- Admin Commands ---
  // Middleware to check admin
  const isAdmin = async (ctx: Context, next: Function) => {
    const userId = ctx.from?.id;
    if (!userId) return;

    // Check if Owner (from Config)
    if (userId === config.ownerId) {
      return next();
    }

    // Check if Admin (from DB)
    const admin = await storage.getAdmin(userId);
    if (admin) {
      return next();
    }

    // Not authorized
    return ctx.reply("⚠️ You are not authorized to use this command.");
  };

  // Apply Admin Middleware to these commands
  const adminCommands = ["addchannel", "channels", "stats", "broadcast", "addadmin", "deladmin", "admins"];
  
  // We'll wrap individual command handlers instead of a global .use() to allow mixed usage if needed later
  
  bot.command("addchannel", async (ctx) => {
    if (ctx.from?.id !== config.ownerId && !(await storage.getAdmin(ctx.from!.id))) {
      return ctx.reply("⚠️ Not authorized.");
    }

    // Format: /addchannel [Anime Name] [Channel Id]
    const args = ctx.match as string;
    const parts = args.split(' ');
    if (parts.length < 2) return ctx.reply("Usage: /addchannel [Anime Name] [Channel Id]");
    
    const channelId = parseInt(parts.pop()!);
    const name = parts.join(' ');

    try {
      await storage.createChannel({
        name,
        telegramChannelId: channelId,
        primaryLink: `https://t.me/c/${String(channelId).replace('-100', '')}/1`,
        hasInvitePermission: true
      });
      ctx.reply(`Successfully Added Channel ${name}`);
    } catch (e) {
      console.error(e);
      ctx.reply("Error adding channel. Ensure I am admin and ID is correct.");
    }
  });

  bot.command("channels", async (ctx) => {
    if (ctx.from?.id !== config.ownerId && !(await storage.getAdmin(ctx.from!.id))) {
      return ctx.reply("⚠️ Not authorized.");
    }

    const channels = await storage.getChannels();
    if (channels.length === 0) return ctx.reply("No channels added.");
    
    let text = "📺 **Channels List**\n\n";
    channels.forEach((c, i) => {
      text += `${i + 1}. ${c.name} (ID: ${c.telegramChannelId})\n`;
    });
    
    ctx.reply(text, { parse_mode: "Markdown" });
  });

  bot.command("stats", async (ctx) => {
    if (ctx.from?.id !== config.ownerId && !(await storage.getAdmin(ctx.from!.id))) {
      return ctx.reply("⚠️ Not authorized.");
    }

    const userCount = await storage.getUserCount();
    const channelCount = await storage.getChannelCount();
    const linkCount = await storage.getActiveLinkCount();

    await ctx.reply(
      `📊 **Bot Statistics**\n\n👥 Total Users: ${userCount}\n📺 Total Channels: ${channelCount}\n🔗 Active Links: ${linkCount}`
    );
  });

  // Start
  bot.start();
  console.log("Bot started!");
  
  // Graceful stop
  process.once("SIGINT", () => bot.stop());
  process.once("SIGTERM", () => bot.stop());
}
