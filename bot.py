import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Бот запущен как {bot.user}")

class UnmuteButton(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.member = member

    @discord.ui.button(label="🔊 Размутить", style=discord.ButtonStyle.success)
    async def unmute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role and muted_role in self.member.roles:
            await self.member.remove_roles(muted_role)
            await interaction.response.send_message(f"{self.member.mention} размучен вручную.", ephemeral=True)
        else:
            await interaction.response.send_message("Этот пользователь не в муте.", ephemeral=True)

@bot.tree.command(name="tempmute", description="Временно замутить пользователя")
@app_commands.describe(member="Пользователь", minutes="На сколько минут замутить")
async def tempmute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    guild = interaction.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted", reason="Создание роли 'Muted'")
        for channel in guild.channels:
            try:
                await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
            except:
                pass

    await member.add_roles(muted_role)

    embed = discord.Embed(
        title="🔇 Игрок замучен",
        description=f"{member.mention} был замучен на **{minutes} минут**.",
        color=discord.Color.red()
    )
    embed.set_footer(text="ZerotixStudio Bot")

    await interaction.response.send_message(embed=embed, view=UnmuteButton(member))
    await asyncio.sleep(minutes * 60)

    if muted_role in member.roles:
        try:
            await member.remove_roles(muted_role)
            await interaction.channel.send(f"{member.mention} автоматически размучен.")
        except:
            pass

@bot.tree.command(name="mute", description="Замутить пользователя навсегда")
@app_commands.describe(member="Пользователь")
async def mute(interaction: discord.Interaction, member: discord.Member):
    guild = interaction.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted", reason="Создание роли 'Muted'")
        for channel in guild.channels:
            try:
                await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
            except:
                pass

    await member.add_roles(muted_role)
    await interaction.response.send_message(f"{member.mention} замучен навсегда.")

@bot.tree.command(name="unmute", description="Размутить пользователя")
@app_commands.describe(member="Пользователь")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await interaction.response.send_message(f"{member.mention} размучен.")
    else:
        await interaction.response.send_message("Этот пользователь не в муте.")

@bot.tree.command(name="ban", description="Забанить пользователя")
@app_commands.describe(member="Кого баним", reason="Причина")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} забанен. Причина: {reason}")

@bot.tree.command(name="say", description="Бот скажет от твоего имени")
@app_commands.describe(text="Текст")
async def say(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "когда вайп" in message.content.lower():
        embed = discord.Embed(
            description=(
                "**Привет!** Вся информация о вайпе публикуется в постах группы ВКонтакте:\n"
                "🔗 https://vk.com/howorld\n"
                "🔗 Лайт-анархия: https://vk.com/holylite\n\n"
                "Если ты **не нашёл пост про вайп**, или в нём **не указано время**, то мы подсказать **не можем**.\n"
                "**Мы не знаем больше, чем написано там.**"
            ),
            color=discord.Color.red()
        )
        embed.set_image(url="https://i.imgur.com/YourWipeMeme.png")
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))