import csv
import datetime
import os
from operator import itemgetter
from random import randint

import discord
from dateutil import parser


def read_token():
    with open('.token', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


def check_user(id, field):
    with open('users.csv', newline='') as users:
        for user in csv.DictReader(users):
            if int(user['user']) == id:
                return user[field]


def generate_words(number):
    words_list = []
    random_words = []
    with open('words.txt', 'r') as words:
        for word in words:
            words_list.append(''.join(list(word)[:-1]))
    while len(random_words) != number:
        random_no = randint(0, 2000)
        if words_list[random_no] not in random_words:
            random_words.append(words_list[random_no])
    with open('trigger_words.txt', 'w') as trigger_words:
        for word in random_words:
            trigger_words.write(word + '\n')


def change_file(id, field, new):
    field_pos = {'user': 0, 'bucks': 1, 'state': 2, 'immunity': 3, 'usage': 4, 'coughs': 5, 'last_collection': 6}
    with open('users.csv', 'r') as old_file, open('updated_users.csv', 'w+') as new_file:
        for row in old_file:
            row_content = row.split(',')
            if row_content[0] == str(id):
                row_content[field_pos[field]] = str(new)
                new_file.write(str(','.join(row_content)))
            else:
                new_file.write(row)
    os.remove('users.csv')
    os.rename('updated_users.csv', 'users.csv')


class MyClient(discord.Client):
    async def on_ready(self):
        print('\nCoronaBot Online')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        message.content = message.content.lower()
        message_words = message.content.split()
        trigger_words = []
        with open('trigger_words.txt', 'r') as file:
            for trigger_word in file:
                trigger_words.append(''.join(list(trigger_word)[:-1]))
            for word in message_words:
                if word in trigger_words:
                    if check_user(message.author.id, 'state') == 'healthy':
                        if int(check_user(message.author.id, 'usage')) > 0:
                            if randint(1, 100) > int(check_user(message.author.id, 'immunity')):
                                change_file(message.author.id, 'state', 'infected')
                                change_file(message.author.id, 'immunity', 0)
                                change_file(message.author.id, 'usage', 0)
                                embed = discord.Embed(title="Infected!",
                                                      description='**' + message.author.name + "** hit a trigger word: **" + word + '**. \n **' + message.author.name + "**'s immunity was not strong enough. \nA new list of 20 words will now be generated.",
                                                      color=0xff0000)
                                generate_words(20)
                                await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                            else:
                                embed = discord.Embed(title="Close Call!",
                                                      description='**' + message.author.name + "** hit a trigger word: **" + word + '**. \n **' + message.author.name + "**'s " + str(
                                                          check_user(message.author.id,
                                                                     'immunity')) + "% immunity protected them from infection, for now... \nA new list of 20 words will now be generated.",
                                                      color=0x00ff00)
                                await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                                generate_words(20)
                                change_file(message.author.id, 'usage', int(check_user(message.author.id, 'usage')) - 1)
                                if int(check_user(message.author.id, 'usage')) == 0:
                                    change_file(message.author.id, 'immunity', 0)
                        else:
                            embed = discord.Embed(title="Infected!",
                                                  description='**' + message.author.name + "** hit a trigger word: **" + word + '**. \nA new list of 20 words will now be generated.',
                                                  color=0xff0000)
                            await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                            generate_words(20)
                            change_file(message.author.id, 'state', 'infected')

        if message.content.startswith('*'):
            if message.content == '*help':
                embed = discord.Embed(title="Help Page", color=0xffa500)
                embed.add_field(name="*bal [user]", value="Check the balance of target user.", inline=False)
                embed.add_field(name="*baltop", value="Check the top 5 balances.", inline=False)
                embed.add_field(name="*stats", value="Check the current statistics.", inline=False)
                embed.add_field(name="*profile [user]", value="Check the profile of target user.", inline=False)
                embed.add_field(name="*collect", value="Collect free nCoV-Bucks every 6 hours.", inline=False)
                embed.add_field(name="*pay [user] [amount]", value="Transfer nCoV-Bucks to target user.", inline=False)
                embed.add_field(name="*shop", value="Buy items using nCoV-Bucks.", inline=False)
                embed.add_field(name="*buy [item no]", value="Buys item from shop.", inline=False)
                embed.add_field(name="*coughon [user]", value="Use a cough to pass on your infection to a target user.",
                                inline=False)
                embed.add_field(name="*support", value="Contact support.", inline=False)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*bal':
                if check_user(message.author.id, 'state') == 'healthy':
                    color = 0x00ff00
                else:
                    color = 0xff0000
                member = str(message.guild.get_member(message.author.id))
                embed = discord.Embed(title="Balance (" + member + ")", color=color)
                embed.add_field(name="nCoV-Bucks", value=str(check_user(message.author.id, 'bucks')) + ' ☣️',
                                inline=False)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content.startswith('*bal <@'):
                check_id = int(''.join(list(message.content)[-19:-1]))
                if check_user(check_id, 'state') == 'healthy':
                    color = 0x00ff00
                else:
                    color = 0xff0000

                member = str(message.guild.get_member(check_id))
                embed = discord.Embed(title="Balance (" + member + ")", color=color)
                embed.add_field(name="nCoV-Bucks", value=str(check_user(check_id, 'bucks')) + ' ☣️', inline=False)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*baltop':

                top_list = []
                top_five = []
                for member in message.guild.members:
                    top_list.append([member.name, int(check_user(member.id, 'bucks'))])
                top_list = sorted(top_list, key=itemgetter(1))
                for n in range(1, 6):
                    top_five.append(top_list[-n])
                embed = discord.Embed(title="Highest Balances",
                                      description="1. **" + top_five[0][0] + '** with **' + str(
                                          top_five[0][1]) + "** ☣️.\n"
                                                            "2. **" + top_five[1][0] + '** with **' + str(
                                          top_five[1][1]) + "** ☣️.\n"
                                                            "3. **" + top_five[2][0] + '** with **' + str(
                                          top_five[2][1]) + "** ☣️.\n"
                                                            "4. **" + top_five[3][0] + '** with **' + str(
                                          top_five[3][1]) + "** ☣️.\n"
                                                            "5. **" + top_five[4][0] + '** with **' + str(
                                          top_five[4][1]) + "** ☣️.", color=0xffa500)

                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*stats':
                healthy = []
                infected = []
                healthy_money = 0
                infected_money = 0
                for member in message.guild.members:
                    if check_user(member.id, 'state') == 'healthy':
                        healthy.append(member.name)
                        healthy_money += int(check_user(member.id, 'bucks'))
                    else:
                        infected.append(member.name)
                        infected_money += int(check_user(member.id, 'bucks'))
                stat_description = '**Healthy**'
                for person in healthy:
                    stat_description = stat_description + '\n' + person
                stat_description = stat_description + '\n\n**Infected**'
                for person in infected:
                    stat_description = stat_description + '\n' + person
                stat_description = stat_description + '\n\n'
                stat_description = stat_description + 'Combined Healthy nCoV-Bucks: **' + str(
                    healthy_money) + "** ☣️.\n"
                stat_description = stat_description + 'Combined Infected nCoV-Bucks: **' + str(
                    infected_money) + "** ☣️."
                embed = discord.Embed(title="Statistics", description=stat_description, color=0xffa500)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*profile':
                if check_user(message.author.id, 'state') == 'healthy':
                    color = 0x00ff00
                else:
                    color = 0xff0000
                member = str(message.guild.get_member(message.author.id))
                embed = discord.Embed(title="Profile (" + member + ")", color=color)
                embed.add_field(name="State", value=str(check_user(message.author.id, 'state').title()), inline=False)
                embed.add_field(name="nCoV-Bucks", value=str(check_user(message.author.id, 'bucks')) + ' ☣️',
                                inline=False)
                embed.add_field(name="Coughs", value=str(check_user(message.author.id, 'coughs') + ' 🤧'), inline=False)
                embed.add_field(name="Current Face Mask", value='% Immunity: ' + str(
                    check_user(message.author.id, 'immunity')) + '\nDurability: ' + str(
                    check_user(message.author.id, 'usage')), inline=False)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content.startswith('*profile <@'):
                check_id = int(''.join(list(message.content)[-19:-1]))
                if check_user(check_id, 'state') == 'healthy':
                    color = 0x00ff00
                else:
                    color = 0xff0000

                member = str(message.guild.get_member(check_id))
                embed = discord.Embed(title="Profile (" + member + ")", color=color)
                embed.add_field(name="State", value=str(check_user(check_id, 'state').title()), inline=False)
                embed.add_field(name="nCoV-Bucks", value=str(check_user(check_id, 'bucks')) + ' ☣️', inline=False)
                embed.add_field(name="Coughs", value=str(check_user(check_id, 'coughs') + ' 🤧'), inline=False)
                embed.add_field(name="Current Face Mask",
                                value='% Immunity: ' + str(check_user(check_id, 'immunity')) + '\nDurability: ' + str(
                                    check_user(check_id, 'usage')), inline=False)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*collect':
                if datetime.datetime.now() - parser.parse(
                        check_user(message.author.id, 'last_collection')) >= datetime.timedelta(hours=6):
                    collected = randint(50, 200)
                    if collected % 10 == 0:
                        embed = discord.Embed(title="Collection Successful",
                                              description="JACKPOT! You collected **1000** nCoV-Bucks.",
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) + 1000)
                        change_file(message.author.id, 'last_collection', str(datetime.datetime.now()) + '\n')
                    else:
                        embed = discord.Embed(title="Collection Successful",
                                              description="You collected **" + str(collected) + "** nCoV-Bucks.",
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) + collected)
                        change_file(message.author.id, 'last_collection', str(datetime.datetime.now()) + '\n')
                else:
                    embed = discord.Embed(title="Collection Failed",
                                          description="You have collected nCoV-Bucks in the past 6 hours.",
                                          color=0xff0000)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content.startswith('*pay <@'):
                pay_id = ''.join(
                    list(message.content)[list(message.content).index(">") - 18:list(message.content).index(">")])
                amount = ''.join(list(message.content)[list(message.content).index(">") + 2:])
                try:
                    if int(amount) >= 0:
                        if int(check_user(message.author.id, 'bucks')) >= int(amount):
                            if str(check_user(message.author.id, 'state')) == str(check_user(int(pay_id), 'state')):
                                embed = discord.Embed(title="Transfer Successful",
                                                      description='**' + str(message.author.name) + '** paid **' + str(
                                                          amount) + '** ☣️ to **' + str(
                                                          message.guild.get_member(int(pay_id))) + '**.',
                                                      color=0x00ff00)
                                await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                                change_file(message.author.id, 'bucks',
                                            int(check_user(message.author.id, 'bucks')) - int(amount))
                                change_file(int(pay_id), 'bucks', int(check_user(int(pay_id), 'bucks')) + int(amount))
                            else:
                                embed = discord.Embed(title="Transfer Failed",
                                                      description='You can only pay people in the same state (healthy or infected) as you.',
                                                      color=0xff0000)
                                await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                        else:
                            embed = discord.Embed(title="Transfer Failed",
                                                  description='You do not have enough money, brokeass.',
                                                  color=0xff0000)
                            await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                    else:
                        embed = discord.Embed(title="Transfer Failed",
                                              description='You can only pay in positive amounts.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                except ValueError:
                    embed = discord.Embed(title="Transfer Failed",
                                          description='You can only pay in integer amounts.',
                                          color=0xff0000)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*shop':
                if check_user(message.author.id, 'state') == 'healthy':
                    embed = discord.Embed(title="Shop (Healthy)", color=0x00ff00)
                    embed.add_field(name="1. Disposable Face Mask (50 ☣️)",
                                    value="Description: *A disposable face mask for minimal protection.*\n"
                                          "Immunity: **50%**\n"
                                          "Durability: **2**\n————————————————————————————", inline=False)
                    embed.add_field(name="2. N95 Face Mask (200 ☣️)",
                                    value="Description: *Better protection, more durable, higher cost.*\n"
                                          "Immunity: **80%**\n"
                                          "Durability: **5**\n————————————————————————————", inline=False)
                    embed.add_field(name="3. Gas Mask (1000 ☣️)",
                                    value="Description: *It's literally just a gas mask.*\n"
                                          "Immunity: **99%**\n"
                                          "Durability: **20**", inline=False)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                else:
                    embed = discord.Embed(title="Shop (Infected)", color=0xff0000)
                    embed.add_field(name="1. Slight Cough (50 ☣️)",
                                    value="Description: *Bad coughing etiquette transmits diseases.*\n"
                                          "Effect: **+1** Cough\n————————————————————————————", inline=False)
                    embed.add_field(name="2. Pneumonia (300 ☣️)",
                                    value="Description: *Get pneumonia now for only $300!*\n"
                                          "Effect: **+8** Cough\n————————————————————————————", inline=False)
                    embed.add_field(name="3. Pandemic (8000 ☣️)",
                                    value="Description: *INFECT. EVERYONE. 100%.*\n"
                                          "Effect: Infected team wins. (everyone dies 🙂)", inline=False)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*buy 1':
                if check_user(message.author.id, 'state') == 'healthy':
                    if int(check_user(message.author.id, 'bucks')) >= 50:
                        change_file(message.author.id, 'immunity', 50)
                        change_file(message.author.id, 'usage', 2)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) - 50)
                        embed = discord.Embed(title="Purchase Successful",
                                              description='You bought item 1 from the Shop (Healthy).',
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                    else:
                        embed = discord.Embed(title="Purchase Failed",
                                              description='You do not have enough money, brokeass.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                else:
                    if int(check_user(message.author.id, 'bucks')) >= 50:
                        change_file(message.author.id, 'coughs', int(check_user(message.author.id, 'coughs')) + 1)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) - 50)
                        embed = discord.Embed(title="Purchase Successful",
                                              description='You bought item 1 from the Shop (Infected).',
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                    else:
                        embed = discord.Embed(title="Purchase Failed",
                                              description='You do not have enough money, brokeass.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*buy 2':
                if check_user(message.author.id, 'state') == 'healthy':
                    if int(check_user(message.author.id, 'bucks')) >= 200:
                        change_file(message.author.id, 'immunity', 80)
                        change_file(message.author.id, 'usage', 5)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) - 200)
                        embed = discord.Embed(title="Purchase Successful",
                                              description='You bought item 2 from the Shop (Healthy).',
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                    else:
                        embed = discord.Embed(title="Purchase Failed",
                                              description='You do not have enough money, brokeass.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                else:
                    if int(check_user(message.author.id, 'bucks')) >= 300:
                        change_file(message.author.id, 'coughs', int(check_user(message.author.id, 'coughs')) + 8)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) - 300)
                        embed = discord.Embed(title="Purchase Successful",
                                              description='You bought item 2 from the Shop (Infected).',
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                    else:
                        embed = discord.Embed(title="Purchase Failed",
                                              description='You do not have enough money, brokeass.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*buy 3':
                if check_user(message.author.id, 'state') == 'healthy':
                    if int(check_user(message.author.id, 'bucks')) >= 1000:
                        change_file(message.author.id, 'immunity', 99)
                        change_file(message.author.id, 'usage', 20)
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) - 1000)
                        embed = discord.Embed(title="Purchase Successful",
                                              description='You bought item 3 from the Shop (Healthy).',
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                    else:
                        embed = discord.Embed(title="Purchase Failed",
                                              description='You do not have enough money, brokeass.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                else:
                    if int(check_user(message.author.id, 'bucks')) >= 8000:
                        change_file(message.author.id, 'bucks', int(check_user(message.author.id, 'bucks')) - 8000)
                        embed = discord.Embed(title="Purchase Successful",
                                              description='You bought item 3 from the Shop (Infected).\n\n**NOVEL CORONAVIRUS IS NOW A PANDEMIC.**\n**EVERYONE IS INFECTED.**\n**INFECTED TEAM WINS.**',
                                              color=0x00ff00)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                        for member in message.guild.members:
                            change_file(member.id, 'state', 'infected')


                    else:
                        embed = discord.Embed(title="Purchase Failed",
                                              description='You do not have enough money, brokeass.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content.startswith('*coughon <@'):
                cough_id = int(''.join(list(message.content)[-19:-1]))
                if int(check_user(message.author.id, 'coughs')) > 0:
                    if check_user(message.author.id, 'state') == 'infected':
                        if check_user(cough_id, 'state') == 'healthy':
                            member = str(message.guild.get_member(cough_id))
                            if int(check_user(cough_id, 'usage')) > 0:
                                if randint(1, 100) > int(check_user(cough_id, 'immunity')):
                                    embed = discord.Embed(title="Infected!",
                                                          description='**' + message.author.name + "** infected **" + member + '**. \n **' + member + "**'s immunity was not strong enough.",
                                                          color=0x00ff00)
                                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                                    change_file(message.author.id, 'coughs',
                                                int(check_user(message.author.id, 'coughs')) - 1)
                                    change_file(cough_id, 'state', 'infected')
                                    change_file(cough_id, 'immunity', 0)
                                    change_file(cough_id, 'usage', 0)
                                else:
                                    embed = discord.Embed(title="Close Call!",
                                                          description='**' + message.author.name + "** coughed on **" + member + '**. \n **' + member + "**'s " + str(
                                                              check_user(cough_id,
                                                                         'immunity')) + "% immunity protected them from infection, for now...",
                                                          color=0xff0000)
                                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                                    change_file(message.author.id, 'coughs',
                                                int(check_user(message.author.id, 'coughs')) - 1)
                                    change_file(cough_id, 'usage', int(check_user(cough_id, 'usage')) - 1)
                                    if int(check_user(cough_id, 'usage')) == 0:
                                        change_file(cough_id, 'immunity', 0)
                            else:
                                embed = discord.Embed(title="Infected!",
                                                      description='**' + message.author.name + "** infected **" + member + '**.',
                                                      color=0x00ff00)
                                await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                                change_file(message.author.id, 'coughs',
                                            int(check_user(message.author.id, 'coughs')) - 1)
                                change_file(cough_id, 'state', 'infected')
                                change_file(cough_id, 'immunity', 0)
                                change_file(cough_id, 'usage', 0)
                        else:
                            embed = discord.Embed(title="Cough Wasted",
                                                  description='Target is already infected, you can only infect healthy targets.',
                                                  color=0xff0000)
                            await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                            change_file(message.author.id, 'coughs', int(check_user(message.author.id, 'coughs')) - 1)
                    else:
                        embed = discord.Embed(title="Cough Wasted",
                                              description='You are still healthy, coughing on target has no effect.',
                                              color=0xff0000)
                        await message.channel.send('{0.author.mention}'.format(message), embed=embed)
                        change_file(message.author.id, 'coughs', int(check_user(message.author.id, 'coughs')) - 1)
                else:
                    embed = discord.Embed(title="Cough Failed",
                                          description='You have no coughs left, buy some coughs in the shop.',
                                          color=0xff0000)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*support':
                embed = discord.Embed(title="Customer Support", description="Send a PM to Eric lol.", color=0xffa500)
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*reset':
                if message.author.id == 230480466023546881:
                    for member in message.guild.members:
                        with open('users.csv', 'a') as users:
                            writer = csv.DictWriter(users, fieldnames=['user', 'bucks', 'state',
                                                                       'immunity', 'usage', 'coughs',
                                                                       'last_collection'])
                            writer.writerow({'user': member.id,
                                             'bucks': 50,
                                             'state': 'healthy',
                                             'immunity': 0,
                                             'usage': 0,
                                             'coughs': 0,
                                             'last_collection': datetime.datetime.now()})
                    embed = discord.Embed(title="Success",
                                          description="Member stats has been reset to default.",
                                          color=0x00ff00)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                else:
                    embed = discord.Embed(title="Denied", description="You do not have perms for this command.",
                                          color=0xff0000)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            elif message.content == '*generate':
                if message.author.id == 230480466023546881:
                    generate_words(20)
                    embed = discord.Embed(title="Success",
                                          description="Twenty random words have been generated.",
                                          color=0x00ff00)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

                else:
                    embed = discord.Embed(title="Denied", description="You do not have perms for this command.",
                                          color=0xff0000)
                    await message.channel.send('{0.author.mention}'.format(message), embed=embed)

            else:
                embed = discord.Embed(title="Invalid Command!", color=0xffa500)
                embed.add_field(name="*help", value="Open help page.")
                await message.channel.send('{0.author.mention}'.format(message), embed=embed)


token = read_token()
client = MyClient()
client.run(token)
