import asyncio
import logging
from datetime import datetime
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import sqlite3

# pars_all, pars_end,pars_notend,percent integer
bd = sqlite3.connect('parsdasha.db')
cu = bd.cursor()

token = '5631292267:AAHNm0mJ6mFoc5LgDDPuItjNb3oebml3CRQ'

storage = MemoryStorage()

bot = Bot(token)

dp = Dispatcher(bot, storage=storage)

now = datetime.now()
current_time = now.strftime("%H:%M")
class Day(StatesGroup):
    new_day = State()
    pars = State()
    all_not = State()
    end = State()


async def CheckTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    msg = current_time
    await bot.send_message(539057262, msg)
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        await asyncio.sleep(2)
        if current_time == "08:00":
            await Notifications()
            break
        else:
            pass



async def Notifications():
    await bot.send_message(539057262, 'Отметься во мне пожалуйста!')

@dp.message_handler(state='*', commands='db')
@dp.message_handler(Text(equals='db', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    kp = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/start')
    kp.add(btn1)
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('db.', reply_markup=kp)


@dp.message_handler(commands=['start'], State=None)
async def start(message: types.Message):
    kp = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Пошла в шарагу ✅')
    btn2 = types.KeyboardButton('Не пошла в шарагу ❌')
    btn3 = types.KeyboardButton('Статистика 📝')
    kp.add(btn1, btn2)
    kp.add(btn3)
    await Day.new_day.set()
    await message.answer('Доброе утро!', reply_markup=kp)

@dp.message_handler(state=Day.new_day)
async def day(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_day'] = message.text
    if message.text == 'Пошла в шарагу ✅':
        await message.answer('Умничка!! Хорошего дня тебе ❤️ \nСколько у тебя пар сегодня?')
        await Day.pars.set()
    elif message.text == 'Не пошла в шарагу ❌':
        kp = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('/start')
        kp.add(btn1)
        await message.reply('Отдыхай, солнышко!', reply_markup=kp)
        await state.finish()
        await CheckTime()
    elif message.text == 'Статистика 📝':
        cu.execute("SELECT SUM(pars_all), SUM(pars_end), SUM(pars_notend) FROM dasha")
        res = cu.fetchall()
        all_pars = res[0][0]
        end_pars = res[0][1]
        not_endpars = res[0][2]
        try:
            percent = int(end_pars) / int(all_pars)
            pos = percent * 100
        except:
            pos = 'Ты пока не ходила ни на одну пару'
        msg = (
                '🧡Твоя статистика на данный момент🧡' + '\n' +
                '📝 Всего пар: ' + str(all_pars) + '\n' +
                '✅ Ты сходила на: ' + str(end_pars) + '\n' +
                '❌ Ты пропустила пар: ' + str(not_endpars) + '\n' +
                '⚠ Процент посещений: ' + str(pos) + '%'
        )
        await bot.send_message(message.from_user.id, msg)


@dp.message_handler(state=Day.pars)
async def Updater(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['pars'] = message.text

    kp = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Я все отсидела! :)')
    btn2 = types.KeyboardButton('Я не все отсидела! :(')
    kp.add(btn1)
    kp.add(btn2)
    await message.answer('Ого как много! \n Служба поддержки заскучавших Даш: @MironManager', reply_markup=kp)
    await Day.all_not.set()


@dp.message_handler(state=Day.all_not)
async def Ender(message: types.Message, state: FSMContext):
    if message.text == 'Я не все отсидела! :(':
        await Day.end.set()
        await message.reply('Сколько пар ты пропустила?')
    else:
        kp = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('/start')
        kp.add(btn)
        async with state.proxy() as data:
            pars = data['pars']
        await message.reply('Умничка, красавица!', reply_markup=kp)
        msg = 'Ты сходила на: ' + pars + ' пар'
        cu.execute("INSERT INTO dasha VALUES(?,?,?)", (int(pars), int(pars), 0,))
        bd.commit()
        await bot.send_message(message.from_user.id, msg)
        await state.finish()
        await CheckTime()


@dp.message_handler(state=Day.end)
async def Math(message: types.Message, state: FSMContext):
    kp = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/start')
    kp.add(btn1)
    async with state.proxy() as data:
        data['end'] = message.text
        pars = data['pars']
    await message.reply('Окей, сча посчитаем')
    par = (int(pars) - int(data['end']))
    await bot.send_message(message.from_user.id, 'Сегодня было ' + str(pars) + ' ,но ты сходила на ' + str(par),
                           reply_markup=kp)
    cu.execute("INSERT INTO dasha VALUES(?,?,?)", (int(pars), int(par), int(data['end'])))
    bd.commit()
    await state.finish()
    await CheckTime()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
