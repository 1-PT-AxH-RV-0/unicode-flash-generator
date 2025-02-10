import requests
import os
import zipfile
import io

def extract_zip_from_bytes(zip_bytes, path):
    zip_file = io.BytesIO(zip_bytes)
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(path)


CUR_FOLDER = os.path.dirname(__file__)
NAMES_LIST_PATH = os.path.join(os.path.dirname(CUR_FOLDER), 'data', 'NamesList.txt')
UCD_XLM_PATH = os.path.join(os.path.dirname(CUR_FOLDER), 'data', 'ucd.nounihan.flat.xml')

if not os.path.exists(NAMES_LIST_PATH):
    url = 'https://www.unicode.org/Public/UCD/latest/ucd/NamesList.txt'
    print('正在更新 NamesList.txt……')
    r = requests.get(url)
    open(NAMES_LIST_PATH, 'w').write(r.text)

if not os.path.exists(UCD_XLM_PATH):
    url = 'https://www.unicode.org/Public/UCD/latest/ucdxml/ucd.nounihan.flat.zip'
    print('正在更新 ucd.nounihan.flat.xml……')
    r = requests.get(url)
    content = r.content
    print('正在解压 ucd.nounihan.flat.zip……')
    extract_zip_from_bytes(content, os.path.dirname(UCD_XLM_PATH))
    