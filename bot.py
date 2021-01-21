from autoIserv import Exercise

import discord
import asyncio
import os
import random
import datetime
from discord.errors import HTTPException
import math
import requests



CONFIG = {}
CHANEL_ID = 689031648045826075  # The channel in which the exercises will be posted
CHANEL_ARCHIVE_ID = 704963705426673695  # The channel in which old exercises end up
SUBJECT_COLORS = {
    "Latin": 0xFAACC0,
    "France": 0xF6C2FA,
    "Spanish": 0xF9D667,
    "Biology" : 0xC3FA7E,
    "Physics": 0xADD2FA,
    "Chemistry": 0x76FFCD,
    "History": 0xAD8651,
    "Politics" : 0x5743FF,
    "English": 0x6ccf2a,
    "Art" : 0xc56cf0,
    "Math": 0x5384FF,
    "German": 0xFFF29A,
    "Geography" : 0x2ed573,
    "Computer Science" : 0x34ace0,
    "Computer Science-WPU" : 0x474787,
    "not_found" : 0xC4C6FA
}
SUBJECT_TRANSLATION = {
    "Latin": "Latein",
    "France": "Französisch",
    "Spanish": "Spanisch",
    "Biology" : "Biologie",
    "Physics": "Physik",
    "Chemistry": "Chemie",
    "History": "Geschichte",
    "Politics" : "Politik",
    "English": "Englisch",
    "Math": "Mathematik",
    "German": "Deutsch",
    "Art" : "Kunst",
    "Geography" : "Erdkunde",
    "Computer Science" : "Informatik",
    "Computer Science-WPU" : "Informatik-WPU",
    "not_found" : "Nicht Erkannt"
}

NEW_EXERCISE_MESSAGES = ["Yay :partying_face: ! Es gibt eine neue Aufgabe :unamused: : ",
                         "Ja Super :clap: ! Noch eine TOLLE :thumbsup: Aufgabe :pencil: die wir machen dürfen :"
                         "Ich hoffe ihr habt die letzte Aufgabe gemacht, denn hier kommt noch eine :smiling_imp: : ",
                         "Wer hat Lust auf eine neue Aufgabe :upside_down: : ",
                         "Potzblitz ! Da gibt est tatsächlich doch eine neue Aufgabe :  ",
                         "Ich hab da mal was vorbereitet... Eine neue Aufgabe : ",
                         "Langweilig ? Hier mit wird dir noch langweiliger :",
                         "Ach übrigens, es gibt ne neue Aufgabe : ",
                         ":new: :pencil:"]

ATTACHMENTS_DOWNLOAD_DIR = r"C:\Users\%username%\Downloads\EmailAttachments"
MAX_FILE_SIZE = 8.0
MAX_DESCRIPTION_SIZE = 2000
MAX_VALUE_SIZE = 1020
SLEEP_TIME = 120
PRIVILEGED_ROLES = [689027602676973580, 689028088880824357]  # These are the ids of the roles that can use the .clear command.
DELETE_OLD_EXERCISE_TIME = datetime.timedelta(hours=1)
MAX_FILES = 10
USE_GROUPS = False
GROUP_CHANGE_EVERY_DAYS = 1
GROUP_START_DATE = datetime.datetime.strptime("26.11.2020", "%d.%m.%Y")
GROUP_OFFSET = datetime.timedelta(days=0)
GROUP_NAMES = {
    1 : "Gruppe A",
    0 : "Gruppe B"
}
BOTH_GROUP_SUBJECTS = []  # Subjects that are in both groups

client = discord.Client()

@client.event
async def on_ready():
    print(f"{client.user} is ready !")


@client.event
async def on_message(message : discord.Message):
    channel = message.channel
    author_roles = message.author.roles
    is_privileged = False
    for role in author_roles:
        if role.id in PRIVILEGED_ROLES:
                is_privileged = True

    if is_privileged:
        message_content = str(message.content)
        if message_content.startswith('.'):
            args = message_content.split(" ")
            if len(args) > 1:
                if args[0] == ".clear":
                    if args[1].isnumeric():
                        print("[*] Clearing Messages")
                        async for msg in channel.history(limit=int(args[1])+1):
                            await msg.delete()


def clamp_string(string, length=1000):
    return string[:length] + (string[length:] and '...')


def get_active_group(start_date : datetime.datetime, subject):
    if subject in BOTH_GROUP_SUBJECTS:
        return "Gruppe A und Gruppe B"
    group_id = math.floor(((start_date + GROUP_OFFSET) - GROUP_START_DATE).days / GROUP_CHANGE_EVERY_DAYS % len(GROUP_NAMES))
    return GROUP_NAMES[group_id]


async def is_changed_exercises(exercises: Exercise, channel : discord.TextChannel):
    async for msg in channel.history():
        if len(msg.embeds) > 0:
            for embed in msg.embeds: # type: discord.Embed
                if embed.url == exercises.view_url:
                    return True
    return False


async def change_status():
    global CONFIG
    try:
        result = requests.get(CONFIG["IServUrl"])
        if result:
            game = discord.Game("Aufgaben suchen")
            await client.change_presence(status=discord.Status.online, activity=game)
        else:
            game = discord.Game("Iserv ist down :sweat_smile:")
            await client.change_presence(status=discord.Status.idle, activity=game)
    except requests.exceptions.ConnectionError:
        game = discord.Game("Iserv ist down :sweat_smile:")
        await client.change_presence(status=discord.Status.idle, activity=game)


async def look_for_exercises():
    await client.wait_until_ready()
    channel = client.get_channel(CHANEL_ID)
    archive_channel = client.get_channel(CHANEL_ARCHIVE_ID)
    while True:
        # Look for new exercises and post them in the channel
        await change_status()
        for file in os.listdir(CONFIG["ExercisesFolder"]):
            try:
                exercise = Exercise.load(f"{CONFIG['ExercisesFolder']}\\{file}")
                if exercise.new:
                    is_changed = await is_changed_exercises(exercise, channel)
                    if is_changed:
                        print("[*] Change in Exercise : " + str(exercise.title))
                    else:
                        print("[*] New Exercise : " + str(exercise.title))

                    embed = discord.Embed(title=clamp_string(exercise.title, MAX_VALUE_SIZE), colour=discord.Colour(SUBJECT_COLORS[exercise.subject]),
                                          url=exercise.view_url,
                                          description=clamp_string(exercise.description, MAX_DESCRIPTION_SIZE))
                    embed.set_author(name=f"{exercise.by}")
                    embed.add_field(name="Anfangs Datum", value=clamp_string(exercise.start_date.strftime("%d/%m/%Y"), MAX_VALUE_SIZE), inline=True)
                    embed.add_field(name="Abgabe Datum", value=clamp_string(exercise.due_date.strftime("%d/%m/%Y %H:%M:%S"), MAX_VALUE_SIZE), inline=True)
                    if USE_GROUPS:
                        embed.add_field(name="Gruppe",value=clamp_string(get_active_group(exercise.start_date, exercise.subject), MAX_VALUE_SIZE),inline=True)
                    embed.add_field(name="Fach", value=clamp_string(SUBJECT_TRANSLATION[exercise.subject], MAX_VALUE_SIZE), inline=False)
                    if is_changed:
                        embed.add_field(name="Ist eine Änderung :pen_ballpoint:", value="Ja", inline=False)

                    attachments_field_value = ""
                    for i, attachment in enumerate(exercise.attachments):
                        if i > MAX_FILES:
                            break
                        attachments_field_value += clamp_string(f"{attachment} :\n```{exercise.attachments[attachment]['description']}```\n", MAX_VALUE_SIZE)

                    if len(exercise.attachments) > 0:
                        embed.add_field(name="Anhänge", value=clamp_string(attachments_field_value, MAX_VALUE_SIZE), inline=False)


                    files = []
                    for i, attachment in enumerate(exercise.attachments):
                        if i > MAX_FILES:
                            break
                        file_path = f"{os.path.expandvars(ATTACHMENTS_DOWNLOAD_DIR)}\\{attachment}"
                        if not os.path.getsize(file_path) / 1000000 >= MAX_FILE_SIZE:
                            files.append(discord.File(file_path, filename=attachment))


                    try:
                        await channel.send(content=random.choice(NEW_EXERCISE_MESSAGES), embed=embed, files=files)
                    except HTTPException as e:
                        if e.status == 413:
                            print(f"HTTPError : {e.text}")
                            embed.remove_field(3)
                            embed.add_field(name="Anhänge", value="Daten sind zu groß",inline=False)
                            await channel.send(content=random.choice(NEW_EXERCISE_MESSAGES), embed=embed)

                    exercise.new = False
                    exercise.save(CONFIG["ExercisesFolder"], None)

            except FileNotFoundError:
                pass

        # Delete old messages and move them to archive
        history = channel.history()
        async for msg in history:
            if len(msg.embeds) > 0:
                for embed in msg.embeds:
                    for i, filed in enumerate(embed.fields):
                        if filed.name == "Abgabe Datum":
                            date = datetime.datetime.strptime(filed.value, "%d/%m/%Y %H:%M:%S")
                            if date + DELETE_OLD_EXERCISE_TIME < datetime.datetime.now():
                                print("[*] Deleting old message")
                                files = []
                                for attachment in msg.attachments:
                                    files.append(await attachment.to_file())

                                await archive_channel.send(content=msg.content, embed=embed, files=files)
                                await msg.delete()
                                break

        await asyncio.sleep(SLEEP_TIME)


def run(_config : dict):
    global CONFIG
    CONFIG = _config
    client.loop.create_task(look_for_exercises())
    client.run(CONFIG["DiscordBotToken"])


if __name__ == "__main__":
    print("You need to run main.py")

