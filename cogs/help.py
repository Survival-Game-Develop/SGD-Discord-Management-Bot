import logging
import sys

import discord
from discord.ext import commands

# import for type hint :
from bot import SGD_Bot


class Help(commands.Cog):
    bot: SGD_Bot = None

    def __init__(self, bot: SGD_Bot):
        self.bot: SGD_Bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info('[legacy_cogs] [help] Help 모듈이 준비되었습니다.')
        pass

    # Commands
    @commands.command(
        name='도움말',
        description='봇의 도움말 명령어입니다.'
    )
    async def help_command(self, ctx: commands.Context, cog='all'):
        # The third parameter comes into play when
        # only one word argument has to be passed by the user

        # Prepare the help embed
        help_embed = discord.Embed(
            title='라테봇',
            description='봇 도움말',
            # 루미너스 브론드        [R236/G202/B179]
            color=self.bot.latte_color
        )
        help_embed.set_thumbnail(url=self.bot.user.avatar_url)
        help_embed.set_footer(
            text=f'Requested by {ctx.author.display_name}',
            icon_url=ctx.author.avatar_url
        )

        # Get a list of all legacy_cogs
        cogs = [c for c in self.bot.cogs.keys()]

        # If cog is not specified by the user, we list all legacy_cogs and commands
        if cog == 'all':
            for cog in cogs:
                # Get a list of all commands under each cog
                cog_commands = self.bot.get_cog(cog).get_commands()
                commands_list = ''
                for cmd in cog_commands:
                    commands_list += f'**{cmd.name}** : {cmd.description}\n'
                    try:
                        if type(cmd) == commands.Group:
                            for subcommand in cmd.commands:
                                commands_list += f'ㄴ {subcommand.name} : {subcommand.description}\n'
                                if len(subcommand.aliases) > 0:
                                    commands_list += f'    **동의어** : {", ".join(subcommand.aliases)}\n'
                            pass
                    except Exception as e:
                        self.bot.logger.error(f'[legacy_cogs] [help] Exception occured! {e}')
                        pass

                # Add the cog's details to the embed.
                help_embed.add_field(
                    name=f'**{cog}**',
                    value=commands_list,
                    inline=False
                ).add_field(
                    name='\u200b', value='\u200b', inline=False
                )
                # Also added a blank field '\u200b' is a whitespace character.
            pass

        else:
            # If the cog was specified
            lower_cogs = [c.lower() for c in cogs]

            # If the cog actually exists.
            if cog.lower() in lower_cogs:
                # Get a list of all commands in the specified cog
                commands_list = self.bot.get_cog(cogs[lower_cogs.index(cog.lower())]).get_commands()

                # Add details of each command to the help text
                # Command Name
                # Description
                # Format
                for command in commands_list:
                    help_content: str = f'{command.description}\n'
                    # Also add aliases, if there are any
                    if len(command.aliases) > 0:
                        help_content += f'**동의어** : {", ".join(command.aliases)}\n'
                    else:
                        # Add a newline character to keep it pretty
                        # That IS the whole purpose of custom help
                        # help_content += '\n'
                        pass
                    if type(command) == commands.Group:
                        for subcommand in command.commands:
                            help_content += f'ㄴ **{subcommand.name}** : {subcommand.description}\n'
                            if len(subcommand.aliases) > 0:
                                 help_content += f'    **동의어** : {", ".join(subcommand.aliases)}\n'
                        pass

                    help_embed.add_field(name=f'**{command.name}**', value=f'{help_content}', inline=True)
            else:
                # Notify the user of invalid cog and finish the command
                await ctx.send(f'존재하지 않는 모듈입니다. `{self.bot.command_prefix}도움말` 명령어로 사용 가능한 모듈과 명령어를 확인해주세요!')
                return

        # Developer Info
        help_embed.add_field(name='개발자', value='Discord : sleepylapis#1608', inline=False)

        await ctx.send(embed=help_embed)
        return


def setup(bot):
    bot.logger.info('[cogs] [help] Help 모듈을 준비합니다.')
    bot.add_cog(Help(bot))