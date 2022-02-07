from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config import TOKEN
from key import key_gen_inline, key_gen_reply
from states import foodState
from database.accessor import PostgresAccessor
from database.models import DBfunc
import random
import os
bot = Bot(token=TOKEN)
os.system("redis-server")
storage = storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key')
dp = Dispatcher(bot, storage= storage)
dp.middleware.setup(LoggingMiddleware())
db = PostgresAccessor()
dbFunc = DBfunc()

@dp.message_handler(state = '*',commands=['start'])
async def process_start_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await dbFunc.add(message.from_user.id, str(" ".join(menu[0][0])), str(" ".join(menu[0][1])), str(" ".join(menu[1][0])),\
        str(" ".join(menu[1][1])), str(" ".join(menu[2][0])), str(" ".join(menu[2][1])), str(" ".join(menu[3][0])), str(" ".join(menu[3][1])) )
    await state.set_state(foodState.all()[2])
    await message.reply("Привет!\nЯ бот созданный для генерации случайного меню.", reply_markup = main_menu)

@dp.message_handler(lambda message: message.text == buttons['back'][0], state = '*')
async def process_back_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(foodState.all()[2])
    await message.reply('Вы в главном меню',reply_markup = main_menu)

@dp.message_handler(lambda message: message.text == buttons['menu'][2], state = foodState.MENU)
@dp.message_handler(commands=['help'], state = '*')
async def process_help_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(foodState.all()[1])
    await message.reply("Этот бот создан с той целью, чтобы помочь в выборе пищи на определенный прием пищи.\
    Вы можете изменить ингридиенты из которых будете готовить.", reply_markup= back_button)

@dp.message_handler(lambda message: message.text == buttons['menu'][1], state = foodState.MENU)
@dp.message_handler(commands=['settings'], state = '*')
async def process_settings_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(foodState.all()[3])
    await message.reply("Пожалуйста, выберите что вы хотите сделать", reply_markup= change_button)

@dp.message_handler(lambda message: message.text == buttons['menu'][0], state = foodState.MENU)
async def process_generate_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(foodState.all()[0])
    await message.reply('Выберите прием пищи',reply_markup = generate_button)

async def get_lists(id: int,text: str) -> list:
    temp = await dbFunc.get(id)
    if(text == buttons['generate'][0]):
        temp1 = temp.first1
        temp2 = temp.first2
    elif(text == buttons['generate'][1]):
        temp1 = temp.second1
        temp2 = temp.second2
    elif(text == buttons['generate'][2]):
        temp1 = temp.third1
        temp2 = temp.third2
    else:
        temp1 = temp.snack1
        temp2 = temp.snack2
    return temp1.split(' '), temp2.split(' ')

@dp.message_handler(lambda message: message.text in buttons['change'], state = foodState.SETTINGS)
async def process_settings_a_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    if(message.text == buttons['change'][0]):
        await state.set_state(foodState.all()[4])    
        await message.reply(f"Чтобы получались лингвистически верные названия, основные блюда должны быть в родительном падеже\nДля добавления блюда в меню, отправьте сообщение следующего формата:\nНазвание блюда:Тип блюда(гарнир(1) это или основное блюдо(2)):Прием пищи({','.join(buttons['generate'][:-1])})\nПримемер: Гречка:1:Завтрак", reply_markup= back_button)
    elif(message.text == buttons['change'][1]):
        await state.set_state(foodState.all()[5])    
        await message.reply(f"Блюда будут удалены только в том случае, если название полностью совпадает\nДля удаления блюда из меню, отправьте сообщение следующего формата:\nНазвание блюда:Прием пищи({','.join(buttons['generate'][:-1])})\nПример: Гречка:Завтрак", reply_markup= back_button)
    else:
        for priem in buttons['generate'][:-1]:
            a,b = await get_lists(message.from_user.id, priem)
            await message.reply(f"{priem}\nГарнир:{' '.join(a)}\nОсновное блюдо:{' '.join(b)}")
        await state.set_state(foodState.all()[3])
        await message.reply('Возврат к настройкам', reply=change_button)


@dp.message_handler(state = foodState.SETTINGS_ADD)
async def process_adding(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    isOk = True
    for i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if i in message.text:
            isOk = False
    text = message.text.split(':')
    if(text[1] != '1' and text[1] != '2'):
        isOk = False
    if(text[2] not in buttons['generate'][:-1]):
        isOk = False
    if(len(text) != 3):
        isOk = False
    if(isOk):
        a,b = await get_lists(message.from_user.id, text[2])
        if(text[1] == '1'):
            s = " ".join(a)
        else:
            s = " ".join(b)
        s += " " + text[0]
        if(text[2] == 'Завтрак'):
            q = 'first'
        elif(text[2] == 'Обед'):
            q = 'second'
        elif(text[2] == 'Ужин'):
            q = 'third'
        else:
            q = 'snack'
        await dbFunc.update(q+text[1], message.from_user.id, s)
        a,b = await get_lists(message.from_user.id, text[2])
        await message.reply(f"Обновленное меню:\n{text[2]}\nГарнир:{' '.join(a)}\nОсновное блюдо:{' '.join(b)}\n Если хотите добавить еще одно блюдо, отправьте его в том же формате, иначе нажмите кнопку назад", reply= back_button)
    else:
        await state.set_state(foodState.all()[3])
        await message.reply('Произошла какая-то ошибка.\nВозврат к настройкам', reply=change_button)

@dp.message_handler(state = foodState.SETTINGS_DEL)
async def process_delete_food(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    isOk = True
    for i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if i in message.text:
            isOk = False
    text = message.text.split(':')
    if(text[1] not in buttons['generate'][:-1]):
        isOk = False
    if(len(text) != 2):
        isOk = False
    if(isOk):
        if(text[1] == 'Завтрак'):
            q = 'first'
        elif(text[1] == 'Обед'):
            q = 'second'
        elif(text[1] == 'Ужин'):
            q = 'third'
        else:
            q = 'snack'
        a, b = await get_lists(message.from_user.id, text[1])
        if(text[0] in a):
            i = '1'
            a.remove(text[0])
            s = " ".join(a)
        else:
            i = '2'
            b.remove(text[0])
            s = " ".join(b)
        await dbFunc.update(q+i, message.from_user.id, s)
        a,b = await get_lists(message.from_user.id, text[1])
        await message.reply(f"Обновленное меню:\n{text[1]}\nГарнир:{' '.join(a)}\nОсновное блюдо:{' '.join(b)}\n Если хотите удалить еще одно блюдо, отправьте его в том же формате, иначе нажмите кнопку назад", reply= back_button)
    else:
        await state.set_state(foodState.all()[3])
        await message.reply('Произошла какая-то ошибка.\nВозврат к настройкам', reply=change_button)

@dp.message_handler(lambda message: message.text in buttons['generate'], state = foodState.GENERATE)
async def process_generate_command(message: types.Message):
    local_kb = key_gen_inline(*buttons['inline'])
    first_b,second_b = await get_lists(message.from_user.id, message.text)
    first_b = random.choice(first_b)
    second_b = random.choice(second_b)
    if(second_b != ""):
        first_b += " с"
    else:
        second_b = ''
    text = "{} {}".format(first_b, second_b)
    letmegoogleforyou = "google.com/search?q=Рецепт+{}".format('+'.join(text.split(' ')))
    local_kb.add(types.InlineKeyboardButton("Рецепт", url = letmegoogleforyou))
    await message.reply(f"{message.text}\nВаш выбор: " + text,reply_markup = local_kb)

@dp.message_handler(state = '*')
async def echo_message(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(foodState.all()[2])
    await message.reply("Я не понимаю, что ты говоришь. Теперь ты в главном меню.", reply_markup = main_menu)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'), state = '*')
async def process_callback(callback_query: types.CallbackQuery):
    code = callback_query.data
    if(code == 'btn_re'):
        while(1):
            local_kb = key_gen_inline(*buttons['inline'])
            first_b,second_b = await get_lists(callback_query.from_user.id, callback_query.message.text.split('\n')[0])
            first_b = random.choice(first_b)
            second_b = random.choice(second_b)
            if(second_b != ""):
                first_b += " с"
            else:
                second_b = ''
            text = "{} {}".format(first_b, second_b)
            letmegoogleforyou = "google.com/search?q=Рецепт+{}".format('+'.join(text.split(' ')))
            local_kb.add(types.InlineKeyboardButton("Рецепт", url = letmegoogleforyou))
            if("{}\nВаш выбор: ".format(callback_query.message.text.split('\n')[0]) + text != callback_query.message.text):
                break
        await callback_query.message.edit_text("{}\nВаш выбор: ".format(callback_query.message.text.split('\n')[0]) + text,reply_markup = local_kb)
    if(code == 'btn_ok'):
        await callback_query.message.edit_text(callback_query.message.text, reply_markup= types.InlineKeyboardMarkup().add(callback_query.message.reply_markup.inline_keyboard[1][0]))

async def _on_startup(dp: Dispatcher):
    await db._on_connect()

async def _on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await db._on_disconnect()

if __name__ == '__main__':
    buttons = {}
    buttons['menu'] = ["Сгенерировать", "Настройки", "Помощь"]
    buttons['back'] = ['Назад']
    buttons['generate'] = ["Завтрак", "Обед", "Ужин", "Перекус", "Назад"]
    buttons['inline'] = [['Ок', 'Реролл'], ['btn_ok', 'btn_re']]
    buttons['change'] = ['Добавить', 'Убрать', 'Показать меню', 'Назад']
    menu = [ [ ["Овсянка", "Гречка", "Рис"], ["Маслом", "Молоком", "Орехами", "Сухофруктами"] ],\
    [ ["Суп", "Гречка", "Рис", "Овсянка"], ["Курицой", "Рыбой", "Овощами"] ], [ ["Суп", "Гречка", "Рис", "Овсянка"],\
        ["Курицой", "Рыбой", "Овощами"] ], [ ["Морковка", "Сухофрукты", "Вода", "Ничего"], [] ] ]
    main_menu = key_gen_reply(buttons['menu'])
    back_button = key_gen_reply(buttons['back'])
    generate_button = key_gen_reply(buttons['generate'], isOne= False)
    change_button = key_gen_reply(buttons['change'])
    executor.start_polling(dp, on_startup=_on_startup, on_shutdown= _on_shutdown)