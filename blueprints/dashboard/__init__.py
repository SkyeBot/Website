from quart import render_template, request, redirect, flash, Blueprint, current_app, url_for

dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.route("/dashboard")
async def main():
    discord = current_app.discord
    app = current_app

    
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild_count = await app.ipc.request("get_guild_count")
    guild_ids = await app.ipc.request("get_guild_ids")
    print(guild_ids['data'])

    user = await discord.fetch_user()
    user_guilds = await discord.fetch_guilds()
    guild_ids = guild_ids['data']

    guilds = []
    


    for guild in user_guilds:
        if guild.permissions.administrator:            
            if guild.id in guild_ids:
                guild.class_color = ".green-border" if guild.id in guild_ids else ".red-border"
                guilds.append(guild)
            else:
                continue

        
    print(guilds)

    guild_count = guild_count['count']
    
    

    name = (await discord.fetch_user()).name
    id = (await discord.fetch_user()).discriminator
    return await render_template("dashboard.html", guild_count=guild_count, guilds=guilds, username=name, id=id, user=user)



@dashboard.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    discord = current_app.discord
    app = current_app
    if not await discord.authorized:
        return redirect(url_for("login"))

    
    guild = await app.ipc.request("get_guild", guild_id=guild_id)
    
    try:
        gu_id = guild["id"]
        gu_name = guild["name"]
    except KeyError:
         return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')

    if gu_name is None:
        return """No guild found!"""


    return await render_template("server_settings.html", gu_name=gu_name, gu_id = gu_id)