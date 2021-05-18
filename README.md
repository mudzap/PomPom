# PomPom

## Description

Set of Python scripts to extract and analyze board data from a certain imageboard using SQLite.

## Insights

I would have liked to scrap data from etherscan.io's API to compare the number of holders with the attention the coin gets, in addition to getting the standard deviation of holders and quantity of coins they have to make a proper analysis, however, these features require me to pay.

Rugpulls targets desperate people most of the time so they don't require large amount of marketing to fool some people, assuming this is true in its entirety, one can guess rugpulls are not predicible by means of just observing how much attention a coin gets.

## Usage

### database

Currently the database must contain a table named 'threads', which must contain itself an unique key column with the post/thread id named 'id', another column named 'date_unix' which contains the date in the POSIX standard, and a column named 'content' with the post/thread content inside.

For compatibility with further improvements, the table must be defined specifically this way:

´´´
(
id INTEGER PRIMARY KEY,
parent_id INTEGER,
has_file INTEGER,
date TEXT,
date_unix INTEGER,
content TEXT
)
´´´

### analyze.py

Shows a graph of how much a coin is mentioned.
Arguments:
- --expr EXPR1 [EXPR2]... : Set of expressions to search for, it follow mostly SQL standard.
  + By using '+', you can specify several expressions to be plotted together. For example: 'btc+bitcoin'.
  + By using '@' you can specify a white space, for example, 'you@and@me' searches for 'you and me'.
  + % and _ work the same as in SQL, %, however, applies to the entirety of the content (It will not work with individual word search).
- --sample: Number of histogram bins
- --norm: Normalize the output by dividing by the total activity, i.e: norm_expr = expr/(sum of all posts)
- --log: Plot the histogram using a logarithmic scale in the y axis.
- --db NAME: Uses the 'name.db' database. Defaults to 'threads.db'

### scrap.py

Scraps a board and stores in a database.
Arguments:
- --board BOARD: Board to scrap, defaults to 'biz'
- --db-name DB_NAME: File to store the database in, defaults to 'threads.db'

## Dependencies

- Python 3.6.9 (because of asyncio, specifically)
- SQLite3
- numpy
- matplotlib

## TODO

- Add date limits.
- Add some additional analysis tools.
- Add a weighted value to posts inside a thread which contains a desired expressión.
