import datetime
import logging
import inflect
import telegram
import os
import constants

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

PORT = int(os.environ.get('PORT', constants.PORT_NUMBER))
bot = telegram.Bot(token=constants.API_KEY)

users = []

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# States for conversation

CURRENT_GPA, TOTAL_MCS_REQUIRED, TOTAL_MCS_TAKEN, TARGET_GPA = range(4)


def start(update, context):
    user = update.message.from_user

    if not user.username in users:
        users.append(user.username)
        logger.info("User %s started the conversation.", user.username)
        logger.info("Users to date: %s", len(users))

    update.message.reply_text(
        "Hey " + user.first_name +
        "! Let's see what's needed to get that ideal CAP! So what's your CAP as of now?"
    )
    return CURRENT_GPA


def collect_cgpa(update, context):
    cgpa = update.message.text
    user_data = context.user_data
    context.user_data['CGPA'] = float(cgpa)

    if (float(cgpa) < 0.00 or float(cgpa) > 5.00):
        update.message.reply_text("Hmmm... Your CAP must be within 0 and 5! \n\n"
                                  "Please enter your cumulative CAP again"
                                  )
        return CURRENT_GPA
    else:
        update.message.reply_text("Your CAP as of right now is " + cgpa +
                                  "\n\nWhat is the total number of MCs you are required to clear? "
                                  )
        return TOTAL_MCS_REQUIRED


def collect_MCs_required(update, context):
    mR = update.message.text
    user_data = context.user_data
    user = update.message.from_user
    context.user_data['mR'] = int(mR)

    if (int(mR) < 100 or int(mR) > 250):
        update.message.reply_text(
            "Sorry " + user.first_name + ", are you really studying in NUS?")
        user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text("Total MCs you have to take is " + mR
                                  + "\n\nHow many MCs have you taken?"
                                  )
        return TOTAL_MCS_TAKEN


def collect_MCs_taken(update, context):
    tT = update.message.text
    user_data = context.user_data
    user = update.message.from_user
    context.user_data['tT'] = int(tT)

    if (int(tT) < 0 or int(tT) > 250):
        update.message.reply_text(
            "Sorry " + user.first_name + ", are you really studying in NUS?")
        user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text("Total MCs you have taken is " + tT
                                  + "\n\nWhat's your target CAP when you graduate?"
                                  )
        return TARGET_GPA


def collect_targetgpa(update, context):
    targetgpa = update.message.text
    user = update.message.from_user
    context.user_data['targetgpa'] = float(targetgpa)

    if (float(targetgpa) < 0.0 or float(targetgpa) > 5.0):
        update.message.reply_text("Hmmm... CAP must be within 0 and 5! \n\n"
                                  "Please enter your cumulative CAP again!"
                                  )
        return TARGET_GPA
    else:
        update.message.reply_text(
            "Your target CAP is " + str(targetgpa))

        user_data = context.user_data

        cgpa = user_data['CGPA']
        targetGPA = user_data['targetgpa']
        total_Taken = user_data['tT']
        total_Required = user_data['mR']

        number_left = total_Required - total_Taken

        target_total = targetGPA * total_Required
        current_total = cgpa * total_Taken
        remaining_total = target_total - current_total

        ideal_GPA = round((remaining_total/number_left), 2)

        if (ideal_GPA > 5.0):
            update.message.reply_text(
                "\n\nI am sorry " + user.first_name + ", let's set a more realistic target to work towards to again! \nType '/start' to calculate again")
        elif (ideal_GPA < 0.0):
            update.message.reply_text(
                "\n\nHey " + user.first_name + ", you are doing great now! Let's aim higher! \nType '/start' to calculate again")
        else:
            update.message.reply_text(
                "\n\nYou should achieve an average CAP of " + str(ideal_GPA) +
                " for the remaining " +
                str(total_Required - total_Taken) +
                " MCs you have yet fulfil "
                "in order to graduate with a CAP of " + str(targetGPA) + ". All the best, you can do it! :) ")
            update.message.reply_text(
                "\n\nGoodbye! Type '/start' to calculate again")

            user_data.clear()
            return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s ended the conversation.", user.first_name)
    logger.info("Users to date: %s", len(users))
    update.message.reply_text("\n\nAll the best! Goodbye!\nType '/start' to calculate again",
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def help_doc(update, context):
    update.message.reply_text("This bot aims to help us to work towards the target CAP! To begin, type '/start'"
                              "\n\nIf the bot is unresponsive, please check your input or type '/stop' to stop and restart the bot.",
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def credits(update, context):
    update.message.reply_text("Yay! Hope this helped you throughout! We will be coming up with one more upcoming bot soon! ",
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    update.message.reply_text("Sorry, there is something wrong with your input. Please try again!",
                              reply_markup=ReplyKeyboardRemove())
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        constants.API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        # [0]\.[0]|[0-4]\.(\d?\d?)|[4].[3]|[0-4]$
        states={
            CURRENT_GPA: [MessageHandler(Filters.regex(r"^[0-9]\.[0-9][0-9]|[0-9]\.[0-9]|[0-9]$"), collect_cgpa)
                          ],

            TOTAL_MCS_REQUIRED: [MessageHandler(Filters.regex(r"^[1-9][0-9]\.[05]|[0-9]\.[05]|[1-9][0-9]|[0-9]$"),  collect_MCs_required)
                                 ],

            TOTAL_MCS_TAKEN: [MessageHandler(Filters.regex(r"^[0]\.[0]|[1][0-2]|[0-9]$"), collect_MCs_taken)
                              ],

            TARGET_GPA: [MessageHandler(Filters.regex(r"^[0-9]\.[0-9][0-9]|[0-9]\.[0-9]|[0-9]$"), collect_targetgpa)
                         ],


        },

        fallbacks=[CommandHandler('stop', cancel),
                   CommandHandler('help', help_doc),
                   (CommandHandler('credits', credits))]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen=constants.LISTEN_ADDRESS,
                          port=int(PORT),
                          url_path=constants.API_KEY)

    updater.bot.setWebhook(constants.HEROKU_SERVER_ADDRESS +
                           constants.API_KEY)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
