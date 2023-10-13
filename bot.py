import asyncio
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.parent.__str__())

import httpx
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

from codeforces import Codeforces
from codeforces.models import *

api_id = 1851270 
api_hash = "hash"
bot_token = "token"

cf = Codeforces()
app = Client("a2svcontestanalysisbot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    await message.reply(
            f"✨ Hi __[{name}](tg://user?id={user_id})__, Welcome!\n\nClick the button below to continue.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Continue »",
                            callback_data="contest,next,-1"
                        ),
                    ]
                ]
            )
        )

@app.on_message(filters.command("help"))
async def help(client, message):
    await message.reply("Contact me @dryeab for any help, feature request or bug report.")
    
@app.on_callback_query(filters.regex('^contest,next,'))
async def next(client, update):

    contests = list(Contest.contests().keys())
    
    current = int(update.data.split(',')[-1]) + 1
    current_contests = contests[current*3:current*3+3]
    
    if len(current_contests) == 0:
        await update.answer("It looks like you have reached the end")
        return 
    
    keyboard = [
                    *([
                        InlineKeyboardButton(
                            f"{current_contests[i]}",
                            callback_data=f"contest,analysis,{current_contests[i]}"
                        ) for i in range(j, min(len(current_contests), j + 3))
                    ] for j in range(0, len(current_contests), 3)),
                    [
                        InlineKeyboardButton(
                            "« Prev",
                            callback_data=f"contest,prev,{current}"
                        ),
                        InlineKeyboardButton(
                            "Next »",
                            callback_data=f"contest,next,{current}"
                        ) 
                    ]
                ]
    
    await update.edit_message_text("Please select the contest number that you would like to examine and analyze.", reply_markup=InlineKeyboardMarkup(keyboard),)

@app.on_callback_query(filters.regex('^contest,prev,'))
async def prev(client, update):
    
    contests = list(Contest.contests().keys())
    
    current = int(update.data.split(',')[-1]) - 1
    
    if current < 0:
        await update.answer("It looks like you are at the beginning")
        return 
    
    current_contests = contests[current*3:current*3+3]
    
    keyboard = [
                    *([
                        InlineKeyboardButton(
                            f"{current_contests[i]}",
                            callback_data=f"contest,analysis,{current_contests[i]}"
                        ) for i in range(j, min(len(current_contests), j + 3))
                    ] for j in range(0, len(current_contests), 3)),
                    [
                        InlineKeyboardButton(
                            "« Prev",
                            callback_data=f"contest,prev,{current}"
                        ),
                        InlineKeyboardButton(
                            "Next »",
                            callback_data=f"contest,next,{current}"
                        ) 
                    ]
                ]
    
    await update.edit_message_text("Please select the contest number that you would like to examine and analyze.", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex('^contest,analysis,\w+$'))
async def analysis(client, update):
    
    keyboard = [
        [
            InlineKeyboardButton(
                            "General",
                            callback_data=update.data + f","
                        )    
        ],
        [ 
         
         InlineKeyboardButton(
                            "G47",
                            callback_data=update.data + f",47"
                        ) ,
         InlineKeyboardButton(
                            "G48",
                            callback_data=update.data + f",48"
                        ) 
        ],
        [
            InlineKeyboardButton(
                            "G49",
                            callback_data=update.data + f",49"
                        ) ,
            InlineKeyboardButton(
                            "G4A",
                            callback_data=update.data + f",4A"
                        ) 
        ],
        [
            InlineKeyboardButton(
                            "« Back",
                            callback_data="contest,next,-1"
                        ) ,
        ],
        ]
    
    await update.edit_message_text("Choose the group you would like to get the anlysis for...", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex('^contest,analysis,\w+,\w*$'))
async def group_analysis(client, update):
    
    contest_no, group = update.data.split(',')[-2:]
    
    gym_id = Contest.contests()[contest_no]
    
    G = group or "General"
    
    QBA = ''.join(list(map(
        lambda x: f"\n{x[0]}: {x[1]} students solved",
        cf.question_based_analysis(gym_id, group))))
    
    msg = f"**{G}:**  Contest Analysis for contest {contest_no}"
    msg += "\n\nHere is the number of the students who solved each question:\n ```"
    msg += QBA
    msg += "```\n\n__Click one of the buttons below for more...__" 
    
    keyboard = [
        [
            InlineKeyboardButton(
                            "🎖 TOP 5",
                            callback_data=update.data + ",top5"
                        ),
            InlineKeyboardButton(
                            "📜 Attendance",
                            callback_data=update.data + ",attendance"
                        )        
        ],
        [
            InlineKeyboardButton(
                            "✅ No of Questions Solved",
                            callback_data=update.data + ",solves"
                        )     
        ],
        [
            InlineKeyboardButton(
                            "« Back",
                            callback_data=','.join(update.data.split(',')[:-1])
                        ),
        ],
        ]
    
    await update.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex('^contest,analysis,\w+,\w*,top5$'))
async def top5(client, update):
    """Returns the top 5 performers of a given contest"""
    
    contest_no, group = update.data.split(',')[-3:-1]
    
    gym_id = Contest.contests()[contest_no]
    
    G = group or "General"
    
    msg = f"🎖 **TOP 5:**  {G}\n```\n"
    msg += '\n'.join(cf.top_5(gym_id, group))
    msg += ' \n```'
    msg += '\nGood Job. Keep up the good work!!'
    
    keyboard = [
        [
            InlineKeyboardButton(
                            "Share",
                            switch_inline_query=msg
                        ),
            InlineKeyboardButton(
                            "« Back",
                            callback_data=','.join(update.data.split(',')[:-1])
                        )        
        ],
        ]
    
    await update.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex('^contest,analysis,\w+,\w*,solves$'))
async def solves(client, update):
    """Returns the number of solved problems for a given contest"""
    
    contest_no, group = update.data.split(',')[-3:-1]
    
    gym_id = Contest.contests()[contest_no]
    
    G = group or "General"
    
    solves = cf.solves(gym_id, group)
    s_solves = list(map(lambda x: f"{x[0]}: {x[1]}", solves))
    
    msg = f"🎖 **Number of Questions Solved:**  {G}\n```\n"
    msg += '\n'.join(s_solves)
    msg += ' \n```\n\n**Average:** %.1f' %(sum(x[1] for x in solves) / len(solves))
    
    keyboard = [
        [
            InlineKeyboardButton(
                            "« Back",
                            callback_data=','.join(update.data.split(',')[:-1])
                        )        
        ],
    ]
    
    await update.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    
@app.on_callback_query(filters.regex('^contest,analysis,\w+,\w*,attendance$'))
async def group_attendance(client, update):
    """Returns the list of people who didn't attend the contest"""
    
    contest_no, group = update.data.split(',')[-3:-1]
    
    gym_id = Contest.contests()[contest_no]
    
    G = group or "General"
    
    participated, all = cf.attendance(gym_id, group)
    percentage = float("%.1f" %((participated / all) * 100))

    msg = f"📜 **Attendance:**  {G}\n\n"
    msg += f"📊 Total Attendance: __{percentage}%__\n"
    msg += f"\n**{all - participated}** students haven't participated.```\n"
    msg += '\n'.join(cf.not_attended(gym_id, group))
    msg += '\n\n```'
    msg += "__Let's remind them to take it virtually at least!!__"
    
    keyboard = [
            [
                InlineKeyboardButton(
                                "« Back",
                                callback_data=','.join(update.data.split(',')[:-1])
                            )        
            ],
        ]
    
    await update.edit_message_text(msg,reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@app.on_inline_query()
def answer_inline_query(client, inline_query):
    """Answer all inline queries"""
    
    results = [
        InlineQueryResultArticle(
            id="1",
            title="TOP 5 Performers",
            description="Here are the top 5 Performers",
            input_message_content=InputTextMessageContent(inline_query.query)
        )
    ]

    client.answer_inline_query(inline_query.id, results)

# asyncio.run(cf.import_all())
app.run()