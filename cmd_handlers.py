from turtle import clear
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from menu import create_choose_menu, create_board, create_mode_menu, create_game_menu
from const import GameState
import tictactoe_model
import bot_ai_wrap


cur_sym = tictactoe_model.symbols[0]
next_sym = tictactoe_model.symbols[1]
bot_mode = 2
moves = tictactoe_model.init_board


def start(update: Update, context: CallbackContext):
    welcome_msg = '''<b>Tic-Tac-Toe Bot</b> - простой бот для игры в крестики-нолики с элементами искустенного интеллекта
            Команды:
            <i>/new_game</i> - Начало новой игры
            <i>/end_game</i> - Завершить игру
            '''
    update.message.reply_text(
        text=welcome_msg, parse_mode=ParseMode.HTML)


def new_game(update: Update, context: CallbackContext):
    
    user = update.effective_user.first_name
    msg = f"\tПривет, {user}! \nВыберите интеллект бота..."

    mode_menu = create_mode_menu(tictactoe_model.mode_dict)
    update.message.reply_text(text=msg, reply_markup=mode_menu)

    return GameState.BOT_MODE

def game_mode(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()

    mode_game = query.data

    if mode_game == 'new_game':
        update.effective_chat.send_message("А теперь на деньги! ;)")
        
        user = update.effective_user.first_name 
        msg = f"\tСпасибо, что играете в нашу игру, {user}! \nВыберите интеллект бота..."

        mode_menu = create_mode_menu(tictactoe_model.mode_dict)
        update.effective_chat.send_message(text=msg,reply_markup=mode_menu)

        return GameState.BOT_MODE
    else:        
        update.effective_chat.send_message("До новых встреч!")
        return ConversationHandler.END
    

def mode_bot(update: Update, context: CallbackContext):
    global bot_mode
    query = update.callback_query
    query.answer()
    bot_mode = int(query.data)

    msg = f"Вы выбрали уровень {tictactoe_model.mode_dict[bot_mode]}\nТеперь выберите правильную сторону..."

    sym_menu = create_choose_menu(tictactoe_model.symbols)
    query.edit_message_text(text=msg, reply_markup=sym_menu)

    return GameState.START_TURN


def turn(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_choice = int(query.data) - 1
    moves[user_choice] = cur_sym

    if tictactoe_model.check_winers(moves, cur_sym, user_choice):
        game_board = create_board(moves)
        query.edit_message_text(text="Вы выиграли!",
                                reply_markup=game_board)
        
        game_menu = create_game_menu(tictactoe_model.game_diсt)
        # query.edit_message_reply_markup(reply_markup=game_menu)
        update.effective_chat.send_message('Отличный результат! Попробуйте следующий уровень :)',reply_markup=game_menu)

        return GameState.GAME_MODE 

    bot_choice = bot_ai_wrap.get_bot_turn(moves, next_sym, bot_mode)
    moves[bot_choice] = next_sym

    if tictactoe_model.check_winers(moves, next_sym, bot_choice):
        game_board = create_board(moves)
        query.edit_message_text(
            text="Вы проиграли(((",  reply_markup=game_board)
        
        game_menu = create_game_menu(tictactoe_model.game_diсt)
        # query.edit_message_reply_markup(reply_markup=game_menu)
        update.effective_chat.send_message('Ничего страшного, не на корову же играем...',reply_markup=game_menu)
        return GameState.GAME_MODE 

    if not tictactoe_model.has_turns(moves):
        msg = "Ничья"
        game_board = create_board(moves)
        query.edit_message_text(
            text="Ничья, больше ходов нет.", reply_markup=game_board)
        
        game_menu = create_game_menu(tictactoe_model.game_diсt)
        # query.edit_message_reply_markup(reply_markup=game_menu)
        update.effective_chat.send_message('Игра достойных соперников!',reply_markup=game_menu)
        return GameState.GAME_MODE

    msg = f"Ваш ход: {query.data}\nХод бота: {bot_choice + 1}"
    game_board = create_board(moves)

    query.edit_message_text(text=msg, reply_markup=game_board)

    return GameState.USER_TURN


def end_game(update: Update, context: CallbackContext):
    global moves
    moves = tictactoe_model.init_board
    update.effective_chat.send_message("До новых встреч!")

    return ConversationHandler.END


def select(update: Update, context: CallbackContext):
    global cur_sym
    global next_sym
    global moves

    query = update.callback_query
    query.answer()

    cur_sym = query.data
    next_sym = tictactoe_model.symbols[1 - tictactoe_model.symbols.index(cur_sym)]

    moves = tictactoe_model.init_board()

    sym = tictactoe_model.get_first_turn(tictactoe_model.symbols)
    if sym == cur_sym:
        msg = f"Ваш выбор: {cur_sym}\n Начинаем, ваш ход..."
    else:
        bot_choice = bot_ai_wrap.get_bot_turn(moves, next_sym, bot_mode)
        moves[bot_choice] = next_sym
        msg = f"Ваш выбор: {cur_sym}\nПервым начинают - {next_sym}.\nИ ход соперника - {bot_choice + 1}"

    game_board = create_board(moves)
    query.edit_message_text(text=msg, reply_markup=game_board)

    return GameState.USER_TURN
