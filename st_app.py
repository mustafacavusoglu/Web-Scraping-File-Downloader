import os
import requests
import pandas as pd
import streamlit as st
from pathlib import Path
from bs4 import BeautifulSoup

st.title("Yerel Yönetimler'den Dosya İndirme")

Path("Downloads").mkdir(parents=True, exist_ok=True)


def control_file_is_exist(file_names, files_info):
    
    if os.path.exists("files_info.csv"):
        already_exist = pd.read_csv("files_info.csv")
        if file_names in already_exist["dosya"].values:
            return True
        else:
            # concat two dataframes
            files_info = pd.DataFrame(files_info)
            df = pd.concat([already_exist, files_info], axis=0)
            df.to_csv("files_info.csv", index=False)
            return False
    else:
        df = pd.DataFrame(files_info)
        df.to_csv("files_info.csv", index=False)
        return False

def download_files(url):
    info_area = st.empty()
    counter = 0
    exist_count = 0
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    files_info = {
        "sıra" : [],
        "tarih" : [],
        "sayı" : [],
        "konu" : [],
        "dosya" : []
    }

    print(f"URL: {url} dosya bilgileri:")
    tr_tags = soup.find_all('tr')
    for tr_tag in tr_tags[1:10]:
        # <td> etiketlerini bul
        td_tags = tr_tag.find_all('td')
        
        
        # <td> etiketlerinin içeriğini ve linkleri yazdır.
        
        sıra = td_tags[0].text.strip()
        tarih = td_tags[1].text.strip()
        sayı = td_tags[2].text.strip()
        konu = td_tags[3].text.strip()
        file_link = td_tags[4].find('a')["href"]
        dosya_adi = file_link.split("/")[-1]
        
        files_info["sıra"].append(sıra)
        files_info["tarih"].append(tarih)
        files_info["sayı"].append(sayı)
        files_info["konu"].append(konu)
        files_info["dosya"].append(dosya_adi)
        
        if not control_file_is_exist(dosya_adi, files_info):
            response = requests.get(file_link)
            info_area.success(f"Dosya: {file_link} dosya indiriliyor...")
            with open("Downloads/" + dosya_adi, "wb") as f:
                f.write(response.content)
            counter += 1
        else:   
            info_area.warning(f"{dosya_adi} dosyası zaten indirildi.")
            exist_count += 1
    if exist_count != 0:
        info_area.info(f"Downloads klasörüe toplam {counter} dosya indirildi. {exist_count} dosya zaten mevcut.")
    else:
        info_area.info(f"Downloads klasörüe toplam {counter} dosya indirildi.")

url_area = st.text_input(label="URL giriniz: ", placeholder="https://yerelyonetimler.csb.gov.tr/belediye-gorusleri-i-98891")

if st.button("İndir"):
    download_files(url_area)
    
    
