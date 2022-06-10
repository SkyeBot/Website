import asyncio
import dotenv
from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc

import os
import json
import aiohttp


dotenv.load_dotenv()

app = Quart(__name__)
IPC = ipc.Client(
    host="127.0.0.1", 
    port=2301, 
    secret_key="your_secret_key_here"
) # These params must be the same as the ones in the client
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

app.config["SECRET_KEY"] = "test123"
app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]
app.config["DISCORD_REDIRECT_URI"] = "https://skyebot.dev/callback"


discord = DiscordOAuth2Session(app)


@app.route("/")
async def home():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:6060/bot/stats") as request:
            data = await request.json()

            servers = data["servers"]

    
    return await render_template("index.html", servers=servers)

@app.route('/a')
async def ass():
    return await app.ipc.request("get_guild_ids")


@app.route("/login")
async def login():
    return await discord.create_session()


@app.route("/callback")
async def callback():
    try:
        a = await discord.callback()


    except Exception as exceptiom:
        print(exceptiom)

    return redirect(url_for("dashboard"))
    


@app.route("/dashboard")
async def dashboard():
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild_count = await app.ipc.request("get_guild_count")
    guild_ids = await app.ipc.request("get_guild_ids")

    user = await discord.fetch_user()
    user_guilds = await discord.fetch_guilds()
    

    guilds = []
    


    for guild in user_guilds:
    
        if guild.permissions.administrator:
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)
        
    print(guilds)

    guild_count = guild_count['count']
    
    guilds.sort(key=lambda x: x.class_color == "red-border")
    name = (await discord.fetch_user()).name
    id = (await discord.fetch_user()).discriminator
    return await render_template("dashboard.html", guild_count=guild_count, guilds=guilds, username=name, id=id, user=user)

    
@app.route("/commands/")
async def commands():

    return await render_template("commands.html")

@app.route("/invite/")
async def invite():
    return await render_template("invite.html")

@app.route("/FAQ/")
async def FAQ():
    return await render_template("faq.html")
@app.route("/contact/")
async def contact():
    return await render_template("contact.html")

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild = await app.ipc.request("get_guild", guild_id=guild_id)
    
    if guild is None:
        return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')

    gu_id = guild["id"]
    gu_name = guild["name"]


    return await render_template("dashboard2.html", gu_name=gu_name, gu_id = gu_id)
        

@app.route("/me/guilds/")
async def user_guilds():
    guilds = await discord.fetch_guilds()
    return "<br />".join([f"[ADMIN] {g.name}" if g.permissions.administrator else g.name for g in guilds])


@app.route("/me/")
async def me():
	user = await discord.fetch_user()
	return f"""
			<html>
			<head>
			<title>{user.name}</title>
			</head>
			<body><img src='{user.avatar_url or user.default_avatar_url}' />
			<p>Is avatar animated: {str(user.is_avatar_animated)}</p>
			<a href={url_for("my_connections")}>Connections</a>
			<br />
			</body>
			</html>

	"""



@app.route("/logout/")
async def logout():
    discord.revoke()
    return redirect(url_for(".home"))




if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        app.ipc = loop.run_until_complete(IPC.start(loop=loop)) # `Client.start()` returns new Client instance or None if it fails to start
        app.run(port=5000,loop=loop)
    finally:
        loop.run_until_complete(app.ipc.close()) # Closes the session, doesn't close the loop
        loop.close()
