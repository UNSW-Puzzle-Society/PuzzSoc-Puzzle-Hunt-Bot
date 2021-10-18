"""
josh write an module string here or something
"""
import datetime
import time
import csv
import os
import discord
with open('.token', 'r', encoding="utf-8") as f:
    TOKEN = f.read()

#########################################################################
# Version 1.3

puzzle_answers = [
    'brakedance',
    'caramelpies',
    'adventure',
    'eeniemeenieminiemo',
    'class',
    'metaanswer']
puzzle_links = [
    'https://cdn.discordapp.com/attachments/'
    '608260104906866717/873216521072169010/Full_Speed_Ahead_.png',
    'https://cdn.discordapp.com/attachments'
    '/608259916918161429/873216949302210631/A_Sweet_Mix-up.png',
    'https://cdn.discordapp.com/attachments/'
    '861807322786693139/873508887515508826/Soul_Reason.png',
    'https://cdn.discordapp.com/attachments/'
    '609363499705171969/873540148808282152/trashtowers.png',
    'https://cdn.discordapp.com/attachments/'
    '608260104906866717/873216550998507530/Nemos_New_Family.png',
    'meta linkkkkk'
]
NUM_SCOREBOARD = 40
NUM_HINTS = 5
CHANNEL_ID = 727145488125788270  # where updates get sent to BOT UPDATES
CHANNEL_ID_2 = 727145488125788270  # where successes get sent to
CHANNEL_ID_3 = 727145488125788270  # where meta successes get sent to
ADMIN_PASSWORD = ''  # password for admin commands
# name of responses csv
RESPONSES_CSV = "EcoSoc x PuzzleSoc_ [event name] (Responses) - Form Responses 1.csv"

HUNT_STARTED = True

#########################################################################

teamlist = {}
# creating dictionary {"teamid":"teamname"}
with open('teamlist.csv', newline='', encoding="utf-8") as f:
    for team in csv.DictReader(f):
        teamlist[team["teamid"]] = team["teamname"]

try:  # initialising teamlist.csv creates/formats it if incorrect form
    with open("teamlist.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        if next(reader) != [
            'teamid',
            'teamname',
            'user1',
            'user2',
            'user3',
            'user4',
            'solve1',
            'solve2',
            'solve3',
            'solve4',
            'solve5',
            'solve6',
                'hints']:
            with open("teamlist.csv", "w", encoding="utf-8") as ff:
                ff.write(
                    "teamid,teamname,"
                    "user1,user2,user3,user4,solve1,solve2,solve3,solve4,solve5,hints\n")
except BaseException:  # what is this supposed to be?
    with open("teamlist.csv", "w", encoding="utf-8") as f:
        f.write(
            "teamid,teamname,user1,user2,user3,user4,"
            "solve1,solve2,solve3,solve4,solve5,solve6,hints\n"
        )

try:  # initialising statistics.csv creates/formats it if incorrect form
    with open("statistics.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        if next(reader) != [
            'teamid',
            'attempts1',
            'time1',
            'attempts2',
            'time2',
            'attempts3',
            'time3',
            'attempts4',
            'time4',
            'attempts5',
            'time5',
            'attempts6',
                'time6']:
            with open("statistics.csv", "w", encoding="utf-8") as ff:
                ff.write(
                    "teamid,attempts1,time1,attempts2,time2,attempts3,time3,"
                    "attempts4,time4,attempts5,time5,attempts6,time6\n"
                )

except BaseException:  # what is this supposed to be?
    with open("statistics.csv", "w", encoding="utf-8") as f:
        f.write(
            "teamid,attempts1,time1,attempts2,time2,attempts3,time3,"
            "attempts4,time4,attempts5,time5,attempts6,time6\n"
        )


# updates a given field for a team
def update_field(teamid, field, new, filename):
    field_pos = {
        'teamid': 0,
        'solve1': 6,
        'solve2': 7,
        'solve3': 8,
        'solve4': 9,
        'solve5': 10,
        'solve6': 11,
        'hints': 12,
        'attempts1': 1,
        'time1': 2,
        'attempts2': 3,
        'time2': 4,
        'attempts3': 5,
        'time3': 6,
        'attempts4': 7,
        'time4': 8,
        'attempts5': 9,
        'time5': 10,
        'attempts6': 11,
        'time6': 12}
    with open(filename, 'r', encoding="utf-8") as old_file, open(
            'temporary_file.csv', 'w+', encoding="utf-8") as new_file:
        for row in old_file:
            row_content = row.split(',')
            if row_content[0] == str(teamid):
                row_content[field_pos[field]] = str(new)
                new_file.write(str(','.join(row_content)))
                # to solve cap issue (no newline written when last field is
                # updated)
                if field in ('hints', 'solve6'):
                    new_file.write("\n")
            else:
                new_file.write(row)
    os.remove(filename)
    os.rename('temporary_file.csv', filename)


# returns a specific field for a specific team
def get_field(teamid, field, filename):
    with open(filename, newline='', encoding="utf-8") as users:
        for user in csv.DictReader(users):
            if int(user['teamid']) == teamid:
                return user[field]


# returns teamid from userid. Returns -1 if not in a teamlist.csv
# registered team
def team_id(userid):
    with open('teamlist.csv', newline='', encoding="utf-8") as f:
        for team in csv.DictReader(f):
            if str(userid) == team["user1"] or str(userid) == team["user2"] or str(
                    userid) == team["user3"] or str(userid) == team["user4"]:
                return int(team["teamid"])
    return -1


# returns the number of puzzles solved for a specific teamid
def check_score(teamid):
    x = 0
    for i in range(5):
        if get_field(teamid, f'solve{str(i + 1)}', "teamlist.csv") == '1':
            x += 1
    return x


# returns teamid from the team name
def get_teamid(teamname):
    with open('teamlist.csv', newline='', encoding="utf-8") as users:
        for user in csv.DictReader(users):
            if user['teamname'] == teamname:
                return int(user['teamid'])
    return -1


class MyClient(discord.Client):
    @staticmethod
    async def on_ready():
        print('\nOnline')
        print(f'We have logged in as {client.user}')

    async def on_message(self, message):
        # R0912: Too many branches (58/12) (too-many-branches)
        # R0915: Too many statements (182/50) (too-many-statements)
        # Just create seperate functions for these things
        # W0603: Using the global statement (global-statement)
        # also stop using globals
        global teamlist
        global HUNT_STARTED
        if message.author.id == self.user.id:
            return
        # print(
        #     f'{message.author.name}',
        #     f'[{message.guild.name}/{message.channel.name}]: {message.content}'
        # )
        if message.content.startswith('!'):
            message_words = message.content.split()
            team = team_id(message.author.id)

            if message.content == '!help':
                embed = discord.Embed(title="Help Page", color=0x5865F2)
                embed.add_field(
                    name="!puzz[number] [answer]",
                    value="Check the answer of your [number]th puzzle. The meta is considered "
                        f"puzzle {len(puzzle_answers)}\nEg !puzz1 sampleanswer",
                    inline=False)
                embed.add_field(
                    name="!getmeta",
                    value="Get the meta, if you've answered all 5 puzzles correctly!",
                    inline=False)
                embed.add_field(
                    name="!progress",
                    value="Check your current progress and number of hints remaining.",
                    inline=False)
                embed.add_field(
                    name="!getpuzzles",
                    value="Get the links for the first 5 puzzles again.",
                    inline=False)
                embed.add_field(
                    name="!top",
                    value="Check the leaderboard for puzzles solved!",
                    inline=False)
                await message.channel.send(embed=embed)

            elif message.content == '!admin' + ADMIN_PASSWORD:
                embed = discord.Embed(title="Admin Commands", color=0x000000)
                embed.add_field(
                    name="!convert",
                    value="Converts registration form to teamlist (leaves existing teams alone).",
                    inline=False)
                embed.add_field(
                    name="!getid [user tag]",
                    value="Gets the id of a user if they share a server with the bot.\n"
                    "Eg !getid puzzlemaster#1234",
                    inline=False)
                embed.add_field(
                    name="!usedhint [team name]",
                    value="Reduces hint count of team by 1.\nEg !usedhint TSM gia",
                    inline=False)
                embed.add_field(
                    name="!check [team name]",
                    value="Shows progress and number of hints remaining.\nEg !check TSM gia",
                    inline=False)
                embed.add_field(name="!send",
                                value="Sends message (change in bot code)",
                                inline=False)
                embed.add_field(name="!huntenable",
                                value="activates hunt and !getpuzzles command",
                                inline=False)
                embed.add_field(name="!huntdisable",
                                value="deactivates hunt and disables !getpuzzles command",
                                inline=False)
                await message.channel.send(embed=embed)

            elif message.content == '!huntenable' + ADMIN_PASSWORD:
                HUNT_STARTED = True
                await message.channel.send('Hunt enabled')

            elif message.content == '!huntdisable' + ADMIN_PASSWORD:
                HUNT_STARTED = False
                await message.channel.send('Hunt disabled')

            elif message.content == '!convert' + ADMIN_PASSWORD:

                try:
                    with open(RESPONSES_CSV, "r", encoding="utf-8") as f:
                        pass
                except FileNotFoundError:
                    await message.channel.send('Registration form csv not found!')

                with open(RESPONSES_CSV, 'r', encoding="utf-8", newline='') as f:
                    j = 1
                    for team in csv.DictReader(f):
                        ids = []
                        for i in range(1, 5):
                            # if i == 1:
                            #     person = team[
                            #         f"Team member {str(i)}'s Discord#ID (eg PuzzleMaster#1234)"]
                            # else:
                            person = team[f"Discord Name and Number {str(i)}"]
                            try:
                                ids.append(
                                    discord.utils.get(
                                        client.get_all_members(),
                                        name=f"{person[:-5]}",
                                        discriminator=f"{person[-4:]}"
                                    ).id
                                )
                            except BaseException:
                                ids.append("None")
                                if person != '':
                                    print(person + " wasn't found")
                                    await message.channel.send(f"{person} wasn't found")

                        # this runs like 1, 12, 123, because each new one is
                        # added per loop
                        team_already_exists = False
                        with open('teamlist.csv', 'r', encoding="utf-8") as ff:
                            for row in csv.DictReader(ff):
                                if row["teamname"] == team['Team Name']:
                                    team_already_exists = True
                                    await message.channel.send('Team **' + team[
                                        'Team Name'] + "** is already in teamlist.csv. "
                                        "No action taken for team.")

                        if not team_already_exists:
                            with open(
                                    'teamlist.csv', 'a', newline='', encoding="utf-8") as teamlist:
                                writer = csv.DictWriter(
                                    teamlist,
                                    fieldnames=[
                                        'teamid',
                                        'teamname',
                                        'user1',
                                        'user2',
                                        'user3',
                                        'user4',
                                        'solve1',
                                        'solve2',
                                        'solve3',
                                        'solve4',
                                        'solve5',
                                        'solve6',
                                        'hints'])
                                writer.writerow({'teamid': j,
                                                 'teamname': team['Team Name'],
                                                 'user1': ids[0],
                                                 'user2': ids[1],
                                                 'user3': ids[2],
                                                 'user4': ids[3],
                                                 'solve1': 0,
                                                 'solve2': 0,
                                                 'solve3': 0,
                                                 'solve4': 0,
                                                 'solve5': 0,
                                                 'solve6': 0,
                                                 'hints': NUM_HINTS
                                                 })
                            with open(
                                    'statistics.csv',
                                    'a',
                                    newline='',
                                    encoding="utf-8",
                                ) as statistics:
                                writer = csv.DictWriter(
                                    statistics,
                                    fieldnames=[
                                        'teamid',
                                        'attempts1',
                                        'time1',
                                        'attempts2',
                                        'time2',
                                        'attempts3',
                                        'time3',
                                        'attempts4',
                                        'time4',
                                        'attempts5',
                                        'time5',
                                        'attempts6',
                                        'time6'])
                                writer.writerow({'teamid': j,
                                                 'attempts1': 0,
                                                 'time1': "NULL",
                                                 'attempts2': 0,
                                                 'time2': "NULL",
                                                 'attempts3': 0,
                                                 'time3': "NULL",
                                                 'attempts4': 0,
                                                 'time4': "NULL",
                                                 'attempts5': 0,
                                                 'time5': "NULL",
                                                 'attempts6': 0,
                                                 'time6': "NULL",
                                                 })
                        j += 1

                teamlist = {}
                with open('teamlist.csv', newline='', encoding="utf-8") as f:
                    for team in csv.DictReader(f):
                        teamlist[team["teamid"]] = team["teamname"]

                await message.channel.send('Teams loaded')

            elif message_words[0] == '!check' + ADMIN_PASSWORD:
                teamname = message.content.split(' ', 1)[1]

                if get_teamid(teamname) == -1:
                    await message.channel.send(
                        'Team not found! Make sure you type the team name exactly, case sensitive.')
                else:
                    try:
                        embed = discord.Embed(
                            title=f"Team {teamname} Progress", color=0x7289DA)
                        embed.add_field(
                            name='**  **1\t 2\t\u20093\t\u20094\t\u200A5\u2005\u2005\u2005M',
                            value=" ".join(
                                [':green_square:' if get_field(
                                    get_teamid(teamname),
                                    f'solve{str(i + 1)}',
                                    "teamlist.csv",
                                ) == '1' else ":black_large_square:" for i in range(6)]
                            ),
                        )
                        embed.add_field(
                            name="Hints",
                            value=f"""{get_field(get_teamid(teamname),"hints","teamlist.csv")} """
                            "hints remaining.",
                            inline=False)
                        await message.channel.send(embed=embed)

                    except TypeError:
                        await message.channel.send(
                            "Team not found! "
                            "Make sure you type the team name exactly, case sensitive."
                        )

            elif message_words[0] == '!getid' + ADMIN_PASSWORD:
                person = message.content.split(' ', 1)[1]
                x = discord.utils.get(client.get_all_members(), name="{}".format(
                    person[:-5]), discriminator="{}".format(person[-4:])).id
                await message.channel.send(x)

            elif message_words[0] == '!usedhint' + ADMIN_PASSWORD:
                teamname = message.content.split(' ', 1)[1]
                try:
                    hints = int(get_field(get_teamid(teamname), "hints", "teamlist.csv"))

                except TypeError:
                    await message.channel.send(
                        'Team not found! Make sure you type the team name exactly, case sensitive.')

                else:
                    if hints > 0:
                        update_field(get_teamid(teamname), "hints", str(hints - 1), "teamlist.csv")
                        await message.channel.send(
                            f"Team **{teamname}** now has "
                            f"""{get_field(get_teamid(teamname), "hints", "teamlist.csv")} """
                            "hints remaining."
                        )
                    else:
                        await message.channel.send(
                            'ALERT: team **{teamname}** already had 0 hints remaining!'
                        )
                except TypeError:
                    await message.channel.send(
                        'Team not found! Make sure you type the team name exactly, case sensitive.'
                    )

            elif message.content == '!send' + ADMIN_PASSWORD:
                sendchannel = client.get_channel(503533739104665632)
                await sendchannel.send("""happy birthday chwip <3""")

            elif message.content == '!getpuzzles':
                if HUNT_STARTED:
                    embed = discord.Embed(title="Puzzle List", color=0x5865F2)
                    for i in range(len(puzzle_links) - 1):
                        embed.add_field(name="Puzzle " + str(i + 1),
                                        value=puzzle_links[i],
                                        inline=False)
                    if check_score(team) >= 5:
                        embed.add_field(name="Meta Puzzle (Puzzle 6)",
                                        value=puzzle_links[len(puzzle_links) - 1],
                                        inline=False)
                    else:
                        embed.add_field(
                            name="Meta Puzzle",
                            value="Unlocks once all 5 puzzles have been correctly submitted.",
                            inline=False)
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(
                        'The hunt has not commenced yet! '
                        'The !getpuzzles command will activate soon!')

            elif message.content == '!top':
                score_list = []
                with open('teamlist.csv', newline='', encoding="utf-8") as f:
                    for teama in csv.DictReader(f):
                        score = check_score(int(teama["teamid"]))
                        try:
                            score_list.append(
                                [
                                    teamlist[teama["teamid"]],
                                    score,
                                    get_field(int(teama["teamid"]), 'time6', "statistics.csv"),
                                ]
                            )
                        except KeyError:
                            score_list.append(
                                [
                                    teama["teamid"],
                                    score,
                                    get_field(int(teama["teamid"]), 'time6', "statistics.csv")
                                ]
                            )

                # teams are first sorted by total score, then within the same scores,
                # they are sorted by meta submission time
                score_list = sorted(score_list, key=lambda x: (-x[1], x[2]))

                display_list = []
                for i in range(0, NUM_SCOREBOARD):
                    try:
                        displaylist.append(
                            f"{str(i + 1)}. Team **{score_list[i][0]}** with "
                            f"**{score_list[i][1]}** puzzle"
                            f"""{"" if score_list[i][1] == 1 else "s"} completed."""
                        )
                    except IndexError:  # there should be a better way than try/except
                        pass
                embed = discord.Embed(
                    title="Trick or Treat Hunt Top " +
                    str(NUM_SCOREBOARD) +
                    " Leaderboard",
                    description="\n".join(display_list),
                    color=0xffa500)

                await message.channel.send(embed=embed)

            elif message.content.startswith('!puzz'):
                if team == -1:
                    await message.channel.send(
                        'Sorry, you are not registered. '
                        'If you think this is an error, contact a PuzzleSoc Exec.')
                else:
                    message.content = message.content.lower()
                    channel = client.get_channel(CHANNEL_ID)
                    channel2 = client.get_channel(CHANNEL_ID_2)
                    channel3 = client.get_channel(CHANNEL_ID_3)
                    puzzle_no = message_words[0][-1]
                    answer_attempt = message.content.split(' ', 1)[1]
                    if puzzle_no not in ['1', '2', '3', '4', '5', '6']:
                        await message.channel.send("Use !help to see how to use this bot.")
                        return
                    puzzle_no = int(puzzle_no)
                    try:
                        if get_field(
                            team, f'solve{puzzle_no}', "teamlist.csv"
                        ) != "1":
                            attempts = int(
                                get_field(
                                    team,
                                    'attempts{puzzle_no}',
                                    "statistics.csv",
                                )
                            )
                            update_field(
                                team,
                                'attempts{puzzle_no}',
                                str(attempts + 1),
                                "statistics.csv",
                            )

                        if answer_attempt == puzzle_answers[puzzle_no - 1]:
                            update_field(
                                team,
                                f"solve{puzzle_no}",
                                1,
                                "teamlist.csv",
                            )
                            embed = discord.Embed(color=0x00ff00)
                            embed.add_field(
                                name="Correct!",
                                value=f"Your answer to puzzle {puzzle_no} is correct!\n"
                                        f"Puzzle solved for **{teamlist[str(team)]}**.",
                                inline=False
                            )
                            await message.channel.send(embed=embed)
                            await channel.send(
                                f"<t:{int(time.time())}> "
                                f"Team **{teamlist[str(team)]}** solved puzzle "
                                f"{puzzle_no} with answer "
                                f"'**{message.content[7:]}**'!"
                            )
                            await channel2.send(
                                f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** "
                                f"solved puzzle {puzzle_no} with answer "
                                f"'**{message.content[7:]}**'!"
                            )
                            if puzzle_no == 6:
                                await channel3.send(
                                    f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** "
                                    f"solved puzzle the META with answer "
                                    f"'**{message.content[7:]}**'!"
                                )

                            if check_score(team) == 5:
                                await message.channel.send(
                                    "Congratulations on solving all 5 puzzles! "
                                    "Here's the meta!\n" + puzzle_links[5])
                                await channel.send(
                                    f"<t:{int(time.time())}> "
                                    f"Team **{teamlist[str(team)]}** has reached the meta!"
                                )
                                await channel2.send(
                                    f"<t:{int(time.time())}> "
                                    f"Team **{teamlist[str(team)]}** has reached the meta!"
                                )

                            if get_field(
                                team,
                                f"time{puzzle_no}",
                                "statistics.csv",
                            ) == "NULL":
                                update_field(
                                    team,
                                    "time{puzzle_no}",
                                    datetime.datetime.now().strftime("%c"),
                                    "statistics.csv"
                                )

                        else:
                            embed = discord.Embed(color=0xff0000)
                            embed.add_field(
                                name="Incorrect.",
                                value=f"Your answer to puzzle {puzzle_no} is incorrect.",
                                inline=False
                            )
                            await message.channel.send(embed=embed)
                            await channel.send(
                                f"<t:{int(time.time())}> "
                                f"Team **{teamlist[str(team)]}** "
                                "has incorrectly attempted puzzle "
                                f"{puzzle_no} with answer "
                                f"'**{message.content[7:]}**'."
                            )
                    except IndexError:
                        await message.channel.send("Use !help to see how to use this bot.")

            elif message.content == '!progress':
                if team == -1:
                    await message.channel.send(
                        'Sorry, you are not registered. '
                        'If you think this is an error, contact a PuzzleSoc Exec.')
                else:
                    embed = discord.Embed(
                        title=f"""Team {get_field(team, 'teamname', "teamlist.csv")} Progress""",
                        color=0x7289DA,
                    )
                    embed.add_field(
                        name='**  **1\t 2\t\u20093\t\u20094\t\u200A5\u2005\u2005\u2005M',
                        value=" ".join(
                            [
                                ':green_square:' if get_field(
                                    team, f"solve{i + 1}", "teamlist.csv"
                                ) == '1' else ":black_large_square:" for i in range(6)
                            ]
                        )
                    )

                    embed.add_field(
                        name="Hints",
                        value=f"""{get_field(team, "hints", "teamlist.csv")} hints remaining.""",
                        inline=False,
                    )
                    await message.channel.send(embed=embed)

            elif message.content == '!getmeta':
                if team == -1:
                    await message.channel.send(
                        'Sorry, you are not registered. '
                        'If you think this is an error, contact a PuzzleSoc Exec.'
                    )
                else:
                    x = check_score(team)
                    if x == 5:
                        embed = discord.Embed(color=0xa2f9ff)
                        embed.add_field(
                            name="Meta",
                            value="Congratulations! Here's the meta! "
                            "Remember to submit your meta answer with !puzz6 [answer]\n"
                            f"<:v2:870586401018753044>\n{puzzle_links[5]}",
                            inline=False
                        )
                        await message.channel.send(embed=embed)

                    else:
                        await message.channel.send(
                            f"""You still have {5 - x} puzzle{"" if x == 4 else "s"} to go."""
                        )

            else:
                await message.channel.send("Use !help to see how to use this bot.")


intents = discord.Intents().all()
activity = discord.Activity(name='with puzzles', type=discord.ActivityType.playing)
client = MyClient(intents=intents, activity=activity)
client.run(TOKEN)
