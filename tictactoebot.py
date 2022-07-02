from telegram.ext import (Dispatcher, Updater, CommandHandler,
                          ConversationHandler, CallbackQueryHandler, MessageHandler)
import cmd_handlers
from const import GameState

digits = "|".join([str(i) for i in range(1, 10)])
digit_pattern = f"^{digits}$"

game_state_hdl = ConversationHandler(
    entry_points=[CommandHandler('new_game', cmd_handlers.new_game)],
    states={
        GameState.BOT_MODE: [CallbackQueryHandler(
            cmd_handlers.mode_bot)],
        GameState.START_TURN: [CallbackQueryHandler(
            cmd_handlers.select)],
        GameState.USER_TURN: [CallbackQueryHandler(
            cmd_handlers.turn, pattern=digit_pattern)],
        GameState.GAME_MODE: [CallbackQueryHandler(
            cmd_handlers.game_mode)],    
    },
    fallbacks=[CommandHandler('end_game', cmd_handlers.end_game)]
)


def get_tocken() -> str:
    with open("env.txt") as ifile:
        data = ifile.read()
    return data.strip()


def init_handlers(dispather: Dispatcher):
    dispather.add_handler(CommandHandler(['start', 'help'], cmd_handlers.start))
    dispather.add_handler(game_state_hdl)


def run():
    bot_token = get_tocken()

    updater = Updater(
        token=bot_token, use_context=True)
    print("Tic-Tac-Toe bot started work...")

    dp = updater.dispatcher
    init_handlers(dp)

    updater.start_polling(poll_interval=1, drop_pending_updates=True)
    updater.idle()
