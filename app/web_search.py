import requests

#CONNECTS TO GOOGLE SEARCH URL, PARSES PARAMS, RETURNS FOUND RESULTS

def google_search(query, api_key, cx, num=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("items", [])
    except Exception as e:
        return {
            "error": "google_search_failed",
            "details": str(e),
        }
