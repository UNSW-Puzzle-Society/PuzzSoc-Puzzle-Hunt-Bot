import csv
from operator import itemgetter

import discord
from discord.ext import commands

client = discord.Client()
with open('.token', 'r') as f:
    TOKEN = f.read()

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content
    puzzles = {"!puzz1": 'sampleanswer',
               "!puzz2": 'sampleanswer',
               "!puzz3": 'sampleanswer',
               "!puzz4": 'sampleanswer',
               "!puzz5": 'sampleanswer',
               }
    combinedanswer = 'sampleanswer'
    metalink = 'https://google.com'

    teamlist = {"1": "YES MAN",
                "2": "NO MAN",
                "3": "uwu doki doki nyan nyan neko girls nya",
                "4": "yes man",
                "5": "hoes",
                "6": "yes man",
                "7": "yes man",
                "8": "maybe man",
                "9": "yes man",
                "10": "yes man",
                "11": "timmy fan club uwu",
                "12": "team number 12",
                }

    if msg.startswith('!'):
        if message.content == '!help':
            embed = discord.Embed(title="Help Page", color=0x000000)
            embed.add_field(name="!puzz[number] [answer]",
                            value="Check the answer of your [number]th puzzle.\nE.g. !puzz1 sampleanswer",
                            inline=False)
            embed.add_field(name="!getmeta [answer]",
                            value="Get the meta, if you've answered all 5 puzzles correctly!\nEnter all 5 puzzle answers in order combined, lowercase without spaces.\nE.g. !getmeta sampleanswer",
                            inline=False)
            await message.channel.send(embed=embed)

        elif message.content == '!top':
            top_ten = []
            score_list = []
            with open('users.csv', newline='') as f:
                for team in csv.DictReader(f):
                    score = int(team["solve1"]) + int(team["solve2"]) + int(team["solve3"]) + int(team["solve4"]) + int(
                        team["solve5"])
                    score_list.append([teamlist[team["teamid"]], score])

            score_list = sorted(score_list, key=itemgetter(1))
            for n in range(1, 11):
                top_ten.append(score_list[-n])
            embed = discord.Embed(title="PixarHunt Top 10 Leaderboard",
                                  description="1. Team **" + top_ten[0][0] + '** with **' + str(
                                      top_ten[0][1]) + "** puzzles completed.\n"
                                                       "2. Team **" + top_ten[1][0] + '** with **' + str(
                                      top_ten[1][1]) + "** puzzles completed.\n"
                                                       "3. Team **" + top_ten[2][0] + '** with **' + str(
                                      top_ten[2][1]) + "** puzzles completed.\n"
                                                       "4. Team **" + top_ten[3][0] + '** with **' + str(
                                      top_ten[3][1]) + "** puzzles completed.\n"
                                                       "5. Team **" + top_ten[4][0] + '** with **' + str(
                                      top_ten[4][1]) + "** puzzles completed.\n"
                                                       "6. Team **" + top_ten[5][0] + '** with **' + str(
                                      top_ten[5][1]) + "** puzzles completed.\n"
                                                       "7. Team **" + top_ten[6][0] + '** with **' + str(
                                      top_ten[6][1]) + "** puzzles completed.\n"
                                                       "8. Team **" + top_ten[7][0] + '** with **' + str(
                                      top_ten[7][1]) + "** puzzles completed.\n"
                                                       "9. Team **" + top_ten[8][0] + '** with **' + str(
                                      top_ten[8][1]) + "** puzzles completed.\n"
                                                       "10. Team **" + top_ten[9][0] + '** with **' + str(
                                      top_ten[9][1]) + "** puzzles completed.", color=0xffa500)

            await message.channel.send(embed=embed)

        elif len(message.content.split()) == 2:
            verb = message.content.split()[0]
            noun = message.content.split()[1]

            if verb in puzzles:
                if noun == puzzles[verb]:
                    await message.channel.send('Correct!')
                else:
                    await message.channel.send('Incorrect :(')
            elif verb == '!getmeta':
                if noun == combinedanswer:
                    await message.channel.send('Correct! Metapuzzle link:\n' + metalink)
                else:
                    await message.channel.send('Incorrect :(')
            else:
                await message.channel.send('Incorrect Usage!\nType !help for usage.')

        else:
            await message.channel.send('Incorrect Usage!\nType !help for usage.')


bot.run(TOKEN)
