from datetime import datetime

import discord
from discord.ext import commands

# import for type hint :
from bot import SGD_Bot


class Meeting(commands.Cog):
    bot: SGD_Bot = None

    def __init__(self, bot: SGD_Bot):
        self.bot: SGD_Bot = bot
        self.meeting_text_ch_dict: dict = {}
        self.meeting_voice_ch_dict: dict = {}

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("[cogs] [meeting] Meeting 모듈이 준비되었습니다.")
        pass

    # Commands
    @commands.group(
        name="회의",
        description="팀의 회의를 보조하는 기능들을 모아둔 명령어 그룹입니다."
    )
    async def meeting(self, ctx: commands.Context, *args):
        if ctx.invoked_subcommand is None:
            # Prepare the help embed
            meeting_embed = discord.Embed(
                title="SGD Management Bot",
                description="봇 도움말",
                color=self.bot.initial_color
            )
            meeting_embed.set_thumbnail(url=self.bot.user.avatar_url)
            meeting_embed.set_footer(
                text=f"{ctx.author.display_name}님이 요청하셨습니다.",
                icon_url=ctx.author.avatar_url
            )
            meeting_embed.add_field(name="meeting 모듈 소개", value="디스코드 내 회의에 도움을 주는 다양한 기능들을 포함한 모듈입니다.\n"
                                                                + "사용법 : SGD 도움말 meeting")

    @meeting.command(
        name="시작",
        description="주어진 주제로 회의를 시작합니다."
    )
    async def start(self, ctx: commands.Context, topic: str):
        meeting_category: discord.CategoryChannel = discord.utils.find(lambda ch: ch.name == ctx.channel.name, ctx.guild.categories)

        meeting_text_ch: discord.TextChannel = await meeting_category.create_text_channel(f"회의_{topic}")
        meeting_start_time: datetime = ctx.message.created_at
        meeting_info_embed: discord.Embed = discord.Embed(
            title=f"{meeting_start_time.year}년 {meeting_start_time.month}월 {meeting_start_time.day}일 회의",
            description=f"회의 주제 : **{topic}**"
        )

        await meeting_text_ch.send(embed=meeting_info_embed)

        meeting_voice_ch: discord.VoiceChannel = await meeting_category.create_voice_channel(name=f"회의_{topic}")
        await meeting_voice_ch.set_permissions(target=ctx.guild.default_role, connect=False, manage_permissions=False)

        self.meeting_text_ch_dict[topic] = meeting_text_ch
        self.meeting_voice_ch_dict[topic] = meeting_voice_ch

    @meeting.command(
        name="종료",
        description="회의를 종료합니다. 결정사항 없이는 종료할 수 없습니다."
    )
    async def finish(self, ctx: commands.Context, conclusion: str):
        meeting_topic: str = ctx.channel.name[2:]
        if ctx.channel != self.meeting_text_ch_dict[meeting_topic]:
            return await ctx.send("> 오류가 발생했습니다!\n저장된 해당 주제의 회의 채널과 현재 채널이 다릅니다!")
        else:
            await ctx.send("> 해당 결정사항으로 회의를 종료하겠습니다.")
            conclusion_ch_id = self.bot.guild_config["modules"]["meeting"]["ch_ids"]["conclusion"]
            conclusion_ch: discord.TextChannel = discord.utils.find(lambda ch: ch.id == conclusion_ch_id, ctx.guild.text_channels)
            
            conclusion_embed: discord.Embed = discord.Embed(
                title=f"{meeting_topic}에 대한 회의가 종료되었습니다.",
                description=f"회의 결과에 대해 안내드립니다."
            )
            conclusion_embed.add_field(name="결론", value=conclusion)
            await conclusion_ch.send(embed=conclusion_embed)

            await ctx.channel.delete(reason="회의가 종료되었습니다.")

            meeting_voice_channel: discord.VoiceChannel = discord.utils.find(lambda ch: meeting_topic in ch.name, ctx.guild.voice_channels)




            


def setup(bot):
    bot.logger.info("[cogs] [meeting] Meeting 모듈을 준비합니다.")
    bot.add_cog(Meeting(bot))