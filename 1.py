import discord
from discord.ext import commands
from urllib.parse import urlparse, parse_qs
import requests

# Thay thế 'YOUR_BOT_TOKEN' bằng token của bot mà bạn đã sao chép từ Discord Developer Portal
TOKEN = 'MTIwMDU4MjgzMDQzMDg4Nzk5OA.GtxIq3.oXO5VUAsE0hPQr87Qrb-FDFFVmxIftCQL78RBI'

# Cấu hình bot
intents = discord.Intents.default()
intents.message_content = True  # Đảm bảo bot có quyền đọc nội dung tin nhắn
bot = commands.Bot(command_prefix='/', intents=intents)

# Hàm gửi yêu cầu đến API Fluxus và sao chép giá trị key
async def handle_fluxus(channel, hwid):
    url = f'https://stickx.top/api-fluxus/?hwid={hwid}&api_key=E99l9NOctud3vmu6bPne'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            if 'key' in json_data:
                key = json_data['key']
                await channel.send(f'**Fluxus API Key:** {key}')
            else:
                await channel.send(f'**Fluxus API Response:** {response.text}')
        else:
            await channel.send(f'**Fluxus API Status Code:** {response.status_code}')
    except Exception as e:
        await channel.send(f'Đã xảy ra lỗi: {e}')

# Hàm gửi yêu cầu đến API Delta và sao chép giá trị key
async def handle_delta(channel, id_param):
    url = f'https://stickx.top/api-delta/?hwid={id_param}&api_key=E99l9NOctud3vmu6bPne'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            if 'key' in json_data:
                key = json_data['key']
                await channel.send(f'**Delta API Key:** {key}')
            else:
                await channel.send(f'**Delta API Response:** {response.text}')
        else:
            await channel.send(f'**Delta API Status Code:** {response.status_code}')
    except Exception as e:
        await channel.send(f'Đã xảy ra lỗi: {e}')

# Hàm gửi yêu cầu đến API Linkvertise và sao chép giá trị key
async def handle_linkvertise(channel, link):
    url = f'https://stickx.top/api-linkvertise/?link={link}&api_key=E99l9NOctud3vmu6bPne'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            if 'key' in json_data:
                key = json_data['key']
                await channel.send(f'**Linkvertise API Key:** {key}')
            else:
                await channel.send(f'**Linkvertise API Response:** {response.text}')
        else:
            await channel.send(f'**Linkvertise API Status Code:** {response.status_code}')
    except Exception as e:
        await channel.send(f'Đã xảy ra lỗi: {e}')

# Xử lý sự kiện tin nhắn
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Bot không phản hồi tin nhắn của chính nó

    if 'http' in message.content:
        link = message.content
        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        if 'flux.li' in link:
            # Trích xuất HWID từ liên kết
            hwid = query_params.get('HWID', [None])[0]
            if hwid:
                await handle_fluxus(message.channel, hwid)
            else:
                await message.channel.send('Không tìm thấy HWID trong liên kết Fluxus.')
        elif 'linkvertise.com' in link:
            # Gọi lệnh linkvertise với liên kết đã gửi
            await handle_linkvertise(message.channel, link)
        elif 'gateway.platoboost.com' in link:
            # Trích xuất ID từ liên kết Delta
            id_param = query_params.get('id', [None])[0]
            if id_param:
                await handle_delta(message.channel, id_param)
            else:
                await message.channel.send('Không tìm thấy ID trong liên kết Delta.')
        else:
            await message.channel.send('Liên kết không chứa "flux.li", "linkvertise.com", hoặc "gateway.platoboost.com".')

# Chạy bot
bot.run(TOKEN)
