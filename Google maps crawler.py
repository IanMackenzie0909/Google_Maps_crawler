import googlemaps
import json
import time
import os

API_KEY = 'your_api'  # 請替換為你的Google Maps API金鑰
gmaps = googlemaps.Client(key=API_KEY)

def get_landmark_info(client, landmark):
    """
    取得地標的地址和郵遞區號資訊

    Args:
        client: Google Maps API 客戶端
        landmark: 地標名稱

    Returns:
        dict: 包含地址和郵遞區號的字典，若無法取得資訊則返回 None
    """
    try:
        geocode_result = client.geocode(landmark, language='zh-TW')
        if not geocode_result:
            return None
        return {
            "address": geocode_result[0]['formatted_address'],
            "postal_code": next((comp['long_name'] for comp in geocode_result[0]['address_components'] if 'postal_code' in comp['types']), None)
        }
    except Exception as e:
        print(f"Error getting landmark info: {e}")
        return None

def search_nearby(client, location, radius, keyword):
    """
    搜尋地標附近的指定類型店家

    Args:
        client: Google Maps API 客戶端
        location: 地標的經緯度座標 (tuple)
        radius: 搜尋範圍半徑（公尺）
        keyword: 店家種類關鍵字

    Returns:
        list: 包含所有符合條件店家的資訊列表
    """
    places = []
    page_token = None

    while True:
        try:
            # 使用 Google Maps API 搜尋附近的店家
            places_result = client.places_nearby(location=location, radius=radius, keyword=keyword, type='point_of_interest', language='zh-TW', page_token=page_token)
            for place in places_result.get('results', []):
                places.append({
                    "商店名稱": place.get('name'),
                    "地址": place.get('vicinity'),
                    "評分": place.get('rating', 'N/A')
                })
            page_token = places_result.get('next_page_token')
            if not page_token:
                break
            time.sleep(2)  # Google 建議的間隔時間
        except Exception as e:
            print(f"Error searching nearby places: {e}")
            break

    return places

def main():
    """
    主函數，執行地標資訊查詢及附近店家搜尋
    """
    landmark = input("請輸入地標名稱 (中文或英文): ")
    landmark_info = get_landmark_info(gmaps, landmark)
    if not landmark_info:
        print("無法取得地標資訊")
        return

    print(f"地標資訊：{landmark_info}")

    while True:
        # 輸入搜尋範圍半徑
        radius_input = input("請輸入查詢方圓多少公尺 (或按下 'Enter' 結束查詢): ")
        if not radius_input:
            print("結束查詢")
            break

        try:
            radius = int(radius_input)
        except ValueError:
            print("輸入的半徑不是有效的數字")
            continue

        # 輸入店家種類
        place_type = input("請輸入店家種類 (例如：拉麵店、飲料店) (或按下 'Enter' 結束查詢): ")
        if not place_type:
            print("結束查詢")
            break

        # 取得地標的經緯度座標
        location = gmaps.geocode(landmark, language='zh-TW')[0]['geometry']['location']
        nearby_places = search_nearby(gmaps, (location['lat'], location['lng']), radius, place_type)
        print(f"找到的 {place_type} 總數: {len(nearby_places)}")

        # 將結果輸出為 JSON 文件
        output_filename = f"{landmark}方圓{radius}公尺{place_type}介紹.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(nearby_places, f, ensure_ascii=False, indent=4)

        print(f"{place_type} 詳細資料已輸出至 {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    main()
