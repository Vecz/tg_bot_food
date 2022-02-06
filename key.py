from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

def key_gen_reply(keys: list, isResize: bool = True, isOne: bool = True):
    gen = ReplyKeyboardMarkup(resize_keyboard= isResize, one_time_keyboard=isOne)
    for i in keys:
        gen.add(KeyboardButton(i))
    return gen
    
def key_gen_inline(keys: list, call:list, new_row:int = 2):
    ans = InlineKeyboardMarkup(row = new_row)
    for i in range(min(len(keys), len(call))):
        ans.insert(InlineKeyboardButton(keys[i], callback_data=call[i]))
    return ans
