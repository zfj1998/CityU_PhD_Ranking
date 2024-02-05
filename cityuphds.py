from scholarly import scholarly
from bs4 import BeautifulSoup
import re
import json
import ipdb
import os
from tqdm import tqdm

def load_html_into_str(html_file):
    with open(html_file, 'r', encoding='utf8') as file:
        return file.read()

def dump_jsonl(data, filename):
    with open(filename, 'w+', encoding='utf8') as file:
        for line in data:
            json.dump(line, file)
            file.write('\n')

def load_json(filename):
    with open(filename, 'r', encoding='utf8') as file:
        return json.load(file)

def dump_json(data, filename):
    with open(filename, 'w', encoding='utf8') as file:
        json.dump(data, file)

def get_phd_names():
    # Your HTML content
    html_content = load_html_into_str('phds.html')

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all rows in the table body
    rows = soup.find('tbody').find_all('tr')

    # Extract names and emails
    students = []
    for row in rows:
        # Extracting name
        full_name = row.find_all('td')[0].text.strip()
        if full_name.startswith('Miss') or full_name.startswith('Ms') or full_name.startswith('Mr'):
            full_name = full_name.split(' ', 1)[1]
            full_name = full_name.replace(', ', ' ')
        name_filtered = re.sub(r"[^\x00-\x7F]+", "", full_name).strip()
        
        # Extracting email, which is in the href attribute of the <a> tag
        email_link = row.find('a')
        email = email_link['href'].replace('mailto:', '') if email_link else None
        
        students.append((name_filtered, email))

    return students

def get_phd_info(name):
    search_query = scholarly.search_author(name)
    for author in search_query:
        if 'cityu' in str(author).lower() or 'city u' in str(author).lower():
            return author
    return None

def main():
    result_path = 'phd_info.jsonl'
    author_info = load_json(result_path) if os.path.exists(result_path) else {}
    students = get_phd_names()
    for student in tqdm(students):
        name, email = student
        ipdb.set_trace()
        if email in author_info:
            continue
        print(f'Name: {name}, Email: {email}')
        author = get_phd_info(name)
        if not author:
            print('No author found')
            author_info[email] = None
        print(author)
        print()
        author_info[email] = (name, author)
        dump_json(author_info, 'phd_info.jsonl')

if __name__ == '__main__':
    main()