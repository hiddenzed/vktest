
from tabletext import to_text
from pathlib import Path
from threading import Thread

import requests
import json
import random
import time
import os

from config import bcolors, info, files, js

from vkapi import avatarPost, privacySet, logIn, stickersGet, albumsGet, photosDelete


def bdate_gen():
	bdate = '{}.{}.{}'.format(random.randint(1, 28), random.randint(1, 12),
		random.randint(1990, 1999))

	return bdate


def pro(proxy):
	proxies = {
		'http': 'http://{}'.format(proxy),
		'https': 'https://{}'.format(proxy)
	}

	return proxies


def geturl(method, params, token):
	api_v = '5.80'

	url = 'https://api.vk.com/method/{}?'.format(method)

	for param in params:
		url += '{}={}&'.format(param, params[param])

	url += 'access_token={}&v={}'.format(token, api_v)

	return url


def ls(allgroups='none', onlynames=0):
	def ls_t(num, account):
		i = num + 1
		uid = account['id']
		name = account['name']
		token = account['access_token']

		proxies = pro(account['proxy'])

		if 'error' in requests.get(geturl('wall.get', {'count': 1}, token), proxies=proxies).json():
			status = 'ban'

		else:
			status = 'active'

		temp_an.update({num:[i, name, uid, status]})


	fullstat = '\n'

	if allgroups == 'none':
		allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))


	if onlynames == 0:
		for one in allgroups:
			fullstat += '\n' + bcolors.OKGREEN + to_text([[one, allgroups[one]['note'],
				allgroups[one]['created'], len(allgroups[one]['accounts'])]]) + bcolors.ENDC

			fullstat += '\n'

			temp_an = {}
			accounts = allgroups[one]['accounts']

			for num, account in enumerate(accounts, 0):
				Thread(target=ls_t, args=(num, account)).start()

			while len(temp_an) != len(accounts):
				pass

			stat = []
			stat.append(['#', 'name', 'id', 'status'])

			for i in range(len(accounts)):
				stat.append(temp_an[i])

			fullstat += to_text(stat)

	else:
		stat = []
		stat.append(['name', 'note', 'created', 'accounts count'])

		for one in allgroups:
			stat.append([one, allgroups[one]['note'], allgroups[one]['created'],
				len(allgroups[one]['accounts'])])

		fullstat = to_text(stat)


	return fullstat


def la():
	def laa(n, groupname, account):
		uid = account['id']
		name = account['name']

		proxies = pro(account['proxy'])
		token = account['access_token']

		with open(js.la) as file:
			script = file.read()

		response = requests.get(geturl('execute', {'code': script}, token),
			proxies=proxies).json()

		if 'error' in response:
			status = 'banned'
			groups = '-'
			admin_groups = '-'
			views = '-'
			friends = '-'
			followers = '-'
			requests_count = '-'

		else:
			response = response['response']

			status = 'active'
			views = response['views']
			groups = response['groups']
			admin_groups = response['admin_groups']

			friends = response['friends']
			followers = response['followers']
			requests_count = response['requests']

		stat = [n, name, uid, status, views, groups, admin_groups, friends, followers, requests_count]
		temp_an[groupname].update({str(n): stat})

	allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

	al = {}
	temp_an = {}

	for one in allgroups:
		temp_an.update({one:{}})
		accounts = allgroups[one]['accounts']

		onegroup = {
			'title': [allgroups[one]['name'], allgroups[one]['note'], allgroups[one]['created'], len(allgroups[one]['accounts'])],
			'accounts': [],
			'accountsCount': len(accounts),
			'viewsCount': ''
		}

		al.update({one:onegroup})

		for n, account in enumerate (accounts, 1):
			Thread (target=laa, args=(n, one, account)).start ()

	dead = False
	while not dead:
		ready_accounts = 0
		all_accounts_count = 0

		for one in temp_an:
			ready_accounts += len(temp_an[one])

		for one in allgroups:
			all_accounts_count += len(allgroups[one]['accounts'])

		if ready_accounts == all_accounts_count:
			dead = True

	for one in temp_an:
		viewsCount = 0
		for i in range(len(temp_an[one])):
			i += 1
			al[one]['accounts'].append(temp_an[one][str(i)])

			if temp_an[one][str(i)][4] == '-':
				print('bleat')

			elif str(temp_an[one][str(i)][4]).isdigit() == False:
				print('bleat bleat bleat')
				temp_an[one][str(i)][4] = '-'

			else:
				viewsCount += int(temp_an[one][str(i)][4])

		al[one]['viewsCount'] = viewsCount


	stat = ''
	for one in al:
		title = ['#', 'name', 'id', 'status', 'views', 'pubs', 'admin', 'friends', 'in', 'out']
		temp_dt = []
		temp_dt.append(title)

		for item in al[one]['accounts']:
			temp_dt.append(item)

		groupinfo = []

		for item in al[one]['title']:
			groupinfo.append(item)

		groupinfo.append('total views: {}'.format(al[one]['viewsCount']))


		stat += bcolors.OKGREEN + to_text([groupinfo]) + bcolors.ENDC + '\n'
		stat += to_text(temp_dt) + '\n'

	return stat


def create_tasks():
	def onetask(one):
		if one == 'nc':
			return ['nc']

		elif one == 'gc':
			file = input('input path to groups comment\n↪ ')
			return ['gc', file]

		elif one == 'vc':
			q = input('query to comment videos\n↪ ')
			return ['vc', q]

		elif one == 'vu':
			q = input('query to video upload\n↪ ')
			return ['vu', q]

		elif one == 'fs':
			return ['fs']

		elif one == 'ff':
			file = input('path to follow from file\n↪ ')
			return ['ff', file]

		elif one == 'fl':
			return ['fl']

		elif one == 'cr':
			return ['cr']

		elif one == 'jf':
			file = input('path to file with groups to join\n↪ ')
			return ['jf', file]

		elif one == 'js':
			q = input('query to search groups to join\n↪ ')
			return ['js', q]

		elif one == 'pp':
			file = input('path to file with settings to post\n↪ ')
			return ['pp', file]

		else:
			print(bcolors.FAIL + 'command unknown {}'.format(one) + bcolors.ENDC)
			return []


	newtask = {'t':[], 'sleeptime':[]}

	print('nc,gc,vc,vu,fs,ff,fl,cr,jf,js')
	d = input('do you want to see help page? (y/N)\n↪ ')

	if d == 'y':
		hpage = []
		hpage.append(['sc', 'comment'])

		hpage.append(['nc', 'newsfeed comment'])
		hpage.append(['gc', 'groups from file comment'])
		hpage.append(['vc', 'videos comment'])

		hpage.append(['vu', 'video upload'])

		hpage.append(['fs', 'follow suggested'])
		hpage.append(['ff', 'follow from file'])
		hpage.append(['fl', 'follow from likes'])

		hpage.append(['cr', 'confirm incoming requests'])

		hpage.append(['jf', 'join group from file'])
		hpage.append(['js', 'join from search'])

		print(to_text(hpage))

	d = input('input with space (ex: nc gc)\n↪ ').split(' ')

	for one in d:
		newtask['t'].append(onetask(one))

	sleeptime = input('input sleeptime (2 nums, ex: 100 200)\n↪ ').split(' ')

	for sec in sleeptime:
		newtask['sleeptime'].append(int(sec))

	return newtask


def group_actions(accounts):
	print('gl ic pd ap ps sg wd wd1 rp rd')
	d = input('do you want to see help page? (y/N)\n↪ ')

	if d == 'y':
		hpage = []
		hpage.append(['sc', 'comment'])

		hpage.append(['ic', 'change account info'])
		hpage.append(['ap', 'post an avatar'])
		hpage.append(['rp', 'repost'])
		hpage.append(['ps', 'set privacy settings'])
		hpage.append(['sg', 'get sticker packs'])
		hpage.append(['wd', 'delete wall posts (all)'])
		hpage.append(['wd1', 'delete last post'])
		hpage.append(['pd', 'delete all photos'])
		hpage.append(['gl', 'leave all groups'])
		hpage.append(['rd', 'delete outcoming requests'])

		print(to_text(hpage))

	d = input('input actions (or all)\n↪ ').split(' ')
		

	if d[0] == 'all':
		d = 'gl ic pd ap ps sg wd rp rd'.split(' ')


	for one in d:
		if one == 'ic':
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				params = {
					'relation': 0,
					'bdate_visibility': 2,
					'bdate': bdate_gen(),
					'home_town': '',
					'country_id': 0,
					'city_id': 0,
					'status': ''}

				print(requests.get(geturl('account.saveProfileInfo', params, token),
					proxies=proxies).json())


		elif one == 'ap':
			for account in accounts:
				myid = account['id']
				token = account['access_token']
				proxies = pro(account['proxy'])

				path_to_photo = account['avadir'] + random.choice(os.listdir(account['avadir']))

				resp = avatarPost(token, proxies, path_to_photo)
				if resp == 'ok':
					print(f'{myid} - avatar posted')

				else:
					print(f'{myid} - avapost - {str(resp)}')


		elif one == 'rp':
			posts = input('posts in format wall-1_234 (one or many with space)\n↪ ').split(' ')

			for post in posts:
				for account in accounts:
					token = account['access_token']
					proxies = pro(account['proxy'])

					resp = requests.get(geturl('wall.repost', {'object': post}, token),
						proxies=proxies).json()


					if 'response' in resp:
						print('done: + one repost - ' + bcolors.OKBLUE + account['name'] + bcolors.ENDC)

					else:
						print(resp)

					time.sleep (0.04)

				time.sleep(1)


		elif one == 'ps':
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				print('account - {}'.format(account['id']))

				keys = ['mail_send', 'status_replies', 'groups', 'wall_send']
				privacySet(token, proxies, keys)


		elif one == 'sg':
			for account in accounts:
				proxies = pro(account['proxy'])
				login = account['login']
				paswd = account['pass']
				
				headers = {
					"User-Agent": account['ua'],
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					"Accept-Language": "ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3",
					"Accept-Encoding": "gzip, deflate",
					"Connection": "keep-alive",
					"DNT": "1"}

				print('account - {}'.format(account['id']))

				s = logIn(login, paswd, proxies, headers)
				stickersGet(s, proxies, headers)


		elif one == 'wd':
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				print('account - {}'.format(account['id']))

				count = requests.get(geturl('wall.get', {'count': 100}, token),
					proxies=proxies).json()['response']['count']

				for i in range(count // 100 + 1):
					resp = requests.get(geturl('wall.get', {'count': 100, 'offset': i * 100}, token),
						proxies=proxies).json()['response']['items']

					for wall in resp:
						try:
							response = requests.get(geturl('wall.delete', {'post_id': wall['id']}, token),
								proxies=proxies).json()

							print(f'wall delete - {response}')

							time.sleep(0.3)

						except Exception as e:
							print(e)


		elif one == 'wd1':
			count = int(input('input count of posts to delete\n↪ '))
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				print('account - {}'.format(account['id']))

				resp = requests.get(geturl('wall.get', {'count': count}, token),
					proxies=proxies).json()['response']['items']

				for wall in resp:
					try:
						response = requests.get(geturl('wall.delete', {'post_id': wall['id']}, token),
							proxies=proxies).json()

						print(f'wall delete - {response}')

					except Exception as e:
						print(e)


		elif one == 'pd':
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				albums = albumsGet(token, proxies)

				for album in albums:
					time.sleep(0.05)
					resp = photosDelete(token, proxies, album['id'], 'all')

					for i in resp:
						print(i)


		elif one == 'gl':
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				resp = requests.get(geturl('groups.get', {'count': 1000}, token),
					proxies=proxies).json()['response']

				print('account {} - leaving groups'.format(account['id']))
				print('groups count {}'.format(resp['count']))

				for gid in resp['items']:
					print(requests.get(geturl('groups.leave', {'group_id': gid}, token),
						proxies=proxies).json())
					
					time.sleep(0.3)


		elif one == 'rd':
			for account in accounts:
				token = account['access_token']
				proxies = pro(account['proxy'])

				requests_count = requests.get(geturl('friends.getRequests', {'out': 1}, token),
					proxies=proxies).json()['response']['count']

				print('account {} - deleting outcoming requests'.format(account['id']))
				print(requests_count)

				for i in range(requests_count // 100 + 1):
					uids = requests.get(geturl('friends.getRequests', {'out': 1, 'count': 100}, token),
						proxies=proxies).json()['response']['items']

					for user in uids:
						print(requests.get(geturl('friends.delete', {'user_id': user}, token),
							proxies=proxies).json())

						time.sleep(0.3)


		else:
			print(f'command {one} unknown')

		time.sleep(0.3)


def showlog():
	def slog():
		log = []
		global bleatb

		while getattr(t, "do_run", True):
			with open(files.log) as file:
				log_full = file.read().splitlines()

				log_full = log_full[-50:]
				log = log[-50:]

				if log != log_full:
					print_log = log_full[len(log):]

					for one in log_full:
						print(one)

					print(bcolors.OKGREEN + '\n\npress enter to leave' + bcolors.ENDC)

					log = log_full

				time.sleep(1)

	os.system('clear')
	t = Thread(target=slog)
	t.start()
	input()
	t.do_run = False


def bancheck():
	def check(n, groupname, account):
		uid = account['id']
		name = account['name']

		proxies = pro(account['proxy'])
		token = account['access_token']

		if 'error' in requests.get(geturl('wall.get', {'count': 1}, token), proxies=proxies).json():
			status = '-'
			temp_an[groupname]['banned'].append(account)

		else:
			status = '+'
			temp_an[groupname]['active'].append(account)

	allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

	temp_an = {}
	oldbanned = json.loads(Path(files.banned).read_text(encoding='utf-8'))
	banned = []

	for group in allgroups:
		accounts = allgroups[group]['accounts']
		temp_an.update({group:{'banned':[], 'active': []}})

		for n, account in enumerate (accounts, 1):
			Thread (target=check, args=(n, group, account)).start ()

	dead = False
	while not dead:
		ready_accounts = 0
		all_accounts_count = 0

		for one in temp_an:
			for o in temp_an[one]:
				ready_accounts += len(temp_an[one][o])

		for one in allgroups:
			all_accounts_count += len(allgroups[one]['accounts'])

		if ready_accounts == all_accounts_count:
			dead = True

	for group in temp_an:
		for account in temp_an[group]['banned']:
			banned.append(account)
			del(allgroups[group]['accounts'][allgroups[group]['accounts'].index(account)])


	with open(files.groups, 'w') as file:
		json.dump(allgroups, file, indent=2, ensure_ascii=False)

	oldbanned += banned

	with open(files.banned, 'w') as file:
		json.dump(oldbanned, file, indent=2, ensure_ascii=False)


	print('banned accounts - {}'.format(len(banned)))


def proxycheck(proxy):
	proxies = pro(proxy)

	try:
		requests.get('https://api.vk.com/', proxies=proxies, timeout=5)
		return 1

	except:
		return 0

