# from https://github.com/liamroddy/Teanglann-Tarraingeoir-Focal-An-Lae

from bs4 import BeautifulSoup
import requests

'''
EXAMPLE wod div:

<div class="wod">
    <span class="title">FOCAL AN LAE</span> 
    <span class="entry">
            <a class="headword" href="/ga/?s=iarmhairt">iarmhairt</a>
            <span class="sense fgb"><span class="box">&nbsp;</span>&nbsp;<a href="/ga/fgb/?s=iarmhairt"><span class="tag">f.</span> <span class="def">result, consequence</span></a></span> 
            <span class="sense fb"><span class="box">&nbsp;</span>&nbsp;<a href="/ga/fb/?s=iarmhairt"><span class="tag">bain3</span> <span class="def">toradh, iarsma</span></a></span>     
    </span>
</div>
'''

'''
desired format:

Focal an lae: iarmhairt; f. result, consequence; bain3 toradh, iarsma
'''

URL = "https://www.teanglann.ie/ga/"

def get_focal_an_lae(url = URL):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        wod_div = soup.find('div', class_='wod')
        if not wod_div:
            return "Error: 'wod' div not found"
        
        title = wod_div.find('span', class_='title').text.strip() if wod_div.find('span', class_='title') else "Unknown"
        
        headword = wod_div.find('a', class_='headword').text.strip() if wod_div.find('a', class_='headword') else "Unknown"
        
        senses = []
        for sense in wod_div.find_all('span', class_='sense'):
            tag = sense.find('span', class_='tag').text.strip() if sense.find('span', class_='tag') else "Unknown"
            definition = sense.find('span', class_='def').text.strip() if sense.find('span', class_='def') else "Unknown"
            senses.append(f"{tag} {definition}")
        
        senses_text = "; ".join(senses)
        return f"{title}: {headword}; {senses_text}"
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}"
    except Exception as e:
        return f"Error processing data: {str(e)}"

if __name__ == "__main__":
    result = get_focal_an_lae()
    print(result)
