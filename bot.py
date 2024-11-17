import os
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv

# 봇 초기 설정
intents = discord.Intents.all()
intents.messages = True  # 메시지 관련 권한 활성화
bot = commands.Bot(command_prefix="!", intents=intents)

# 환경 설정
load_dotenv()
TOKEN=os.getenv("TOKEN")
CHANNEL_ID=int(os.getenv("CHANNEL_ID"))
ROLE_ID=int(os.getenv("ROLE_ID"))
THREAD_CREATION_INTERVAL = 3600*24  # 1시간(3600초) 간격
TARGET_TIME = time(14,17)

# 봇 준비 이벤트
@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")
    bot.loop.create_task(wait_until_target_time())  # 특정 시간에 실행하는 태스크 시작

# 특정 시간까지 대기하고 스레드 생성
async def wait_until_target_time():
    while True:
        now = datetime.now()
        target_datetime = datetime.combine(now.date(), TARGET_TIME)

        # 현재 시간이 실행 시간 이후면 다음 날로 설정
        if now > target_datetime:
            target_datetime = datetime.combine(now.date().replace(day=now.day + 1), TARGET_TIME)

        # 남은 시간 계산
        wait_seconds = (target_datetime - now).total_seconds()
        print(f"다음 실행까지 {wait_seconds:.2f}초 대기합니다.")

        # 대기 후 스레드 생성
        await asyncio.sleep(wait_seconds)
        await create_thread_with_mention()

# 스레드 생성 함수
async def create_thread_with_mention():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("채널을 찾을 수 없습니다.")
        return

    current_time = datetime.now().strftime("%Y년 %m월 %d일")
    thread_name = f"{current_time} 스크럼"

    try:
        thread = await channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.public_thread,
            auto_archive_duration=1440
        )
        mention_message = f"<@&{ROLE_ID}> 스크럼 작성합시다."
        template_message = """```
* **:white_check_mark: Done**


* **:mag:In progress**


* **:eyes: Todo**
```"""
        await thread.send(mention_message)
        await thread.send(template_message)
        print(f"스레드 생성 완료: {thread_name}")
    except Exception as e:
        print(f"스레드 생성 중 오류 발생: {e}")

# 봇 실행
bot.run(TOKEN)