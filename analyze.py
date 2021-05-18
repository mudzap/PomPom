import sqlite3
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter
import datetime


# Parsing rules:
# % -> as expected
# a+b -> a and b results, summed
# a -> '%a%'
# a_b -> aXb
# a@b -> 'a b'
def parse_expr(expr):
    split_str = expr.split('+')
    result = []
    for word in split_str:
        word = word.replace('@', ' ')
        if not(word.endswith('%') or word.startswith('%')): # Hackish word search
            result.append(word + " %")
            result.append("% " + word)
            result.append("% " + word + " %")
        result.append(word)
    return result


parser = argparse.ArgumentParser()
parser.add_argument("--expr", nargs="+")
parser.add_argument("--sample", type=int, default=100)
parser.add_argument("--norm", action='store_true')
parser.add_argument("--log", action='store_true')


args= parser.parse_args()
exprs = args.expr
sample = args.sample
norm = args.norm
use_log_scale = args.log


con = sqlite3.connect("threads.db")
cur = con.cursor()

locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
formatter = mdates.ConciseDateFormatter(locator)
if norm:
    cur.execute("SELECT date_unix FROM threads")
    norm_array = np.array(cur.fetchall(), dtype=np.float)

for expr in exprs:
    new_expr = parse_expr(expr)
    exec_script = 'SELECT date_unix FROM threads WHERE 1=0' #Let's avoid hacks like these
    for _ in new_expr:
        exec_script += ' OR content LIKE ?'
    cur.execute(exec_script, tuple(new_expr))

    date_array = np.array(cur.fetchall(), dtype=np.float)
    date_hist, bins_edges = np.histogram(date_array, bins=sample)

    bins_edges = mdates.epoch2num(bins_edges)
    bins_edges = mdates.num2date(bins_edges)
    
    if norm:
        norm_vec, _ = np.histogram(norm_array, bins=sample, range=(date_array.min(), date_array.max()) )
        norm_date = np.divide(date_hist, norm_vec)
        plt.plot_date(bins_edges[:-1], norm_date, '-', label=expr)
    else:
        plt.plot_date(bins_edges[:-1], date_hist, '-', label=expr)    
    
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)
if use_log_scale:
    plt.yscale('log')
if norm:
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.legend()
plt.show()
