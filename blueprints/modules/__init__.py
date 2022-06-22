import asyncio
from quart import Blueprint, redirect, render_template, url_for, current_app
from app import App

modules = Blueprint('simple_page', __name__,
                        template_folder='templates')




@modules.route('/dashboard/<int:guild_id>/modules')
async def hello(guild_id):
    
    app = current_app

    if not await app.discord.authorized:
        return redirect(url_for("login"))


    guild = await app.ipc.request("get_guild", guild_id=guild_id)
    
    if guild is None:
        return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')

    gu_id = guild["id"]
    gu_name = guild["name"]

    if gu_name is None:
        return """No guild found!"""


    return await render_template("dashboard2.html", gu_name=gu_name, gu_id = gu_id)
