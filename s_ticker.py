import discord
from discord import app_commands
import io
import yfinance as yf
import mplfinance as mpf
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intent設定
intents = discord.Intents.default()
intents.message_content = True

# Botの設定
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# チャート作成関数
def create_candlestick_chart(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d")
        df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]]

        mc = mpf.make_marketcolors(up='red', down='blue', wick='black', volume='gray')
        s = mpf.make_mpf_style(marketcolors=mc)

        buf = io.BytesIO()
        mpf.plot(df, type="candle", style=s, volume=True, mav=(25, 75), figratio=(10, 6),
                 panel_ratios=(3, 1), title=f"{ticker} 1-Year Candlestick Chart", savefig=buf)
        buf.seek(0)
        return buf

    except Exception as e:
        print(f"エラー: {e}")
        return None

# スラッシュコマンドの登録
@tree.command(name="ticker", description="指定した銘柄の株価チャートを取得")
async def ticker(interaction: discord.Interaction, symbol: str):
    await interaction.response.defer()  # 処理中の表示
    buf = create_candlestick_chart(symbol)

    if buf:
        await interaction.followup.send(file=discord.File(buf, filename=f"{symbol}_chart.png"))
    else:
        await interaction.followup.send("⚠️ チャートの生成に失敗しました。ティッカーを確認してください。")

# Botが起動したときにスラッシュコマンドを同期
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

# Botを起動
bot.run(TOKEN)
