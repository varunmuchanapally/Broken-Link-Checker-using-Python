#! python3

# Broken links checker and analyzer
# written in Python
# Author: Amusa Abayomi
# Github: Amusa-Paulos
# Twitter: @paulos_ab

import requests, os, re, random
from bs4 import BeautifulSoup

def run(url, sitemap=False):
    os.chdir(os.getcwd())
    log_file_name = "report-logs"
    rm_trailing_slash = re.compile(r'\/$').sub('', url)
    rm_trailing_slash = "http://" + rm_trailing_slash if not re.compile(r'^http').search(rm_trailing_slash) else url
    print(f"Paulos Ab: {f'getting {rm_trailing_slash}...'.rjust(12)}")
    req = requests.get(rm_trailing_slash)
    domain_main_name = re.compile(r'(www\.)?([a-zA-Z0-9]+)\.\w{3,9}').search(rm_trailing_slash).groups()[1].capitalize()
    
    os.makedirs(os.path.join(os.getcwd(), log_file_name), exist_ok=True)
    if sitemap:
        os.makedirs(f"{os.path.join('report-logs', domain_main_name)}", exist_ok=True)
        general_file = open(f"{os.path.join(os.path.join(log_file_name, domain_main_name), domain_main_name + '_website_deep_scan.txt')}", "a")

    
    domain_name = re.compile(r"(http(s)?\:\/\/)?(www\.)?[a-zA-Z0-9]+\.\w{3,9}(\.\w{2,3})?(\/)?").search(rm_trailing_slash).group()
    domain_name = domain_name + '/' if not re.compile(r'\/$').search(domain_name) else domain_name
    if req.status_code == 404:
        broken_link_msg = f"Paulos Ab: {'-'*10} {f'{rm_trailing_slash} returns {req.status_code}, Link is broken!'.rjust(12)}"
        print("*"*len(broken_link_msg))
        return print(broken_link_msg)
    if req.status_code >= 600:
        denied_link_msg = f"Paulos Ab: {'-'*10} {rm_trailing_slash} {f':::returns  {str(req.status_code)}'} {f' ::: link not permited for scanning by host ::: cant determine status'.rjust(15)}\n"
        print("*"*len(denied_link_msg))
        return print(denied_link_msg)
    print(f"Paulos Ab: {f'got {rm_trailing_slash}'.rjust(12)}")
    print(f"Paulos Ab: {f'parsing {rm_trailing_slash} content...'.rjust(12)}")
    soup = BeautifulSoup(req.content, 'html.parser')
    print(f"Paulos Ab: {f'{rm_trailing_slash} parsed successfully!'.rjust(12)}")
    links = soup.find_all('a')
    print(f"\nPaulos Ab:  {f'now searching for broken links in {rm_trailing_slash}'.rjust(12)}\n")
    broken_link = 0
    okay_links = 0
    denied_links = 0
    load_too_long_links = 0
    all_links = len(links)
    broken_link_arr = []
    okay_links_arr = []
    denied_links_arr = []
    load_too_long_links_arr = []
    trimed_links = remove_duplicate_links(links)
    print(f"Paulos Ab: {f'analyzing {len(trimed_links)} links in {rm_trailing_slash}...'.rjust(12)}\n")
    try: 
        for link in trimed_links:
            url_to_check = f"{domain_name}{link}" if link.startswith('/') else f"{rm_trailing_slash}/{link}"  if link.startswith('/') or link.startswith('#') or not "http" in link else link
            url_to_check = re.compile(r"\/{2}").sub('/', url_to_check)
            replace_broken_http_param = re.compile(r"(https?\:\/)|(http?\:\/)")
            search_in_url = replace_broken_http_param.search(url_to_check)
            url_to_check = re.compile(r"(https?\:\/)|(http?\:\/)").sub(search_in_url.group(0) + '/', url_to_check)
            url_to_check = re.compile(r"\/$").sub('', url_to_check)
            print(f"{'+'*10}checking {url_to_check}...")
            if url_to_check == '#':
                print(f'{"-"*10}link not routable\n')
                continue
            try: 
                get_link = requests.get(url_to_check, timeout=25)
                if get_link.status_code >= 500 and get_link.status_code < 600:
                    broken_link_msg = f"{'-'*10} Link {f'{rm_trailing_slash} returns {get_link.status_code} - Internal Server Error, Link is broken!'.rjust(12)}"
                    broken_link += 1
                    print(broken_link_msg)
                    broken_link_arr.append(url_to_check + " ::: reason :::}> " + broken_link_msg)

                if get_link.status_code >= 400 and get_link.status_code < 500:
                    broken_link_msg = f"{'-'*10} Link {f'{rm_trailing_slash} returns {get_link.status_code}, Link is broken!'.rjust(12)}"
                    broken_link += 1
                    print(broken_link_msg)
                    broken_link_arr.append(url_to_check + " ::: reason :::}> " + broken_link_msg)

                if get_link.raise_for_status() is not None:
                    print(f"Paulos Ab: {f'Connection timeout while trying to get {link}, status code {get_link.status_code}'.rjust(12)}")
                    continue

                if get_link.status_code >= 600:
                        broken_text = f"{'-'*10} link {url_to_check} {f':::returns  {str(get_link.status_code)}'} {f' ::: link not permited for scanning by host ::: cant determine status'.rjust(15)}\n"
                        denied_links += 1
                        denied_links_arr.append(url_to_check + " ::: reason :::}> " + broken_text)
                        print(broken_text)
                        
                if get_link.status_code >= 200 and get_link.status_code < 300:
                    print(f"Paulos Ab: link {url_to_check} {f':::returns  {str(get_link.status_code)}'.rjust(15)} {f' ::: link Okay'.rjust(15)}\n")
                    okay_links += 1
                    okay_links_arr.append(url_to_check)
            except Exception as e:
                if "Forbidden" in str(e):
                    exception_msg_text = f"Paulos Ab: {f'Error occured while trying to get {url_to_check}...::: Error :::...'.rjust(12)} {e}\n"
                    print(exception_msg_text)
                    denied_links += 1
                    denied_links_arr.append(url_to_check + " ::: reason :::}> " + str(e))
                elif "ConnectTimeoutError" in str(e):
                    exception_msg_text = f"Paulos Ab: {f'Error occured while trying to get {url_to_check}...::: Error :::...'.rjust(12)} Connection to {url_to_check} timed out. (connect timeout={25})\n"
                    print(exception_msg_text)
                    load_too_long_links += 1
                    load_too_long_links_arr.append(url_to_check + " ::: reason :::}> " + f"Connection to {url_to_check} timed out. (connect timeout={25})")

        analytics_file_title = str(random.randint(1, 9999999)) if soup.title is None else soup.title.text
        log_directory = f"{os.getcwd()}/{os.path.join(log_file_name, domain_main_name if sitemap else '')}"
        analytics_log_file_location = f"{os.path.join(log_directory, ''.join(e for e in analytics_file_title if e.isalnum()))}_webpage_links_analysis.txt"
        analytics_log_file = open(analytics_log_file_location, 'a')
        print(f"Paulos Ab: {'Analysis'.rjust(12)}\n")
        analytics_log_file.write(f"Paulos Ab: {'Analysis'.rjust(12)}\n")
        if sitemap:
            general_file_length = general_file.readlines() if general_file.readable() else 0
            put_new_lines = '\n\n\n' if general_file_length == 0 else ''
            general_file.write(f"{put_new_lines} Link {rm_trailing_slash} analysis \n")
            general_file.write(f"Paulos Ab: {'Analysis'.rjust(12)}\n")
        analytics_header = (f"\n{'| All links |'} {'| Links ( excl. duplicates ) |'} {'| Okay links |'} {'| Broken links |'} {'| Denied links |'} {'| Slow loading links |'} ")
        print(analytics_header)
        analytics_log_file.write(analytics_header)
        if sitemap:
            general_file.write(analytics_header)
        okay_lnks_justify = (analytics_header.find('| Okay') - analytics_header.find('| Links ( excl. duplicates )'))
        broken_lnks_justify = (analytics_header.find('| Broken') - analytics_header.find('| Okay'))
        denied_lnks_justify = (analytics_header.find('| Denied') - analytics_header.find('| Broken'))
        slow_lnks_justify = (analytics_header.find('| Slow') - analytics_header.find('| Denied'))
        non_duplicates_link_justify = analytics_header.find('| Links ( excl. duplicates )')
        print(f"{f'| {all_links} |'} {f'| {len(trimed_links)} |'.rjust(non_duplicates_link_justify)} {f'| {okay_links} |'.rjust(okay_lnks_justify)} {f'| {broken_link} |'.rjust(broken_lnks_justify)} {f'| {denied_links} |'.rjust(denied_lnks_justify)} {f'| {load_too_long_links} |'.rjust(slow_lnks_justify)} ")
        analytics_log_file.write(f"\n{f'| {all_links} |'} {f'| {len(trimed_links)} |'.rjust(non_duplicates_link_justify)} {f'| {okay_links} |'.rjust(okay_lnks_justify)} {f'| {broken_link} |'.rjust(broken_lnks_justify)} {f'| {denied_links} |'.rjust(denied_lnks_justify)} {f'| {load_too_long_links} |'.rjust(slow_lnks_justify)} ")
        if sitemap:
            general_file.write(f"\n{f'| {all_links} |'} {f'| {len(trimed_links)} |'.rjust(non_duplicates_link_justify)} {f'| {okay_links} |'.rjust(okay_lnks_justify)} {f'| {broken_link} |'.rjust(broken_lnks_justify)} {f'| {denied_links} |'.rjust(denied_lnks_justify)} {f'| {load_too_long_links} |'.rjust(slow_lnks_justify)} ")
        print(f"\n\n--Broken links \n")
        analytics_log_file.write(f"\n\n--Broken links \n")
        if sitemap:
            general_file.write(f"\n\n--Broken links \n")
        for link in broken_link_arr:
            print(link)
            analytics_log_file.write(f"{link}\n")
            if sitemap:
                general_file.write(f"{link}\n")
        if len(broken_link_arr) == 0:
            print("No broken links \n")
            analytics_log_file.write("No broken links \n")
            if sitemap:
                general_file.write("No broken links \n")
        print(f"\n\n--Links access denied by host \n")
        analytics_log_file.write(f"\n\n--Links access denied by host \n")
        if sitemap:
            general_file.write(f"\n\n--Links access denied by host \n")
        for link in denied_links_arr:
            print(link)
            analytics_log_file.write(f"{link}\n")
            if sitemap:
                general_file.write(f"{link}\n")
        if len(denied_links_arr) == 0:
            print("No links denied by host \n")
            analytics_log_file.write("No links denied by host \n")
            if sitemap:
                general_file.write("No links denied by host \n")
        print(f"\n\n--Links that took too long to load \n")
        analytics_log_file.write(f"\n\n--Links that took too long to load \n")
        if sitemap:
            general_file.write(f"\n\n--Links that took too long to load \n")
        for link in load_too_long_links_arr:
            print(link)
            analytics_log_file.write(f"{link}\n")
            if sitemap:
                general_file.write(f"{link}\n")
        if len(load_too_long_links_arr) == 0:
            print("No links that took too long to load \n")
            analytics_log_file.write("No links that took too long to load \n")
            if sitemap:
                general_file.write("No links that took too long to load \n")
        print(f"\n\n--Okay links \n")
        analytics_log_file.write(f"\n\n--Okay links \n")
        if sitemap:
            general_file.write(f"\n\n--Okay links \n")
        for link in okay_links_arr:
            print(link)
            analytics_log_file.write(f"{link}\n")
            if sitemap:
                general_file.write(f"{link}\n")
        if len(okay_links_arr) == 0:
            print("No links that return 200 \n")
            analytics_log_file.write("No links that return 200 \n")
            if sitemap:
                general_file.write("No links that return 200 \n")
        print(f"\n\nGenerated analytics log file: {os.path.basename(analytics_log_file_location)}_page_links_analysis_log.txt")
        analytics_log_file.close()
        if sitemap:
            print(f"{'*'*25}\n")
    except KeyboardInterrupt as e:
        print('Paulos Ab: Analysis interrupted!')
    general_file.close()

def remove_duplicate_links(links):
    set_links = set()
    for link in links:
        if link.get('href') is None:
            continue
        set_links.add(link.get('href'))
    return list(set_links)

def main(param):
    try:
        if '--with-sitemap' in param:
            param.remove('--with-sitemap')
            link_to_xml_sitemap = "".join(param[2:])
            if link_to_xml_sitemap.startswith('http'):
                return print('Paulos Ab: Please provide a valid link to your xml sitemap!')
            print(f"Paulos Ab: {'Fetching ' + link_to_xml_sitemap + '...'.rjust(12)}")
            with open(link_to_xml_sitemap, 'r') as sitemap:
                xml_sitemap = " ".join(sitemap.readlines())
                soup = BeautifulSoup(xml_sitemap, features="xml")
                links = soup.find_all('loc')
                print(f"Paulos Ab: {'Fetched ' + link_to_xml_sitemap + '!'.rjust(12)}\n")
                print(f"Paulos Ab: Total Links: {len(links)} {'Analyzing Sitemap '.rjust(12) + link_to_xml_sitemap + '...'}\n")
                try:
                    for link in links:
                        print(f"Paulos Ab: {'Analyzing URL '.rjust(12) + link.text + '...'}")
                        run(link.text, True)
                except KeyboardInterrupt as e:
                    print('Paulos Ab: Analysis interrupted!')
        else:
            run(" ".join(param[1:]))

    except KeyboardInterrupt as e:
        print('Paulos Ab: Analysis interrupted!')
    