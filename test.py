#!/usr/bin/python
import os
import sys
from ir_webstats_rc.client import iRWebStats
import dotenv
dotenv.load_dotenv()

irw = iRWebStats()
irw.login(os.getenv("IRACING_USERNAME"), os.getenv("IRACING_PASSWORD"))

print(irw.lastrace_stats("499343"))
