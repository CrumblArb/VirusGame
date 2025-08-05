import aiohttp
import asyncio
import json
import os
import sys
from fake_useragent import UserAgent
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate, PeerIdInvalid
from config import *



try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.formatted_text import HTML
except ImportError:
    print("Библиотека prompt-toolkit не установлена. Пожалуйста, установите ее:")
    print("pip install prompt-toolkit")
    exit()



logger.remove()
logger.add(sys.stderr, level=LOGGING_LEVEL)


try:
    os.mkdir(SESSIONS_DIR)
except:
    pass

class Acc:
    def __init__(self,acc_name:str, url:str=None, token=None, proxy=None, user_agent: str = None,api_hash:str = None, api_id:int = None):
        self.token = token
        self.proxy = proxy
        self.acc_name = acc_name
        self.url = url
        self.useragent = user_agent
        self.proxy = proxy


        self.app = Client(acc_name,api_id,api_hash)



        if user_agent is None:
            self.useragent = UserAgent().random

        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'apollo-require-preflight': '*',
            'authorization': f'Bearer {self.token}',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://virusgift.pro',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://virusgift.pro/',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.useragent,
            'x-batch': 'true',
        }

    async def init(self):
        try:
            async with self.app:
                me = await self.app.get_me()
                logger.success(f"[{self.acc_name}] Успешный вход в Telegram: {me.first_name}")
        except Exception as e:
            logger.error(f"[{self.acc_name}] Ошибка при авторизации: {e}")
            raise e

    async def getSpin(self):
        json_data = [
            {
                'operationName': 'me',
                'variables': {},
                'query': 'query me {\n  me {\n    id\n    refCode\n    userId\n    firstName\n    lastName\n    userName\n    photo\n    balance\n    starsBalance\n    status\n    miningSpeed\n    deathDate\n    languageCode\n    isFirstInfection\n    hidden\n    onboardingCompleted\n    invitedCount\n    refsRecoveryPercent\n    testSpin\n    nextFreeSpin\n    refBalance\n    refHoldBalance\n    refBalanceUsd\n    refHoldBalanceUsd\n    __typename\n  }\n}',
            },
        ]
        logger.info(f"[{self.acc_name}] Получаю информацию о доступных спинах")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    'https://virusgift.pro/api/graphql/query',
                    headers=self.headers,
                    json=json_data,
                    proxy=self.proxy
                ) as response:
                    if response.status != 200:
                        logger.error(f"[{self.acc_name}] Ошибка получения спинов: {response.status} {await response.text()}")
                        return None
                    data = await response.json()
                    logger.debug(data)
                    return data[0]["data"]["me"]["testSpin"]
            except Exception as ex:
                logger.error(f"[{self.acc_name}] Исключение при получении спинов: {ex}")
                return None


    async def spin(self):



        test_json_data = [
            {
                'operationName': 'markTestSpinTonnelClick',
                'variables': {},
                'query': 'mutation markTestSpinTonnelClick {\n  markTestSpinTonnelClick {\n    success\n    __typename\n  }\n}',
            },
        ]
        json_data = {
            'operationName': 'startRouletteSpin',
            'variables': {'input': {'type': 'X1'}},
            'query': 'mutation startRouletteSpin($input: StartRouletteSpinInput!) {\n  startRouletteSpin(input: $input) {\n    success\n    prize {\n      id\n      name\n      caption\n      animationUrl\n      photoUrl\n      exchangeCurrency\n      exchangePrice\n      prizeExchangePrice\n      isSpinSellable\n      isClaimable\n      isExchangeable\n      storyLinkAfterWin\n      __typename\n    }\n    userPrizeId\n    balance\n    isStoryRewardAvailable\n    storyReward\n    __typename\n  }\n}',
        }
        logger.info(f"[{self.acc_name}] Кручу рулетку")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post('https://virusgift.pro/api/graphql/query', headers=self.headers, json=test_json_data, proxy=self.proxy) as response:
                    logger.debug(f"[{self.acc_name}] Ответ на pre-spin: {await response.text()}")
                test_json_data = [
                    {
                        'operationName': 'markTestSpinPortalClick',
                        'variables': {},
                        'query': 'mutation markTestSpinPortalClick {\n  markTestSpinPortalClick {\n    success\n    __typename\n  }\n}',
                    },
                ]
                async with session.post('https://virusgift.pro/api/graphql/query', headers=self.headers, json=test_json_data, proxy=self.proxy) as response:
                    logger.debug(f"[{self.acc_name}] Ответ на pre-spin: {await response.text()}")
                async with session.post('https://virusgift.pro/api/graphql/query', headers=self.headers, json=json_data, proxy=self.proxy) as response:
                    if response.status != 200:
                        logger.error(f"[{self.acc_name}] Ошибка спина: {response.status} {await response.text()}")
                        return None
                    data = await response.json()

                    logger.debug(data)

                    if data[0]["errors"]:
                        if data[0]["errors"][0]["extensions"]["code"] == "TELEGRAM_SUBSCRIPTION_REQUIRED":
                            await self.subscribe_to_channel(data[0]["errors"][0]["extensions"]["username"])
                            await self.spin()

                    else:
                        logger.success(f"[{self.acc_name}] Спин выполнен успешно.")

                    return data
            except Exception as ex:
                logger.error(f"[{self.acc_name}] Исключение во время спина: {ex}")
                return None

    async def subscribe_to_channel(self,channel_username:str):
        # Initialize the Pyrogram client


        try:
            # Start the client and handle authorization
            logger.info("Starting Pyrogram client and attempting to log in...")
            with self.app:
                # Check if the user is already authorized
                await self.app.start()
                if not await self.app.get_me():
                    logger.error("Failed to authorize. Please check your API credentials or phone number.")
                    return

                logger.info("Successfully logged in. Attempting to join channel...")

                # Attempt to join the channel
                try:
                    await self.app.join_chat(channel_username)
                    logger.success(f"Successfully subscribed to {channel_username}")
                except ChannelInvalid:
                    logger.error(f"Invalid channel username: {channel_username}. Please check the username.")
                except ChannelPrivate:
                    logger.error(f"Cannot join {channel_username}. The channel is private or you are banned.")
                except PeerIdInvalid:
                    logger.error(f"Invalid peer ID for {channel_username}. Ensure the channel exists and is public.")
                except FloodWait as e:
                    logger.warning(f"Flood wait: Please wait {e.value} seconds before retrying.")
                except Exception as e:
                    logger.error(f"An error occurred while trying to join {channel_username}: {e}")

        except Exception as e:
            logger.error(f"Failed to start client or authorize: {e}")


def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=4, ensure_ascii=False)
    logger.info(f"Данные сохранены в {ACCOUNTS_FILE}")

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    try:
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Ошибка загрузки {ACCOUNTS_FILE}: {e}. Будет создан новый файл.")
        return []

async def process_account(account_details):
    try:
        acc = Acc(
            acc_name=account_details['acc_name'],
            token=account_details.get('token'),
            proxy=account_details.get('proxy'),
            api_hash=account_details.get("api_hash"),
            api_id=account_details.get("api_id")
        )
        if not acc.token:
            logger.warning(f"Пропускаем аккаунт '{acc.acc_name}' из-за отсутствия токена.")
            return


        spins = await acc.getSpin()
        if spins is not None and spins > 0:
            logger.info(f"Аккаунт '{acc.acc_name}' имеет {spins} спинов. Запускаю...")
            for i in range(spins):
                await acc.spin()
                if i < spins - 1:
                    await asyncio.sleep(2)
        else:
            logger.info(f"У аккаунта '{acc.acc_name}' нет доступных спинов.")

    except Exception as e:
        logger.error(f"Критическая ошибка при обработке аккаунта '{account_details['acc_name']}': {e}")


async def main():
    accounts = load_accounts()
    if accounts:
        logger.info(f"Загружено {len(accounts)} аккаунтов из {ACCOUNTS_FILE}")

    session = PromptSession()

    while True:
        print("\n" + "="*30)
        print("1. Добавить аккаунт")
        print("2. Запустить все аккаунты")
        print("3. Показать добавленные аккаунты")
        print("4. Выход")
        print("="*30)

        choice = await session.prompt_async("Выберите действие: ")

        if choice == '1':
            acc_name = await session.prompt_async("Введите имя для аккаунта: ")
            proxy_input = await session.prompt_async(HTML("<ansiblue>Введите прокси</ansiblue> (формат: http://user:pass@host:port) или оставьте пустым: "))
            proxy = proxy_input if proxy_input else None

            instruction_text = """
✅ --- Инструкция по получению токена ---
1. Откройте Telegram Web в браузере (Chrome, Edge).
2. Нажмите F12, чтобы открыть Инструменты разработчика.
3. Перейдите на вкладку 'Application' (Приложение).
4. В меню слева ('Storage') раскройте 'Session Storage'.
5. Нажмите на строку с адресом сайта (https://virusgift.pro).
6. Справа в таблице найдите ключ 'token' и скопируйте его значение.
-----------------------------------------
"""
            print(instruction_text)
            


            token = await session.prompt_async(HTML("<ansiblue>Теперь вставьте скопированный токен сюда:</ansiblue> "))

            if not token:
                logger.error("Токен не был введен. Аккаунт не добавлен.")
                continue

            instruction_text = """
✅ --- Инструкция по получению API_HASH и API_ID ---
1. Откройте https://my.telegram.org и войдите.
2. Нажмите API development tools.
3. Создайте любое приложение.
-----------------------------------------
"""

            print(instruction_text)

            api_hash = await session.prompt_async(HTML("<ansiblue>API_HASH:</ansiblue> "))

            if not api_hash:
                logger.error("api_hash не был введен. Аккаунт не добавлен.")
                continue

            api_id = await session.prompt_async(HTML("<ansiblue>API_ID:</ansiblue> "))

            if not api_id:
                logger.error("api_ID не был введен. Аккаунт не добавлен.")
                continue

            #Client("sessions/"+acc_name, api_id=api_id, api_hash=api_hash) #eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ0NzI3NTMsImlkIjoiMTIxNzIyNjQifQ.TaXL71SyovNUq1PfpuegV5IpoHu-7JuZfxYuCVJ8ITM

            acc_path = SESSIONS_DIR+"/" + acc_name
            acc_obj = Acc(
                acc_name=acc_path,
                token=token,
                proxy=proxy,
                api_id=int(api_id),
                api_hash=api_hash
            )

            # Авторизация в Telegram
            try:
                await acc_obj.init()
            except Exception:
                logger.error(f"Аккаунт '{acc_name}' не был добавлен из-за ошибки авторизации.")
                continue

            accounts.append({
                'acc_name': acc_path,
                'proxy': proxy,
                'token': token,
                'url': None,
                "api_hash": api_hash,
                "api_id": int(api_id)
            })
            save_accounts(accounts)
            logger.success(f"Аккаунт '{acc_name}' успешно добавлен, авторизован и сохранен!")


        elif choice == '2':
            if not accounts:
                logger.warning("Нет аккаунтов для запуска. Сначала добавьте аккаунт.")
                continue
            
            logger.info(f"Запуск обработки для {len(accounts)} аккаунтов...")
            tasks = [process_account(acc) for acc in accounts]
            await asyncio.gather(*tasks)
            logger.info("Все аккаунты обработаны.")

        elif choice == '3':
            if not accounts:
                logger.info("Список аккаунтов пуст.")
            else:
                logger.info(f"Добавленные аккаунты ({len(accounts)}):")
                for i, acc in enumerate(accounts, 1):
                    proxy_status = f"Прокси: {acc.get('proxy')}" if acc.get('proxy') else "Без прокси"
                    token_status = "Токен предоставлен"
                    print(f"  {i}. {acc['acc_name']} ({proxy_status}, {token_status})")

        elif choice == '4':
            logger.info("Выход из программы.")
            break
        
        else:
            logger.warning("Неверный выбор. Пожалуйста, введите число от 1 до 4.")

if __name__ == '__main__':
    asyncio.run(main())
