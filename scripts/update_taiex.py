import json
import requests
import warnings
import os
import re
from datetime import datetime, timezone, timedelta

warnings.filterwarnings('ignore')
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0'}
TW_TZ = timezone(timedelta(hours=8))
LIVE_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_live.js')
D0050_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_0050.js')
DATA_VT_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_vt.js')
DATA_SPY_PATH      = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_spy.js')
ANALYSIS_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis_data.js')


# ── TAIEX ────────────────────────────────────────────────────────────────────

def _fetch_taiex_yfinance():
    """用 yfinance 抓 ^TWII，約 15 分鐘延遲，可從非台灣 IP 存取。"""
    try:
        import yfinance as yf
        ticker = yf.Ticker('^TWII')
        # 優先抓今日 5 分鐘盤中資料
        hist = ticker.history(period='1d', interval='5m')
        if not hist.empty:
            date  = hist.index[-1].strftime('%Y-%m-%d')
            close = round(float(hist['Close'].iloc[-1]), 2)
            high  = round(float(hist['High'].max()), 2)
            low   = round(float(hist['Low'].min()), 2)
            print(f'TAIEX yfinance 盤中 {date} 現值={close} 今日高={high}')
            return date, close, high, low
        # 日線 fallback（取最近一個完整交易日）
        hist = ticker.history(period='5d')
        if not hist.empty:
            last  = hist.iloc[-1]
            date  = hist.index[-1].strftime('%Y-%m-%d')
            close = round(float(last['Close']), 2)
            high  = round(float(last['High']), 2)
            low   = round(float(last['Low']), 2)
            print(f'TAIEX yfinance 日線 {date} 收盤={close}')
            return date, close, high, low
    except Exception as e:
        print(f'TAIEX yfinance error: {e}')
    return None, None, None, None


def fetch_taiex_today():
    now = datetime.now(TW_TZ)
    # 優先用 yfinance（從 GitHub Actions 非台灣 IP 可正常存取）
    result = _fetch_taiex_yfinance()
    if result[0] is not None:
        return result
    # fallback: TWSE MI_5MINS_HIST（盤後才有完整資料）
    date_str = now.strftime('%Y%m%d')
    url = f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={date_str}&response=json'
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        d = r.json()
        if d.get('stat') == 'OK' and d.get('data'):
            last = d['data'][-1]
            parts = last[0].split('/')
            year = int(parts[0]) + 1911
            date = f'{year}-{parts[1]}-{parts[2]}'
            close = float(last[4].replace(',', ''))
            high  = float(last[2].replace(',', ''))
            low   = float(last[3].replace(',', ''))
            return date, close, high, low
    except Exception as e:
        print(f'TAIEX fetch error: {e}')
    return None, None, None, None


# ── VT ───────────────────────────────────────────────────────────────────────

def fetch_vt():
    """用 yfinance 抓 VT 最新收盤、YTD 高低，並從歷史找 ATH."""
    try:
        import yfinance as yf
        ticker = yf.Ticker('VT')

        # 歷史最高點（含今年資料）
        full = ticker.history(period='max')
        if full.empty:
            return None, None, None, None, None, None, None

        ath_date = full['High'].idxmax().strftime('%Y-%m-%d')
        ath_val  = round(float(full['High'].max()), 2)

        # 最近 5 天，取最後一筆有效資料
        hist = full.tail(5)
        last  = hist.iloc[-1]
        date  = hist.index[-1].strftime('%Y-%m-%d')
        close = round(float(last['Close']), 2)
        high  = round(float(last['High']),  2)

        # 當年度 YTD 高低（精確計算）
        this_year = datetime.now(TW_TZ).year
        ytd = full[full.index.year == this_year]
        ytd_high = round(float(ytd['High'].max()), 2) if not ytd.empty else None
        ytd_low  = round(float(ytd['Low'].min()),  2) if not ytd.empty else None

        return date, close, high, ath_val, ath_date, ytd_high, ytd_low
    except Exception as e:
        print(f'VT fetch error: {e}')
    return None, None, None, None, None, None, None


# ── 讀 / 寫 OHLC JS 檔（通用）───────────────────────────────────────────────

def read_ohlc_year(path, year):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(rf'\{{ y: {year}, o: ([\d.]+), c: ([\d.]+), h: ([\d.]+), l: ([\d.]+) \}}', content)
    if not m:
        return None
    return {'o': float(m.group(1)), 'c': float(m.group(2)),
            'h': float(m.group(3)), 'l': float(m.group(4))}


def write_ohlc_year(path, year, o, c, h, l):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    old = re.search(rf'\{{ y: {year}, o: [\d.]+, c: [\d.]+, h: [\d.]+, l: [\d.]+ \}}', content)
    if not old:
        print(f'{os.path.basename(path)} 中找不到 {year} 年的資料列')
        return
    new_line = f'{{ y: {year}, o: {o}, c: {c}, h: {h}, l: {l} }}'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content[:old.start()] + new_line + content[old.end():])


def append_ohlc_year(path, year, o, c, h, l):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    insert_pos = content.rfind('  ]\n}')
    if insert_pos == -1:
        print(f'{os.path.basename(path)} 格式不符，無法新增 {year} 年資料')
        return
    new_line = f'    {{ y: {year}, o: {o}, c: {c}, h: {h}, l: {l} }},\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content[:insert_pos] + new_line + content[insert_pos:])
    print(f'{os.path.basename(path)} 已新增 {year} 年資料')


# ── SPY ──────────────────────────────────────────────────────────────────────

def fetch_spy_ytd(year):
    try:
        import yfinance as yf
        full = yf.Ticker('SPY').history(period='max')
        if full.empty:
            return None, None, None, None
        ytd = full[full.index.year == year]
        if ytd.empty:
            return None, None, None, None
        return (
            round(float(ytd['Open'].iloc[0]),  2),
            round(float(ytd['Close'].iloc[-1]), 2),
            round(float(ytd['High'].max()),     2),
            round(float(ytd['Low'].min()),      2),
        )
    except Exception as e:
        print(f'SPY fetch error: {e}')
    return None, None, None, None


# ── 成分股報酬率更新 ─────────────────────────────────────────────────────────

def fetch_tw_prices(date_str):
    """TWSE 批次 API，回傳 {股票代號: 收盤價} dict。"""
    url = f'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date_str}&type=ALL&response=json'
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        d = r.json()
        if d.get('stat') != 'OK':
            return {}
        # table[8] = 每日收盤行情(全部)，index 8 = 收盤價
        table = next((t for t in d.get('tables', []) if '收盤價' in t.get('fields', [])), None)
        if not table:
            return {}
        close_idx = table['fields'].index('收盤價')
        return {row[0]: float(row[close_idx].replace(',', ''))
                for row in table['data']
                if row[close_idx] not in ('--', '', None)}
    except Exception as e:
        print(f'TWSE 批次價格 fetch error: {e}')
    return {}


def update_analysis_data(prices):
    """依最新股價重算 type=current 各股報酬率，寫回 analysis_data.js。"""
    with open(ANALYSIS_DATA_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'const ANALYSIS_DATA = ({.*});', content, re.DOTALL)
    if not m:
        print('analysis_data.js 格式異常，略過')
        return
    data = json.loads(m.group(1))

    updated, missing = 0, []
    all_stocks = (
        [(s, 'currentStocks')  for s in data.get('currentStocks',  []) if s.get('type') == 'current'] +
        [(s, 'departedStocks') for s in data.get('departedStocks', [])
         if s.get('return') != -100 and '已下市' not in s.get('name', '')]
    )
    for stock, _ in all_stocks:
        entry = stock.get('entryPrice')
        if not entry:
            continue
        code = str(stock['code'])
        price = prices.get(code)
        if price is None:
            missing.append(code)
            continue
        new_ret = round((price / entry - 1) * 100, 1)
        if new_ret != stock['return']:
            stock['return'] = new_ret
            updated += 1

    if updated:
        s = json.dumps(data, ensure_ascii=False, indent=2)
        with open(ANALYSIS_DATA_PATH, 'w', encoding='utf-8') as f:
            f.write(f'const ANALYSIS_DATA = {s};\n')
        print(f'analysis_data.js 已更新 {updated} 支股票')
    else:
        print('analysis_data.js 無變化')
    if missing:
        print(f'  找不到股價: {missing}')


# ── 讀 / 寫 data_live.js ─────────────────────────────────────────────────────

def read_stored():
    with open(LIVE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    def section(name):
        m = re.search(rf'{name}:\s*\{{([^}}]+)\}}', content, re.DOTALL)
        return m.group(1) if m else ''

    def val_f(text, key):
        m = re.search(rf'{key}:\s*([-\d.]+)', text)
        return float(m.group(1)) if m else 0.0

    def val_i(text, key):
        m = re.search(rf'{key}:\s*(\d+)', text)
        return int(m.group(1)) if m else 0

    def val_s(text, key):
        m = re.search(rf"{key}:\s*'([^']*)'", text)
        return m.group(1) if m else ''

    tx = section('taiex')
    vx = section('vt')

    return {
        'taiex': {
            'current': val_f(tx, 'current'), 'currentDate': val_s(tx, 'currentDate'),
            'ath': val_f(tx, 'ath'), 'athDate': val_s(tx, 'athDate'),
            'athYtdCount': val_i(tx, 'athYtdCount'), 'athYtdYear': val_i(tx, 'athYtdYear'),
        },
        'vt': {
            'current': val_f(vx, 'current'), 'currentDate': val_s(vx, 'currentDate'),
            'ath': val_f(vx, 'ath'), 'athDate': val_s(vx, 'athDate'),
            'athYtdCount': val_i(vx, 'athYtdCount'), 'athYtdYear': val_i(vx, 'athYtdYear'),
        },
    }


def write_live(taiex, vt):
    updated_at = datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M')
    content = f"""const DATA_LIVE = {{
  taiex: {{
    current: {taiex['current']},
    currentDate: '{taiex['currentDate']}',
    ath: {taiex['ath']},
    athDate: '{taiex['athDate']}',
    dropFromAth: {taiex['dropFromAth']},
    athYtdCount: {taiex['athYtdCount']},
    athYtdYear: {taiex['athYtdYear']},
  }},
  vt: {{
    current: {vt['current']},
    currentDate: '{vt['currentDate']}',
    ath: {vt['ath']},
    athDate: '{vt['athDate']}',
    dropFromAth: {vt['dropFromAth']},
    athYtdCount: {vt['athYtdCount']},
    athYtdYear: {vt['athYtdYear']},
  }},
  updatedAt: '{updated_at}',
}};
"""
    with open(LIVE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    stored = read_stored()

    this_year = datetime.now(TW_TZ).year

    def update_ytd_count(stored_data, new_ath_date, old_ath_date):
        count = stored_data['athYtdCount']
        year  = stored_data['athYtdYear']
        if year != this_year:
            count, year = 0, this_year
        if new_ath_date != old_ath_date:
            count += 1
        return count, year

    # ── TAIEX ──
    t_date, t_close, t_high, t_low = fetch_taiex_today()
    if t_close is None:
        print('無 TAIEX 今日資料，保留上次數值')
        t_close    = stored['taiex']['current']
        t_date     = stored['taiex']['currentDate']
        t_ath      = stored['taiex']['ath']
        t_ath_date = stored['taiex']['athDate']
        t_ytd_count, t_ytd_year = stored['taiex']['athYtdCount'], stored['taiex']['athYtdYear']
    else:
        print(f'TAIEX 今日 {t_date}  收盤 {t_close}  最高 {t_high}  最低 {t_low}')
        t_ath      = stored['taiex']['ath']
        t_ath_date = stored['taiex']['athDate']
        if t_high > t_ath:
            t_ath, t_ath_date = t_high, t_date
            print(f'TAIEX 新 ATH！{t_ath} @ {t_ath_date}')
        t_ytd_count, t_ytd_year = update_ytd_count(stored['taiex'], t_ath_date, stored['taiex']['athDate'])

    # ── data_0050.js 當年度增量更新 ──
    if t_low is not None:
        yr = read_ohlc_year(D0050_PATH, this_year)
        if yr:
            new_c = t_close
            new_h = max(yr['h'], t_high)
            new_l = min(yr['l'], t_low)
            if new_c != yr['c'] or new_h != yr['h'] or new_l != yr['l']:
                write_ohlc_year(D0050_PATH, this_year, yr['o'], new_c, new_h, new_l)
                print(f'data_0050.js {this_year} 已更新  c={new_c}  h={new_h}  l={new_l}')
            else:
                print(f'data_0050.js {this_year} 無變化')
        else:
            print(f'data_0050.js 找不到 {this_year} 年資料，略過')

    # ── VT ──
    v_date, v_close, v_high, v_hist_ath, v_hist_ath_date, v_ytd_high, v_ytd_low = fetch_vt()
    if v_close is None:
        print('無 VT 資料，保留上次數值')
        v_close    = stored['vt']['current']
        v_date     = stored['vt']['currentDate']
        v_ath      = stored['vt']['ath']
        v_ath_date = stored['vt']['athDate']
        v_ytd_count, v_ytd_year = stored['vt']['athYtdCount'], stored['vt']['athYtdYear']
    else:
        print(f'VT 最新 {v_date}  收盤 {v_close}  最高 {v_high}  歷史ATH {v_hist_ath} @ {v_hist_ath_date}')
        v_ath      = v_hist_ath
        v_ath_date = v_hist_ath_date
        if v_high > v_ath:
            v_ath, v_ath_date = v_high, v_date
            print(f'VT 新 ATH！{v_ath} @ {v_ath_date}')
        v_ytd_count, v_ytd_year = update_ytd_count(stored['vt'], v_ath_date, stored['vt']['athDate'])

    # ── data_vt.js 當年度更新（YTD 精確計算）──
    if v_ytd_high is not None and v_ytd_low is not None:
        vyr = read_ohlc_year(DATA_VT_PATH, this_year)
        if vyr:
            if v_close != vyr['c'] or v_ytd_high != vyr['h'] or v_ytd_low != vyr['l']:
                write_ohlc_year(DATA_VT_PATH, this_year, vyr['o'], v_close, v_ytd_high, v_ytd_low)
                print(f'data_vt.js {this_year} 已更新  c={v_close}  h={v_ytd_high}  l={v_ytd_low}')
            else:
                print(f'data_vt.js {this_year} 無變化')
        else:
            print(f'data_vt.js 找不到 {this_year} 年資料，略過')

    # ── SPY ──
    spy_o, spy_c, spy_h, spy_l = fetch_spy_ytd(this_year)
    if spy_c is not None:
        print(f'SPY {this_year}  開盤 {spy_o}  收盤 {spy_c}  最高 {spy_h}  最低 {spy_l}')
        syr = read_ohlc_year(DATA_SPY_PATH, this_year)
        if syr:
            if spy_c != syr['c'] or spy_h != syr['h'] or spy_l != syr['l']:
                write_ohlc_year(DATA_SPY_PATH, this_year, syr['o'], spy_c, spy_h, spy_l)
                print(f'data_spy.js {this_year} 已更新  c={spy_c}  h={spy_h}  l={spy_l}')
            else:
                print(f'data_spy.js {this_year} 無變化')
        else:
            append_ohlc_year(DATA_SPY_PATH, this_year, spy_o, spy_c, spy_h, spy_l)
    else:
        print(f'無 SPY {this_year} 資料，略過')

    # ── 成分股報酬率 ──
    if t_date:
        import time; time.sleep(2)
        tw_prices = fetch_tw_prices(t_date.replace('-', ''))
        if tw_prices:
            update_analysis_data(tw_prices)
        else:
            print('無法取得 TWSE 批次價格，略過 analysis_data.js')

    t_drop = round((t_close - t_ath) / t_ath * 100, 2) if t_ath and t_close else 0
    v_drop = round((v_close - v_ath) / v_ath * 100, 2) if v_ath and v_close else 0

    write_live(
        taiex={'current': t_close, 'currentDate': t_date, 'ath': t_ath, 'athDate': t_ath_date, 'dropFromAth': t_drop, 'athYtdCount': t_ytd_count, 'athYtdYear': t_ytd_year},
        vt=   {'current': v_close, 'currentDate': v_date, 'ath': v_ath, 'athDate': v_ath_date, 'dropFromAth': v_drop, 'athYtdCount': v_ytd_count, 'athYtdYear': v_ytd_year},
    )
    print('data_live.js 已更新')


if __name__ == '__main__':
    main()
