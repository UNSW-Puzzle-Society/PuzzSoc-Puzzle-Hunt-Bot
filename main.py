import discord
import csv
import os
from operator import itemgetter
import time
with open('.token', 'r') as f:
    TOKEN = f.read()

#########################################################################
# Version 1.3

puzzle_answers = ['brakedance', 'caramelpies', 'adventure', 'eeniemeenieminiemo', 'class']
puzzle_links = ['https://cdn.discordapp.com/attachments/608260104906866717/873216521072169010/Full_Speed_Ahead_.png',
                'https://cdn.discordapp.com/attachments/608259916918161429/873216949302210631/A_Sweet_Mix-up.png',
                'https://cdn.discordapp.com/attachments/861807322786693139/873508887515508826/Soul_Reason.png',
                'https://cdn.discordapp.com/attachments/609363499705171969/873540148808282152/trashtowers.png',
                'https://cdn.discordapp.com/attachments/608260104906866717/873216550998507530/Nemos_New_Family.png']
num_scoreboard = 15
num_hints = 8
CHANNEL_ID = 111111111111111111 # where updates get sent to BOT UPDATES
CHANNEL_ID_2 = 111111111111111111 # where successes get sent to
metalink = "https://forms.gle/"

hunt_started = 1

#########################################################################

teamlist = {}
with open('teamlist.csv', newline='') as f:             # creating dictionary {"teamid":"teamname"}
    for team in csv.DictReader(f):
        teamlist[team["teamid"]] = team["teamname"]

try:                                                  # initialising teamlist.csv creates/formats it if incorrect form
    with open("teamlist.csv", "r") as f:
        reader = csv.reader(f)
        if next(reader) != ['teamid', 'teamname', 'user1', 'user2', 'user3', 'user4', 'solve1', 'solve2', 'solve3',
                            'solve4', 'solve5', 'hints']:
            with open("teamlist.csv", "w") as ff:
                ff.write("teamid,teamname,user1,user2,user3,user4,solve1,solve2,solve3,solve4,solve5,hints\n")
except:
    with open("teamlist.csv", "w") as f:
        f.write("teamid,teamname,user1,user2,user3,user4,solve1,solve2,solve3,solve4,solve5,hints\n")

# updates a given field for a team
def update_field(teamid, field, new):
    field_pos = {'teamid': 0, 'solve1': 6, 'solve2': 7, 'solve3': 8, 'solve4': 9, 'solve5': 10, 'hints': 11}
    with open('teamlist.csv', 'r') as old_file, open('updated_teamlist.csv', 'w+') as new_file:
        for row in old_file:
            row_content = row.split(',')
            if row_content[0] == str(teamid):
                row_content[field_pos[field]] = str(new)
                new_file.write(str(','.join(row_content)))
                if field == 'hints':                            # to solve cap issue (no newline written when last field is updated)
                    new_file.write("\n")
            else:
                new_file.write(row)
    os.remove('teamlist.csv')
    os.rename('updated_teamlist.csv', 'teamlist.csv')

# returns a specific field for a specific team
def get_field(teamid, field):
    with open('teamlist.csv', newline='') as users:
        for user in csv.DictReader(users):
            if int(user['teamid']) == teamid:
                return user[field]

# returns teamid from userid. Returns -1 if not in a teamlist.csv registered team
def team_id(userid):
    with open('teamlist.csv', newline='') as f:
        for team in csv.DictReader(f):
            if str(userid) == team["user1"] or str(userid) == team["user2"] or str(userid) == team["user3"] or str(userid) == team["user4"]:
                return int(team["teamid"])
    return -1


# returns the number of puzzles solved for a specific teamid
def check_score(teamid):
    x = 0
    for i in range(5):
        if get_field(teamid, 'solve{}'.format(str(i+1))) == '1':
            x += 1
    return x

# returns teamid from the team name
def get_teamid(teamname):
    with open('teamlist.csv', newline='') as users:
        for user in csv.DictReader(users):
            if user['teamname'] == teamname:
                return int(user['teamid'])

class MyClient(discord.Client):
    @staticmethod
    async def on_ready():
        print('\nOnline')
        print('We have logged in as {0.user}'.format(client))
        # print(str(discord.utils.get(client.get_all_members(), name="testname", discriminator="6665").id))

    async def on_message(self, message):
        global teamlist
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!'):
            message_words = message.content.split()
            team = team_id(message.author.id)

            if message.content == '!help':
                embed = discord.Embed(title="Help Page", color=0x000000)
                embed.add_field(name="!puzz[number] [answer]", value="Check the answer of your [number]th puzzle.\nEg !puzz1 sampleanswer",
                                inline=False)
                embed.add_field(name="!getmeta", value="Get the meta, if you've answered all 5 puzzles correctly!",
                                inline=False)
                embed.add_field(name="!progress", value="Check your current progress and number of hints remaining.",
                                inline=False)
                embed.add_field(name="!getpuzzles", value="Get the links for the first 5 puzzles again.",
                                inline=False)
                embed.add_field(name="!top", value="Check the leaderboard for puzzles solved!",
                                inline=False)
                await message.channel.send(embed=embed)

            elif message.content == '!admin':
                embed = discord.Embed(title="Admin Commandlist Page", color=0x000000)
                embed.add_field(name="!convert",
                                value="Converts registration form to teamlist (leaves existing teams alone).",
                                inline=False)
                embed.add_field(name="!getid [user tag]",
                                value="Gets the id of a user if they share a server with the bot.\nEg !getid puzzlemaster#1234",
                                inline=False)
                embed.add_field(name="!usedhint [team name]",
                                value="Reduces hintcount of team by 1.\nEg !usedhint TSM gia",
                                inline=False)
                embed.add_field(name="!check [team name]",
                                value="Shows progress and number of hints remaining.\nEg !check TSM gia",
                                inline=False)
                await message.channel.send(embed=embed)

            elif message.content == '!convert':
                try:
                    with open("Registration Form (Responses) - Form Responses 1.csv", "r") as f:
                        pass
                except FileNotFoundError:
                    await message.channel.send('Registration form csv not found!')

                with open("Registration Form (Responses) - Form Responses 1.csv", 'r', encoding="utf-8", newline='') as f:
                    j = 1
                    for team in csv.DictReader(f):
                        ids = []
                        for i in range(1, 5):
                            if i == 1:
                                person = team[f"Team member {str(i)}'s Discord#ID (eg PuzzleMaster#1234)"]
                            else:
                                person = team[f"Team member {str(i)}'s Discord#ID"]
                            try:
                                ids.append(discord.utils.get(client.get_all_members(), name="{}".format(person[:-5]),
                                                             discriminator="{}".format(person[-4:])).id)
                            except:
                                ids.append("None")
                                if person != '':
                                    print(person + " wasn't found")
                                    await message.channel.send(person + " wasn't found")

                        team_already_exists = False                             # this runs like 1, 12, 123, because each new one is added per loop
                        with open('teamlist.csv', 'r') as ff:
                            for row in csv.DictReader(ff):
                                if row["teamname"] == team['Team Name']:
                                    team_already_exists = True
                                    await message.channel.send('Team **' + team['Team Name'] + "** is already in teamlist.csv. No action taken for team.")

                        if team_already_exists == False:
                            with open('teamlist.csv', 'a', newline='') as teamlist:
                                writer = csv.DictWriter(teamlist, fieldnames=['teamid', 'teamname', 'user1', 'user2',
                                                                              'user3', 'user4', 'solve1',
                                                                              'solve2', 'solve3',
                                                                              'solve4', 'solve5', 'hints'])
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
                                                 'hints': num_hints
                                                 })
                        j += 1

                teamlist = {}
                with open('teamlist.csv', newline='') as f:
                    for team in csv.DictReader(f):
                        teamlist[team["teamid"]] = team["teamname"]

                await message.channel.send('Teams loaded')

            elif message_words[0] == '!check':
                teamname = message.content[7:]
                try:
                    embed = discord.Embed(title="Team {} Progress".format(teamname), color=0x7289DA)
                    embed.add_field(name='**  **1\t 2\t\u20093\t\u20094\t\u200A5', value=" ".join([':green_square:' if get_field(get_teamid(teamname), 'solve{}'.format(str(i+1))) == '1' else ":black_large_square:" for i in range(5)]))
                    embed.add_field(name="Hints", value="{} hints remaining.".format(get_field(get_teamid(teamname), "hints")),
                                    inline=False)
                    await message.channel.send(embed=embed)

                except TypeError:
                    await message.channel.send('Team not found! Make sure you type the team name exactly, case sensitive.')

            elif message_words[0] == '!getid':
                person = message.content[7:]
                x = discord.utils.get(client.get_all_members(), name="{}".format(person[:-5]), discriminator="{}".format(person[-4:])).id
                await message.channel.send(x)

            elif message_words[0] == '!usedhint':
                teamname = message.content[10:]
                try:
                    hints = int(get_field(get_teamid(teamname), "hints"))
                    if hints > 0:
                        update_field(get_teamid(teamname), "hints", str(hints - 1))
                        await message.channel.send('Team **{}** now has {} hints remaining.'.format(teamname, get_field(get_teamid(teamname), "hints")))
                    else:
                        await message.channel.send('ALERT: team **{}** already had 0 hints remaining!'.format(teamname))
                except TypeError:
                    await message.channel.send('Team not found! Make sure you type the team name exactly, case sensitive.')

            elif message.content == '!send':
                sendchannel = client.get_channel(861446005640003644)
                await sendchannel.send("""<:haLove:895869737169469500>""")

            elif message.content == '!getpuzzles':
                if hunt_started:
                    embed = discord.Embed(title="Puzzle List", color=0x000000)
                    for i in range(len(puzzle_links)):
                        embed.add_field(name="Puzzle " + str(i+1),
                                        value=puzzle_links[i],
                                        inline=False)
                    if check_score(team) == 5:
                        embed.add_field(name="Meta Puzzle",
                                        value=metalink,
                                        inline=False)
                    else:
                        embed.add_field(name="Meta Puzzle",
                                        value="Unlocks once all 5 puzzles have been correctly submitted.",
                                        inline=False)
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send('The hunt has not commenced yet! The !getpuzzles command will activate soon!')

            elif message.content == '!top':
                score_list = []
                with open('teamlist.csv', newline='') as f:
                    for team in csv.DictReader(f):
                        score = check_score(int(team["teamid"]))
                        try:
                            score_list.append([teamlist[team["teamid"]], score])
                        except KeyError:
                            score_list.append([team["teamid"], score])

                score_list = sorted(score_list, key=itemgetter(1))                  # sorting list in decreasing order
                score_list = score_list[::-1]

                displaylist = []
                for i in range(0, num_scoreboard):
                    try:
                        displaylist.append(str(i+1)+". Team **"+score_list[i][0]+'** with **'+str(score_list[i][1])+"** puzzle{} completed.".format("" if score_list[i][1] == 1 else "s"))
                    except IndexError:
                        pass
                embed = discord.Embed(title="PixarHunt Top "+ str(num_scoreboard) +" Leaderboard",
                                      description="\n".join(displaylist), color=0xffa500)

                await message.channel.send(embed=embed)

            elif message.content.startswith('!puzz'):
                if team == -1:
                    await message.channel.send(
                        'Sorry, you are not registered. If you think this is an error, contact a PuzzleSoc Exec.')
                else:
                    message.content = message.content.lower()
                    channel = client.get_channel(CHANNEL_ID)
                    channel2 = client.get_channel(CHANNEL_ID_2)
                    puzzle_no = message_words[0][-1]
                    if puzzle_no not in '12345':
                        await message.channel.send("Use !help to see how to use this bot.")
                        return
                    else:
                        puzzle_no = int(puzzle_no)
                    try:
                        if message.content[7:] == puzzle_answers[puzzle_no-1]:
                            update_field(team, 'solve{}'.format(str(puzzle_no)), 1)
                            embed = discord.Embed(color=0x00ff00)
                            embed.add_field(name="Correct!", value="Your answer to puzzle {} is correct!\n"
                                                                   "Puzzle solved for **{}**.".format(puzzle_no, teamlist[str(team)]),
                                            inline=False)
                            await message.channel.send(embed=embed)
                            await channel.send(f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** solved puzzle {puzzle_no} with answer '**{message.content[7:]}**'!")
                            await channel2.send(
                                f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** solved puzzle {puzzle_no} with answer '**{message.content[7:]}**'!")
                            if check_score(team) == 5:
                                await message.channel.send("Congratulations on solving all 5 puzzles! Here's the meta!\n" + metalink)
                                await channel.send(f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** has reached the meta!")
                                await channel2.send(
                                    f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** has reached the meta!")
                        else:
                            embed = discord.Embed(color=0xff0000)
                            embed.add_field(name="Incorrect.", value="Your answer to puzzle {} is incorrect.".format(puzzle_no),
                                            inline=False)
                            await message.channel.send(embed=embed)
                            await channel.send(f"<t:{int(time.time())}> Team **{teamlist[str(team)]}** has incorrectly attempted puzzle {puzzle_no} with answer '**{message.content[7:]}**'.")
                    except IndexError:
                        await message.channel.send("Use !help to see how to use this bot.")

            elif message.content == '!progress':
                if team == -1:
                    await message.channel.send(
                        'Sorry, you are not registered. If you think this is an error, contact a PuzzleSoc Exec.')
                else:
                    embed = discord.Embed(title="Team {} Progress".format(get_field(team, 'teamname')), color=0x7289DA)
                    embed.add_field(name='**  **1\t 2\t\u20093\t\u20094\t\u200A5', value=" ".join([':green_square:' if get_field(team, 'solve{}'.format(str(i+1))) == '1' else ":black_large_square:" for i in range(5)]))
                    embed.add_field(name="Hints", value="{} hints remaining.".format(get_field(team, "hints")),
                                    inline=False)
                    await message.channel.send(embed=embed)

            elif message.content == '!getmeta':
                if team == -1:
                    await message.channel.send(
                        'Sorry, you are not registered. If you think this is an error, contact a PuzzleSoc Exec.')
                else:
                    x = check_score(team)
                    if x == 5:
                        await message.channel.send("Congratulations! Here's the meta! <:v2:870586401018753044>\n" + metalink)
                    else:
                        await message.channel.send("You still have {} puzzle{} to go.".format(5-x, "" if x == 4 else "s"))

            else:
                await message.channel.send("Use !help to see how to use this bot.")


intents = discord.Intents().all()
activity = discord.Activity(name='with puzzles', type=discord.ActivityType.custom)
client = MyClient(intents=intents, activity=activity)
client.run(TOKEN)

