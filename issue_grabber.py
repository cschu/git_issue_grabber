import sys
import requests
import os
from pprint import pprint
import json
import argparse

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("token", str)
	ap.add_argument("service", choices=("github", "gitlab"), default="github")
	ap.add_argument("owner", type=str)
	ap.add_argument("repo", type=str)
	args = ap.parse_args()

# (base) cschu@MacBook-Pro ~ % curl --header "PRIVATE-TOKEN: <token>" "https://gitlab.com/api/v4/projects/ezlab%2Fbusco/issues?per_page=1&page=0"


owner = "saezlab"
repo = "pypath"

query_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
#params = {
#    "state": "all",
#	"per_page": "100",
#	#"page": "3"
#}
# (base) cschu@MacBook-Pro ~ % curl "https://api.github.com/repos/saezlab/pypath/issues?page=0&per_page=1" | less
params = {
	"page": "0",
	"per_page": "1",
	"state": "all"
}
headers = {'Authorization': f'token {token}'}
r = requests.get(query_url, headers=headers, params=params)
#print(len(r.json()))

#issues = json.loads(r.json())
#print(len(issues))
 
#pprint(r.json())

total = int(r.json()[0]["number"])
print(total)

params["per_page"] = "100"
params["page"] = "1"
#r = requests.get(query_url, headers=headers, params=params)
#pprint(r.json())
#sys.exit()

all_issues = list()
while len(all_issues) < total:
	r = requests.get(query_url, headers=headers, params=params)
	# pprint(r.json())
	all_issues.extend(r.json())
	print(len(all_issues))
	params["page"] = str(int(params["page"]) + 1)


from collections import Counter
closed_c, created_c = Counter(), Counter()
for item in all_issues:
	#pprint(item)
	created_month = item.get("created_at", "")
	closed_month = item.get("closed_at", "")
	if closed_month:
		closed_c[tuple(closed_month.split("-")[:2])] += 1
	created_c[tuple(created_month.split("-")[:2])] += 1

for month in sorted(set(created_c).union(closed_c)):
	print("-".join(month), created_c[month], closed_c[month], sep="\t")


#print(*created_c.items(), sep="\n")
#print(*closed_c.items(), sep="\n")




	

