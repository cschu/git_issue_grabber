import sys
import requests
import os
from pprint import pprint
import json
import argparse
from collections import Counter

class GitAccess:
	@classmethod
	def send_request(cls, owner, repo, token, **params):
		params[cls.ALL_PARAM[0]] = cls.ALL_PARAM[1]
		# print(params)
		headers = {cls.HEADERS[0]: cls.HEADERS[1].format(token=token)}
		
		return requests.get(cls.QUERY_URL.format(owner=owner, repo=repo), 
							headers={cls.HEADERS[0]: cls.HEADERS[1].format(token=token)},
							params=params).json()

class GitHubAccess(GitAccess):
	QUERY_URL = "https://api.github.com/repos/{owner}/{repo}/issues"
	ALL_PARAM = ("state", "all")
	HEADERS = ('Authorization', 'token {token}')
	TICKET_NUMBER = "number"

class GitLabAccess(GitAccess):
	# (base) cschu@MacBook-Pro ~ % curl --header "PRIVATE-TOKEN: <token>" "https://gitlab.com/api/v4/projects/ezlab%2Fbusco/issues?per_page=1&page=0"
	QUERY_URL = "https://gitlab.com/api/v4/projects/{owner}%2F{repo}/issues"
	ALL_PARAM = ("scope", "all")
	HEADERS = ("PRIVATE-TOKEN", "{token}")
	TICKET_NUMBER = "iid"
	



def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("token", type=str)
	ap.add_argument("service", choices=("github", "gitlab"), default="github")
	ap.add_argument("owner", type=str)
	ap.add_argument("repo", type=str)
	args = ap.parse_args()

	git = GitHubAccess if args.service == "github" else GitLabAccess

	reply = git.send_request(args.owner, args.repo, args.token, page="0", per_page="1")
	total_issues = reply[0][git.TICKET_NUMBER] if reply else 0
	# print(reply)
	# print(total_issues)

	all_issues = list()
	old_len = 0
	page = 1
	while len(all_issues) < total_issues:
		reply = git.send_request(args.owner, args.repo, args.token, page=str(page), per_page=100)
		all_issues.extend(reply)
		# print(len(all_issues))
		if old_len == len(all_issues):
			break
		old_len = len(all_issues)
		page += 1


	# print(all_issues)
	closed_c, created_c = Counter(), Counter()
	for item in all_issues:
		if item.get("pull_request"):
			continue
		created_month = item.get("created_at", "")
		closed_month = item.get("closed_at", "")
		if closed_month:
			closed_c[tuple(closed_month.split("-")[:2])] += 1
		created_c[tuple(created_month.split("-")[:2])] += 1

	last_year, last_month = None, None
	for year, month in sorted(set(created_c).union(closed_c)):
		if last_month:
			current_year, current_month = map(int, (year, month))
			while True:
				if last_month == 12:
					last_year, last_month = last_year + 1, 1
				else:
					last_month += 1
				if (last_year, last_month) == (current_year, current_month):
					break

				print("{year}-{month:02d}".format(year=last_year, month=last_month), 0, 0, sep="\t")

		print("-".join((year, month)), created_c[(year, month)], closed_c[(year, month)], sep="\t")
		last_year, last_month = map(int, (year, month))
	


if __name__ == "__main__":
	main()
