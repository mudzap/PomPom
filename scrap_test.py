#import argparse
import asyncio
import sqlite3
import re
from pyppeteer import launch
#import shill_tracker
import time
import requests

async def main():
    url = 'https://boards.4channel.org/biz/catalog'
    browser = await launch(headless=True)
    print(browser)
    page = await browser.newPage()
    print(page)
    await page.goto(url)
    print(url)

    con = sqlite3.connect("test.db")
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        is_op INTEGER,
        has_file INTEGER,
        date INTEGER,
        content TEXT)
    ''')

    threads = await page.JJ('.thread')
    urls = []
    for thread in threads:
        new_url = await thread.JJeval('a[href*="/thread/"]', '(nodes => nodes.map(n => n.href))')
        urls.append(new_url[0])

    for thread_url in urls:
        print(thread_url)
        await page.goto(thread_url)
        
        try:
            op = await page.J('.op')
            op_id = await op.Jeval('.postMessage', '(n => n.id)')
            ret = re.search(r'\d+', op_id)
            if ret:
                op_id = int(ret.group(0))
            op_date = await op.Jeval('.dateTime', '(n => n.getAttribute("data-utc"))')
            op_cont = await op.Jeval('.postMessage', '(n => n.innerText)')
        except:
            print("An exception has ocurred, thread possibly doesn't exist anymore.")
            continue

        cur.execute("INSERT or IGNORE INTO threads VALUES (?, ?, ?, ?, ?, ?)",
                    (op_id, op_id, 1, 1, op_date, op_cont)
        )
        
        replies = await page.JJ('.reply')
        for reply in replies:
            reply_id = await reply.JJeval('.postMessage', '(nodes => nodes.map(n => n.id))')
            ret = re.search(r'\d+', reply_id[0])
            if ret:
                reply_id = int(ret.group(0))
            reply_date = await reply.JJeval('.dateTime', '(nodes => nodes.map(n => n.getAttribute("data-utc")))')
            reply_cont = await reply.JJeval('.postMessage', '(nodes => nodes.map(n => n.innerText))')
            
            has_file = 0

            cur.execute("INSERT or IGNORE INTO threads VALUES (?, ?, ?, ?, ?, ?)",
                    (reply_id, op_id, has_file, 1, reply_date[0], reply_cont[0])
            )

    con.commit()
    con.close()

    await browser.close()
    
asyncio.get_event_loop().run_until_complete(main())

print("EOP")
