import discord
from discord.ext import commands
import io
import pandas as pd
import mplfinance as mpf
import yfinance as yf
import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# Discordのbotトークン
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔹 Intentの設定（Message Content を明示的に有効化）
intents = discord.Intents.default()
intents.message_content = True  # これを追加！

# ✅ `intents` を設定してBotを作成
bot = commands.Bot(command_prefix="!", intents=intents)

# チャート作成関数
def create_candlestick_chart(ticker):
    try:
        # 株価データの取得（1年分、日足）
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=False)
        df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]]

        # カスタムカラー設定
        mc = mpf.make_marketcolors(up='red', down='blue', wick='black', volume='gray')
        s = mpf.make_mpf_style(marketcolors=mc)
        
        # 画像をメモリ上に保存（io.BytesIOを使用）
        buf = io.BytesIO()
        mpf.plot(df, type="candle", style=s, volume=True, mav=(25, 75), figratio=(10, 6),
                 panel_ratios=(3, 1), title=f"{ticker} 1-Year Candlestick Chart", savefig=buf  # ここで直接メモリに保存
        )
        buf.seek(0)  # バッファの先頭に移動
        return buf

    except Exception as e:
        print(f"エラー: {e}")
        return None

# プレフィックスコマンド "!ticker" を定義
@bot.command()
async def ticker(ctx, symbol: str):
    """ ユーザーが !ticker 7203.T のように入力すると、チャート画像を送信 """
    await ctx.send(f"📈 {symbol} の株価チャートを取得しています...")
    
    buf = create_candlestick_chart(symbol)
    
    if buf:
        await ctx.send(file=discord.File(buf, filename=f"{symbol}_chart.png"))
    else:
        await ctx.send("⚠️ チャートの生成に失敗しました。ティッカーを確認してください。")

# Botを起動
bot.run(TOKEN)
