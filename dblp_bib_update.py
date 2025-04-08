import bibtexparser
import requests
from urllib.parse import quote
import re
import time
from bs4 import BeautifulSoup
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import homogenize_latex_encoding

def update_bib_from_dblp(input_file, output_file):
    # 配置bibtexparser
    parser = BibTexParser(common_strings=True)
    # parser.customization = homogenize_latex_encoding
    parser.ignore_nonstandard_types = False

    # 读取原始Bib文件
    with open(input_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f, parser=parser)
    
    updated_entries = []
    total = len(bib_database.entries)
    
    for idx, entry in enumerate(bib_database.entries, 1):
        print(f"Processing entry {idx}/{total}: {entry.get('title', '')}")
        
        # 保留原始条目类型和citekey
        updated_entry = {
            'ENTRYTYPE': entry['ENTRYTYPE'],
            'ID': entry['ID']
        }
        
        # 尝试通过标题搜索
        title = entry.get('title', '').strip('{}')
        result = search_dblp(title, entry.get('year'))
        
        if result:
            print(f"Found match in DBLP")
            # 合并字段（优先使用DBLP的数据）
            # updated_entry.update({
            #     'author': format_authors(result.get('authors', [])),
            #     'title': f"{{{result.get('title', title)}}}",
            #     'booktitle': result.get('booktitle', entry.get('booktitle', '')),
            #     'pages': result.get('pages', entry.get('pages', '')),
            #     'year': result.get('year', entry.get('year', '')),
            #     'publisher': result.get('publisher', entry.get('publisher', '')),
            #     'url': result.get('ee', entry.get('url', ''))
            # })
            
            # # 特殊处理会议论文
            # if updated_entry['ENTRYTYPE'] == 'inproceedings':
            #     updated_entry['booktitle'] = result.get('venue', entry.get('booktitle', ''))
            updated_entry.update(**result)
                
        else:
            print("No DBLP match found, keeping original")
            updated_entry.update(entry)
        
        updated_entries.append(updated_entry)
        time.sleep(1)  # 遵守API的礼貌间隔

    # 保存更新后的Bib文件
    new_db = BibDatabase()
    new_db.entries = updated_entries
    
    with open(output_file, 'w', encoding='utf-8') as f:
        bibtexparser.dump(new_db, f)

def search_dblp(title, year=None):
    try:
        query = quote(title)
        url = f"https://dblp.org/search/publ/api?q={query}&format=json"
        response = requests.get(url, timeout=1000)
        response.raise_for_status()
        
        data = response.json()
        hits = data.get('result', {}).get('hits', {}).get('hit', [])
        
        for hit in hits:
            info = hit.get('info', {})
            # 验证年份和标题匹配
            # if str(info.get('year')) == str(year) and \
            #    info.get('title', '').lower() == title.lower():
            #     return parse_dblp_info(info)
            if abs(int(info.get('year')) - int(year)) <= 3 and \
               info.get('title', '').lower().rstrip(".") == title.lower():
                return parse_dblp_info(info)
                
        return None
    except Exception as e:
        print(f"Search error: {str(e)}")
        return None

    
def parse_dblp_info(info):
    # authors = []
    # if 'authors' in info:
    #     for author in info['authors']['author']:
    #         if isinstance(author, dict):
    #             authors.append(f"{author.get('given', '')} {author.get('family', '')}")
    
    # return {
    #     'title': info.get('title', ''),
    #     'booktitle': info.get('booktitle', ''),
    #     'year': info.get('year', ''),
    #     'venue': info.get('venue', ''),
    #     'pages': info.get('pages', ''),
    #     'publisher': info.get('publisher', ''),
    #     'ee': info.get('ee', ''),
    #     'author': authors
    # }
    dblp_url = info['url'].replace("rec/", "rec/bibtex/") + ".bib"
    # 第二步：获取BibTeX内容
    bib_response = requests.get(dblp_url, timeout=1000)
    bib_response.raise_for_status()
    
    # 解析搜索结果
    soup = BeautifulSoup(bib_response.text, 'html.parser')
    dblp_str = soup.find_all(class_='verbatim')[0].text
    
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    dblp_db = bibtexparser.loads(dblp_str, parser=parser)
    dblp_entry = dblp_db.entries[0]
    
    for key in dblp_entry:
        dblp_entry[key] = dblp_entry[key].replace('\n', ' ').replace('\r', '')
    
    dblp_entry.pop('ID', None)  # 删除ID字段
    dblp_entry.pop('ENTRYTYPE', None)  # 删除ENTRYTYPE字段
    dblp_entry.pop('biburl', None)  # 删除url字段
    dblp_entry.pop('bibsource', None)  # 删除url字段
    dblp_entry.pop('doi', None)  # 删除url字段
    dblp_entry.pop('url', None)  # 删除url字段
        
    return dblp_entry

def format_authors(authors):
    formatted = []
    for author in authors:
        if ',' in author:
            formatted.append(author)
        else:
            parts = author.split()
            if len(parts) > 1:
                formatted.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
            else:
                formatted.append(author)
    return ' and '.join(formatted)

if __name__ == "__main__":
    update_bib_from_dblp('input.bib', 'updated.bib')
