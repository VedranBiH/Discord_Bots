import os
import discord
from discord.ext import commands
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class TeamResponseBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.responses = {}
        
    async def setup_hook(self):
        await self.add_cog(ResponseCommands(self))
        
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')

class ResponseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='submit')
    async def submit_response(self, ctx, response_id: str, *, response_text: str):
        """Submit a response for a specific ID"""
        try:
            # Create entry for new response_id if it doesn't exist
            if response_id not in self.bot.responses:
                self.bot.responses[response_id] = {}
            
            # Store the response with timestamp
            self.bot.responses[response_id][str(ctx.author.id)] = {
                'author': ctx.author.name,
                'response': response_text,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            await ctx.send(f'Response submitted for ID: {response_id}')
            logger.info(f'Response submitted by {ctx.author.name} for ID: {response_id}')
            
        except Exception as e:
            logger.error(f'Error submitting response: {str(e)}')
            await ctx.send('There was an error submitting your response. Please try again.')

    @commands.command(name='view')
    async def view_responses(self, ctx, response_id: str):
        """View all responses for a specific ID"""
        try:
            if response_id not in self.bot.responses:
                await ctx.send(f'No responses found for ID: {response_id}')
                return
            
            embed = discord.Embed(
                title=f'Responses for ID: {response_id}',
                color=discord.Color.blue()
            )
            
            for user_id, data in self.bot.responses[response_id].items():
                embed.add_field(
                    name=f"Response from {data['author']}",
                    value=f"{data['response']}\n*Submitted at: {data['timestamp']}*",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            logger.info(f'Responses viewed for ID: {response_id} by {ctx.author.name}')
            
        except Exception as e:
            logger.error(f'Error viewing responses: {str(e)}')
            await ctx.send('There was an error viewing the responses. Please try again.')

    @commands.command(name='list')
    async def list_ids(self, ctx):
        """List all response IDs and their contents"""
        try:
            if not self.bot.responses:
                await ctx.send('No responses have been submitted yet.')
                return
            
            # Create an embed for each response ID
            for response_id, responses in self.bot.responses.items():
                embed = discord.Embed(
                    title=f'Responses for ID: {response_id}',
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                if not responses:
                    embed.description = "No responses for this ID yet."
                else:
                    for user_id, data in responses.items():
                        embed.add_field(
                            name=f"Response from {data['author']}",
                            value=f"{data['response']}\n*Submitted at: {data['timestamp']}*",
                            inline=False
                        )
                
                await ctx.send(embed=embed)
            
            logger.info(f'All responses listed by {ctx.author.name}')
            
        except Exception as e:
            logger.error(f'Error listing responses: {str(e)}')
            await ctx.send('There was an error listing the responses. Please try again.')

    @commands.command(name='clear')
    @commands.has_permissions(administrator=True)
    async def clear_responses(self, ctx, response_id: str):
        """Clear responses for a specific ID (admin only)"""
        try:
            if response_id in self.bot.responses:
                del self.bot.responses[response_id]
                await ctx.send(f'Cleared all responses for ID: {response_id}')
                logger.info(f'Responses cleared for ID: {response_id} by {ctx.author.name}')
            else:
                await ctx.send(f'No responses found for ID: {response_id}')
                
        except Exception as e:
            logger.error(f'Error clearing responses: {str(e)}')
            await ctx.send('There was an error clearing the responses. Please try again.')

def main():
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    
    # Create and run bot
    bot = TeamResponseBot()
    bot.run(token)

if __name__ == "__main__":
    main()
