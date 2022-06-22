import asyncio
import logging
import dotenv
from quart import Quart, flash, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc
import os
import asyncpg

from app import App

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

dotenv.load_dotenv()

from blueprints.modules import modules
from blueprints.dashboard import dashboard

app = App()
app.register_blueprint(modules)
app.register_blueprint(dashboard)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


discord = app.discord

@app.route("/")
async def home():
    servers = await app.ipc.request("get_guild_count")

        
    return await render_template("index.html", servers=servers['count'])

@app.route('/support')
async def support():
    return redirect('https://discord.gg/hJNstPFaJk')

@app.route('/a')
async def ass():
    prefix = await app.db.fetch("SELECT * FROM public.guilds ORDER BY guild_id ASC")
    
    data = [dict(row) for row in prefix]


    data = "<br><br>".join(f'owner_id: {x.get("owner_id")}<br>server_name: {x.get("guild_name")}' for x in data)

    return f"""{data}"""

@app.route('/servers')
async def servers():
    return f"""{await discord.fetch_connections()}"""


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



@app.route("/dashboard/<int:guild_id>", methods=['POST'])
async def dashboard_server2(guild_id):
    if request.method == "POST":
        form = await request.form

        guild = await app.ipc.request("get_guild", guild_id=guild_id)
        gu_id = guild["id"]
        gu_name = guild["name"]
    
        if gu_name is None:
            return """No guild found!"""
    

        
        if form['text'] == '':
        # do something
            logger.info("hi")
            return await render_template("dashboard2.html", gu_name=gu_name, gu_id = gu_id)
        else:

            logger.info("ass")
            await app.db.execute('INSERT INTO welcome_config(guild_id,message) VALUES ($1, $2)', guild_id,form['text'])

            await flash("Succesfully updated your welcome message!")
            return await render_template("dashboard2.html", gu_name=gu_name, gu_id = gu_id)

@app.route('/n')
async def hi():
    return await render_template('ass.html')
        
@app.route('/get_toggled_status', methods=['POST']) 
async def toggled_status():
    current_status = request.args.get('status')

    app.db = await asyncpg.create_pool(dsn="postgres://skye:GRwe2h2ATA5qrmpa@localhost:5432/skyetest")

    if current_status == "Toggled": 
        await app.db.execute('INSERT INTO as(message) VALUES ($1)', current_status)


    return 'Toggled' if current_status == 'Untoggled' else 'Untoggled'



@app.route("/me/guilds")
async def user_guilds():
    user_guilds = await discord.fetch_guilds()
    guilds = []
    
    guild_ids = await app.ipc.request("get_guild_ids")

    user = await discord.fetch_user()

    name = (await discord.fetch_user()).name
    id = (await discord.fetch_user()).discriminator

    for guild in user_guilds:
        if guild.permissions.administrator:

            guild.class_color = ".green-border" if guild.id in guild_ids else ".red-border"
            guilds.append(guild)
    
    return await render_template("dashboard.html", guild_count="34", guilds=guilds, username=name, id=id, user=user)



@app.route("/me/connections/")
async def my_connections():
    if not await discord.authorized:
        return redirect(url_for("login"))
    
    user = await discord.fetch_user()
    connections = await discord.fetch_connections()
    return f"""
<html>
<head>
<title>{user.name}</title>
</head>
<body>
{str([f"{connection.name} - {connection.type}" for connection in connections])}
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
        app.ipc = loop.run_until_complete(app.ipc.start(loop=loop))
        app.start(port=5000, debug=True)
    finally:
        loop.run_until_complete(app.ipc.close()) # Closes the session, doesn't close the loop
        loop.close()
