import requests
from bs4 import BeautifulSoup
import time
import re
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm

# 日本語フォントを設定
font_path = "/System/Library/Fonts/Hiragino Sans GB.ttc" 
font_prop = fm.FontProperties(fname=font_path)
rcParams['font.family'] = font_prop.get_name()


# 地域ごとのURLリスト
regions = {
    "新潟県 / 月岡・阿賀野川":"https://hotel.his-j.com/search/?t=W8y9a48VcO4v6fqY&stayPrefecture=15&stayArea=&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=117&district=&minRate=0&maxRate=",
    "新潟県 / 瀬波・村上・岩船":"https://hotel.his-j.com/search/?t=8Kd8jDbmZ4s1JNgy&stayPrefecture=15&stayArea=117&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=113&district=&minRate=0&maxRate=",
    "新潟県 / 燕・三条・岩室・弥彦":"https://hotel.his-j.com/search/?t=SynRm8VlDl1wKtuN&stayPrefecture=15&stayArea=117&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=116&district=&minRate=0&maxRate=",
    "新潟県 / 柏崎・寺泊・長岡・魚沼（湯之谷）":"https://hotel.his-j.com/search/?t=3MNoxZwmh1LuoGIY&stayPrefecture=15&stayArea=117&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=110&district=&minRate=0&maxRate=",
    "新潟県 / 南魚沼・十日町・津南（六日町）":"https://hotel.his-j.com/search/?t=KNtwAxBKNOX6zrKG&stayPrefecture=15&stayArea=110&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=111&district=&minRate=0&maxRate=",
    "新潟県 / 越後湯沢・苗場":"https://hotel.his-j.com/search/?t=uW4TQbYYK8OIFHQK&stayPrefecture=15&stayArea=110&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=112&district=&minRate=0&maxRate=",
    "新潟県 / 上越・糸魚川・妙高":"https://hotel.his-j.com/search/?t=KYYLp5DidTf4rLBZ&stayPrefecture=15&stayArea=112&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=114&district=&minRate=0&maxRate=",
    "新潟県 / 佐渡":"https://hotel.his-j.com/search/?t=OfdQoIGA30GJIS3s&stayPrefecture=15&stayArea=112&stayDistrict=&hotelCode=&checkInDate=20240201&checkOutDate=20240204&room1Adult=2&sortHotelKey=rateDesc&prefecture=15&area=115&district=&minRate=0&maxRate=",
}

# 地域ごとの平均宿代を格納する辞書
average_prices = {}

# 地域ごとにスクレイピング
for region, url in regions.items():
    print(f"\n地域: {region}")
    res = requests.get(url)
    time.sleep(1)  # サーバー負荷軽減のために待機
    html_soup = BeautifulSoup(res.content, 'html.parser')

    # 宿情報の親要素を検索
    hotels = html_soup.find_all('div', {"class": 'item-wrap'})

    # 宿代リスト
    prices = []

    for hotel in hotels:
        name_tag = hotel.find('span', {"class": 'item-wrap__title-ja'})
        price_tag = hotel.find('span', {"class": 'price--body'})
        price_small_tag = hotel.find('span', {"class": 'price--body-s'})

        # 宿名、宿代、宿代の桁を取得
        name = name_tag.text.strip() if name_tag else "情報なし"
        price = price_tag.text.strip() if price_tag else "情報なし"
        price_small = price_small_tag.text.strip() if price_small_tag else "情報なし"

        # 宿代の数値部分を抽出（例: "¥12,345" → 12345）
        full_price = price + price_small
        price_value = re.sub(r'[^\d]', '', full_price)

        # 数値が取得できた場合のみリストに追加
        if price_value:
            prices.append(int(price_value))

        # 結果を表示
        print(f"宿名: {name}, 宿代: {full_price}")

    # 平均値を計算
    if prices:
        average_price = sum(prices) / len(prices)
        average_prices[region] = average_price
    else:
        average_prices[region] = 0  # 宿代がない場合は0を設定

# ヒストグラムの表示
regions_list = list(average_prices.keys())
average_price_list = list(average_prices.values())

plt.figure(figsize=(10, 6))
bars = plt.barh(regions_list, average_price_list, color='skyblue')

# 横棒の隣に平均宿代を表示
for bar, price in zip(bars, average_price_list):
    plt.text(
        bar.get_width() + 5000,  # 横棒の終端から少し右にずらして表示
        bar.get_y() + bar.get_height() / 2,  # 横棒の中央に合わせる
        f"¥{price:,.0f}",  # カンマ区切りの日本円表記
        va='center',
        fontproperties=font_prop,
        fontsize=10
    )

# 軸ラベルやタイトルの設定
plt.xlabel("平均宿代 (円)", fontproperties=font_prop)
plt.ylabel("地域", fontproperties=font_prop)
plt.title("地域ごとの平均宿代", fontproperties=font_prop)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()