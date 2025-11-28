import requests
import os

def download_nyc_311_csv(year=2023, output_file=None):
    """
    Download NYC 311 Service Requests CSV filtered by year to keep file size manageable.
    Saves file to output_file.
    """
    if output_file is None:
        output_file = f'./data/nyc_311_{year}.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    base_url = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
    soql_query = f"?$where=created_date between '{year}-01-01T00:00:00' and '{year}-12-31T23:59:59'&$limit=200000"
    download_url = base_url + soql_query

    print(f"[⬇] Downloading NYC 311 data for {year} from:\n{download_url}")

    response = requests.get(download_url, stream=True)

    if response.status_code != 200:
        print(f"[❌] Failed to download dataset. Status code: {response.status_code}")
        return False

    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"[✅] Download complete. Saved to {output_file}")
    return output_file

if __name__ == "__main__":
    download_nyc_311_csv()
