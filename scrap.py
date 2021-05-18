import argparse
import asyncio
import sqlite3
import re
from datetime import datetime
import requests

async def main(board, db_name):

    # SETUP
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        has_file INTEGER,
        date TEXT,
        date_unix INTEGER,
        content TEXT)
    ''')

    t_url = 'https://a.4cdn.org/'+board+'/threads.json'
    p_url = 'https://a.4cdn.org/'+board+'/thread/{}.json'
    t_json, t_headers, _ = load_json(t_url)
    t_ids = get_threads_param(t_json,'no')
    t_time = get_threads_param(t_json,'last_modified')
    
    last_mod_date = t_headers['Last-Modified']
    await asyncio.sleep(1)

    # MAIN LOOP
    try:
        while(1):

            has_board_changed = False
            while not has_board_changed:
                t_json, t_headers, t_code = load_json(t_url, {'If-Modified-Since': last_mod_date})
                if t_code == 200:
                    has_board_changed = True
                else:
                    print("HTTP Error: " + str(list_code))
                await asyncio.sleep(1)

            last_mod_date = t_headers['Last-Modified']
        
            new_t_ids = get_threads_param(t_json,'no')
            new_t_time = get_threads_param(t_json,'last_modified')
            checkable_ids = get_diff_threads(t_ids, t_time, new_t_ids, new_t_time)
            t_ids = new_t_ids
            t_time = new_t_time
            
            for t_id in checkable_ids:
                this_url = p_url.format(str(t_id))

                try:
                    p_json, _, _ = load_json(this_url)
                except:
                    continue
                p_ids = get_posts_param(p_json,'no')
                p_parent_ids = get_posts_param(p_json,'resto')
                p_time = get_posts_param(p_json,'time')
                p_date = get_posts_param(p_json,'now')
                p_content = get_posts_param(p_json,'com')
                p_content = clean_html(p_content)
                p_file = posts_have_param(p_json, 'filename')

                p_data = list(zip(p_ids, p_parent_ids, p_file, p_date, p_time, p_content))
                cur.executemany("INSERT or IGNORE INTO threads VALUES (?, ?, ?, ?, ?, ?)", p_data)
                con.commit()

                await asyncio.sleep(1)
                    
    except KeyboardInterrupt: 
        con.close()

# GET THREADS THAT WERE MODIFIED
def get_diff_threads(ids, times, new_ids, new_times):
    # If new_ids not in ids, return new_id
    # If times[new_ids] != new_times[new_ids], return new_id
    #old_set = set(ids)
    #new_set = set(new_ids)
    #ret_set = new_set.difference(old_set) #NOT NEEDED?

    ret_set = set([])
    old_map = dict(zip(ids, times))
    new_map = dict(zip(new_ids, new_times))
    for key in new_map:
        if new_map[key] != old_map.get(key):
            ret_set.add(key)

    return list(ret_set)
    
        
# LOADS JSON FILE, HANDLES ERRORS
def load_json(url, headers={'':''}):
    print('Connecting to: ' + url)
    r = requests.get(url, headers)
    return r.json(), r.headers, r.status_code


# GETS SPECIFIC DATA FROM DICTIONARY THAT CONTAINS POSTS
def get_posts_param(json_p_list, param):
    post_params = []
    for post in json_p_list['posts']:
        if param in post:
            post_param = post[param]
            post_params.append(post_param)
        else:
            post_params.append(None)
    return post_params


# RETURNS LIST OF BOOLS THAT SPECIFY IF EACH POST HAS CERTAIN CONTENT (HAS FILE, FOR EXAMPLE)
def posts_have_param(json_t_list, param):
    has_param = []
    for post in json_t_list['posts']:
        if param in post:
            has_param.append(1)
        else:
            has_param.append(0)
    return has_param


# GETS SPECIFIC DATA FROM DICTIONARY THAT CONTAINS THREADS
def get_threads_param(json_t_list, param):
    thread_params = []    
    for page in json_t_list:
        threads = page['threads']
        for thread in threads:
            if param in thread:
                thread_param = thread[param]
                thread_params.append(thread_param)
            else:
                thread_params.append(None)
    return thread_params


# CLEAN JSON HTML (SUBSTITUTE SPECIAL HTML EXPRESSIONS AND SYMBOLS)
def clean_html(exprs):
        for count, expr in enumerate(exprs):
            try:
                n_expr = expr
                n_expr = n_expr.replace('<br>', '\n')
                cleaner = re.compile(r'<.*?>')
                n_expr = re.sub(cleaner, '', n_expr)
                n_expr = n_expr.replace('&quot;', r'"')
                n_expr = n_expr.replace('&#039;', r"'") # why?
                n_expr = n_expr.replace('&amp;', r'&')
                n_expr = n_expr.replace('&lt;', r'<')
                n_expr = n_expr.replace('&gt;', r'>')
                exprs[count] = n_expr
            except:
                print("Cannot parse None object")
        return exprs
    
# PARSE ARGS
parser = argparse.ArgumentParser()
parser.add_argument("--board", type=str, default='biz')
parser.add_argument("--db-name", type=str, default='threads.db')
args = parser.parse_args()

loop = asyncio.get_event_loop()
loop.run_until_complete(main(args.board, args.db_name))
print("EOP")
