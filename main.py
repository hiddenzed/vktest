
from lib import geturl, ls, la, pro, create_tasks
from lib import proxycheck, group_actions, showlog, bancheck
from config import bcolors, info, files, bases, infiles

from pathlib import Path
from threading import Thread
from datetime import datetime
from tabletext import to_text

import os
import time
import json
import random
import logging
import requests

import vkapi

logging.basicConfig(filename=files.log, level=logging.INFO)

with open(bases.comments) as file:
	comments = file.read().splitlines() 



# add
# groups
# start

threads = {}


def addtask(mythreads):
	threads.update(mythreads)


def log(uid, task, comment):
	logging.info(f'{uid} {task} {comment}')



##################################
############# adding #############
##################################
def addproxies():
	count = input('how many accounts do you want to use on one proxy? (default - 2)\n↪ ')

	try:
		count = int(count)

	except:
		count = 2

	newproxies = []
	badproxies = []
	with open(infiles.proxies, 'r') as file:
		for line in file:
			if len(line) != 0:
				if '@' not in line:
					oneproxy = '{}:{}@{}:{}'.format(line.strip().split(':')[2],
						line.strip().split(':')[3],	line.strip().split(':')[0], line.strip().split(':')[1])

				else:
					oneproxy = line.strip ()

				if proxycheck(oneproxy) == 1:
					for one in range(count):
						newproxies.append(oneproxy)

				else:
					print('error proxy')
					badproxies.append(oneproxy)

	if len(newproxies) != 0:
		with open(bases.proxies, 'a') as file:
			for proxy in newproxies:
				file.write(proxy + '\n')

	else:
		print('no new proxies')

	if len(badproxies) != 0:
		with open(bases.badproxies, 'a') as file:
			for proxy in badproxies:
				file.write(proxy + '\n')

	with open(infiles.proxies, 'w') as file:
		pass

	return f'added {len(newproxies)} proxies, {len(badproxies)} are invalid'

def addaccounts():
	newaccounts = []

	with open(infiles.accounts) as file:
		naccs = file.read().splitlines()

	for one in naccs:
		login = one.split(':')[0]
		paswd = one.split(':')[1]

		myheaders = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Language": "ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Encoding": "gzip, deflate",
			"Connection": "keep-alive",
			"DNT": "1"}

		with open(bases.uas) as file:
			uas = file.read().splitlines()

		ua = random.choice(uas)
		myheaders.update({'User-Agent': ua})

		with open(bases.proxies) as file:
			allproxies = file.read().splitlines()

		proxy = allproxies[0]
		proxies = pro(proxy)

		with open(bases.proxies, 'w') as file:
			for oneproxy in allproxies[1:]:
				file.write(oneproxy + '\n')

		s = requests.session()
		access_token = vkapi.get_access_token(s, login, paswd, proxies, myheaders)

		if 'blocked' in access_token:
			print('error: account in banned')
			with open(bases.badaccounts, 'a') as file:
				file.write(one + '\n')

		elif 'vk.com' in access_token:
			print('error: can\'t get token')

			with open(bases.badaccounts, 'a') as file:
				file.write(one + '\n')

		else:
			print('access token recieved')
			time.sleep(1)
			kate_token = vkapi.get_access_token(s, login, paswd, proxies, myheaders, client_id='2685278', log_in=0)

			temp_dt = requests.get(geturl('users.get', {'fields': 'sex'}, kate_token), proxies=proxies).json()
			
			try:
				temp_dt = temp_dt['response'][0]

			except:
				print(temp_dt)
				print(kate_token)

			uid = temp_dt['id']
			name = temp_dt['first_name']

			user_avatars_path = bases.avadirs + random.choice(os.listdir(bases.avadirs)) + '/'

			if temp_dt['sex'] == 1:
				sex = 'female'

			else:
				sex = 'male'

			account = {'id': uid, 'name': name, 'sex': sex, 'login': login,
				'pass': paswd, 'ua': ua, 'proxy': proxy, 'avadir': user_avatars_path,
				'access_token': access_token, 'kate_token': kate_token}

			allaccounts = json.loads(Path(files.awg).read_text(encoding='utf-8'))

			allaccounts.append(account)

			with open(files.awg, 'w') as file:
				json.dump(allaccounts, file, indent=2, ensure_ascii=False)


	with open(infiles.accounts, 'w') as file:
		pass
##################################



def groups():
	print(info.groups)
	while True:
		d = input(bcolors.OKBLUE + 'main/groups' + bcolors.ENDC + '\n↪ ')

		if d == '1':
			name = input('name for group\n↪ ')
			note = input('note for group\n↪ ')

			allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

			if name in allgroups.keys():
				print(bcolors.FAIL + 'group name already exist' + bcolors.ENDC)

			else:
				created = str(datetime.now()).split('.')[0]

				d = input('do you want to set tasks? (y/n)\n↪ ')

				if d == 'y':
					result = create_tasks()

					t = result['t']
					sleeptime = result['sleeptime']

				else:
					t = []
					sleeptime = []


				group = {
					'name': name,
					'created': created,
					'note': note,
					'accounts': [],
					'tasks': {
						't': t,
						'sleeptime': sleeptime
					}
				}

				allgroups.update({name:group})

				with open(files.groups, 'w') as file:
					json.dump(allgroups, file, indent=2, ensure_ascii=False)

		elif d == '2':
			allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

			mygroups = []
			mygroups.append(['#', 'name', 'note', 'accounts'])

			for num, groupname in enumerate(allgroups, 1):
				mygroups.append([num, groupname, allgroups[groupname]['note'],
					len(allgroups[groupname]['accounts'])])

			print(to_text(mygroups))

			groupname = input('name of group to edit\n↪ ')

			if groupname not in allgroups.keys():
				print(bcolors.FAIL + 'groups with this name does not exist' + bcolors.ENDC)

			else:
				print(info.group_edit)
				d = input(bcolors.OKBLUE + 'main/groups/edit group' + bcolors.ENDC + '\n↪ ')

				if d == '1':
					group = allgroups[groupname]

					newname = input('new name for group (n to use old name)\n↪ ')

					if newname != 'n':
						name = newname

					else:
						name = groupname

					newnote = input('new note for group (n to use old note)\n↪ ')

					if newnote != 'n':
						note = newnote

					else:
						note = allgroups[groupname]['note']

					group_edited = {
						'name': name,
						'created': group['created'],
						'note': note,
						'accounts': group['accounts'],
						'tasks': group['tasks']
					}

					del(allgroups[groupname])
					allgroups.update({name:group_edited})

					with open(files.groups, 'w') as file:
						json.dump(allgroups, file, indent=2, ensure_ascii=False)

				elif d == '2':
					print(bcolors.FAIL + 'note ready yet' + bcolors.ENDC)

					tasks = []
					tasks.append(['action', 'param'])
					for one in allgroups[groupname]['tasks']['t']:
						tasks.append(one)

					print(to_text(tasks))

					d = input('are you sure that you want to delete all tasks and recreate them? (y/n)\n↪ ')

					if d == 'y':
						result = create_tasks()

						t = result['t']
						sleeptime = result['sleeptime']

						allgroups[groupname]['tasks']['t'] = t
						allgroups[groupname]['tasks']['sleeptime'] = sleeptime


						with open(files.groups, 'w') as file:
							json.dump(allgroups, file, indent=2, ensure_ascii=False)
						

					else:
						return

				elif d == '3':
					d = input('(1) add accounts\n(2) delete accounts\n↪ ')

					if d == '1':
						awg = json.loads(Path(files.awg).read_text(encoding='utf-8'))

						lsallgroups = {
							'accounts without groups':
								{
									'name': 'accounts without groups',
									'created': '',
									'note': '',
									'accounts': awg}}

						print(ls(allgroups=lsallgroups))

						d = input('nums of accounts to add\n↪ ').split(' ')

						accounts = []

						for o in d:
							accounts.append(awg[int(o) - 1])

						for o in accounts:
							del(awg[awg.index(o)])
							time.sleep(0.02)


						allgroups[groupname]['accounts'] += accounts

						with open(files.groups, 'w') as file:
							json.dump(allgroups, file, indent=2, ensure_ascii=False)

						with open(files.awg, 'w') as file:
							json.dump(awg, file, indent=2, ensure_ascii=False)

					elif d == '2':
						print(ls(allgroups={groupname:allgroups[groupname]}))

						d = input('nums of accounts to delete\n↪ ').split(' ')

						accounts = []
						newawg = []

						for i in range(len(allgroups[groupname]['accounts'])):
							if str(i + 1) not in d:
								accounts.append(allgroups[groupname]['accounts'][i])

							else:
								newawg.append(allgroups[groupname]['accounts'][i])

						allgroups[groupname]['accounts'] = accounts

						awg = json.loads(Path(files.awg).read_text(encoding='utf-8'))
						awg += newawg


						with open(files.groups, 'w') as file:
							json.dump(allgroups, file, indent=2, ensure_ascii=False)

						with open(files.awg, 'w') as file:
							json.dump(awg, file, indent=2, ensure_ascii=False)

		elif d == '3':
			allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

			mygroups = []
			mygroups.append(['#', 'name', 'note', 'accounts'])

			for num, groupname in enumerate(allgroups, 1):
				mygroups.append([num, groupname, allgroups[groupname]['note'],
					len(allgroups[groupname]['accounts'])])

			print(to_text(mygroups))

			groupname = input('name of group to edit\n↪ ')

			if groupname not in allgroups.keys():
				print(bcolors.FAIL + 'groups with this name does not exist' + bcolors.ENDC)

			else:
				group_actions(allgroups[groupname]['accounts'])

		elif d == '4':
			print(ls())
			allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

			groupname_0 = input('1 group name\n↪ ')

			if groupname_0 not in allgroups:
				print(bcolors.FAIL + 'this group does not exist' + bcolors.ENDC)
				return

			groupname_1 = input('2 group name (will be destroyed)\n↪ ')

			if groupname_1 not in allgroups:
				print(bcolors.FAIL + 'this group does not exist' + bcolors.ENDC)
				return

			allgroups[groupname_0]['accounts'] += allgroups[groupname_1]['accounts']
			del(allgroups[groupname_1])

			with open(files.groups, 'w') as file:
				json.dump(allgroups, file, indent=2, ensure_ascii=False)

		elif d == '5':
			allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))
			d = input('(1) delete all empty groups\n(2) choose and delete group\n↪ ')

			if d == '1':
				badgroups = []

				for one in allgroups:
					if len(allgroups[one]['accounts']) == 0:
						badgroups.append(one)

				for groupname in badgroups:
					del(allgroups[groupname])

			else:
				print(ls())
				groupname = input('group name\n↪ ')

				if len(allgroups[groupname]['accounts']) != 0:
					awg = json.loads(Path(files.awg).read_text(encoding='utf-8'))
					awg += allgroups[groupname]['accounts']

				del(allgroups[groupname])

				with open(files.awg, 'w') as file:
					json.dump(awg, file, indent=2, ensure_ascii=False)


			with open(files.groups, 'w') as file:
				json.dump(allgroups, file, indent=2, ensure_ascii=False)

		elif d == 'clear':
			os.system('clear')

		elif d == 'cd':
			return

		elif d == 'h' or d == 'help':
			print(info.groups)


################################
def restart():
	# names = threads.keys()
	names = []

	for name in threads:
		names.append(name)
		
	kill(names=names)
	bancheck()
	time.sleep(1)
	start(names=names)
	log('restart', 'restart', 'restart')





#######################################
def start(names='n'):
	if names == 'n':
		while True:
			print(ls(onlynames=1))
			d = input(bcolors.OKBLUE + 'main/start' + bcolors.ENDC + '\n↪ ')


			if d == 'la':
				print(la())

			elif d == 'ls':
				print(ls())

			elif d == 'lc':
				print(ls(onlynames=1))

			elif d == 'cd':
				return

			elif d == 'all':
				mygroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

				gogo(mygroups)
				return

			else:
				d = d.split(' ')

				allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

				mygroups = {}

				for one in d:
					try:
						mygroups.update({one:allgroups[one]})

					except:
						print(bcolors.FAIL + f'sorry, group {one} does not exist' + bcolors.ENDC)


					if len(mygroups) != 0:
						gogo(mygroups)

					else:
						print(bcolors.FAIL + 'sorry, you did not choose any group')

					return

	else:
		# d = names.split(' ')
		d = names

		allgroups = json.loads(Path(files.groups).read_text(encoding='utf-8'))

		mygroups = {}

		for one in d:
			try:
				mygroups.update({one:allgroups[one]})

			except:
				print(bcolors.FAIL + f'sorry, group {one} does not exist' + bcolors.ENDC)


			if len(mygroups) != 0:
				gogo(mygroups)

			else:
				print(bcolors.FAIL + 'sorry, you did not choose any group')

			return


def gogo(mygroups):
	for groupname in mygroups:
		group = mygroups[groupname]
		accounts = group['accounts']

		mythreads = {groupname:{}}

		tasklist = group['tasks']

		for account in accounts:
			uid = account['id']

			t = Thread(target=goonetask, args=(account, tasklist, groupname))
			t.start()

			mythreads[groupname].update({uid:[t, account]})

		addtask(mythreads)


def goonetask(account, tasklist, groupname):
	def commit_requests(token, myid, proxies):
		def sl (sec):
			for i in range (sec):
				if getattr (tcr, 'do_run', True):
					time.sleep (1)

		response = requests.get(geturl('friends.getRequests', {'need_viewed': 1}, token),
			proxies=proxies).json()

		try:
			response = response['response']['items']

			for item in response:
				resp = vkapi.userAdd (token, proxies, item, myid)

				if resp == 'captcha':
					log(myid, 'accepting new requests', 'captcha')

				elif resp == 'not found':
					log(myid, 'accepting new requests', 'user not found')

				elif resp == 'unknown error':
					log(myid, 'accepting new requests', 'unknown error or limit reached')

				elif resp == 'ok':
					log(myid, 'accepting new requests', 'user added')

				else:
					log(myid, 'accepting new requests', str (resp))

				sl(1)

		except Exception as e:
			log(myid, 'accepting new requests', 'total error - {}'.format(e))

			print('commit requests error')
			print(e)


		while getattr (tcr, 'do_run', True):
			try:
				response = requests.get(geturl('friends.getRequests', {}, token),
					proxies=proxies).json()

				try:
					response = response['response']['items']

				except:
					print(f'error {response}')

				for item in response:
					try:
						resp = vkapi.userAdd(token, proxies, item, myid)

						if resp == 'captcha':
							log(myid, 'accepting new requests', 'captcha')

						elif resp == 'not found':
							log(myid, 'accepting new requests', 'user not found')

						elif resp == 'unknown error':
							log(myid, 'accepting new requests', 'unknown error or limit reached')

						elif resp == 'ok':
							log(myid, 'accepting new requests', 'user added')

						else:
							log(myid, 'accepting new requests', str (resp))

						sl(1)

					except:
						log(myid, 'accepting new requests', 'total error')

				sl(random.randint (30, 80))


			except ConnectionResetError:
				print(bcolors.FAIL + 'ConnectionResetError' + bcolors.ENDC)

			except ConnectionError:
				print(bcolors.FAIL + 'ConnectionError' + bcolors.ENDC)

			except Exception as e:
				print(e)
				print(type(e))
				with open('critical_errors.txt', 'a') as file:
					file.write(str(type(e)) + '\n')

				sl(10)

	def kill_this_task(t):
		pass


	time.sleep(0.4)

	t = threads[groupname][account['id']][0]

	tasks = tasklist['t']

	st0 = tasklist['sleeptime'][0]
	st1 = tasklist['sleeptime'][1]

	token = account['access_token']
	kate_token = account['kate_token']
	proxies = pro(account['proxy'])

	myid = account['id']

	if ['nc'] in tasks:
		feed_posts = vkapi.feedGet(token, proxies)
		feed_time = requests.get(geturl('utils.getServerTime', {}, token),
			proxies=proxies).json()['response']

		feed = {'posts': feed_posts, 'start_time': feed_time}

	for onetask in tasks:
		if onetask[0] == 'jf':
			with open(onetask[1]) as file:
				grouplist = file.read().splitlines()


	if ['cr'] in tasks:
		tcr = Thread(target=commit_requests, args=(token, myid, proxies))
		tcr.start()

	if len(tasks) != 0:
		while getattr(t, 'do_run', True):
			d = random.choice(tasks)

			if d[0] != 'cr':
				try:
					if d[0] == 'nc':
						try:
							feed_posts = vkapi.feedGet(token, proxies, start_time=feed['start_time'])
							feed_time = requests.get(geturl('utils.getServerTime', {}, token),
								proxies=proxies).json()['response']

							if 'error' in feed_posts:
								log(myid, 'feed commenting', 'can not get feed - {}'.format(feed_posts))

							else:
								for item in feed_posts:
									if '-' in str(item['source_id']) and item['comments']['can_post'] == 1:
										feed['posts'].append(item)
								
								feed['start_time'] = feed_time


							wall = random.choice(feed['posts'])
							del(feed['posts'][feed['posts'].index(wall)])

							owner_id = wall['source_id']
							post_id = wall['post_id']

							message = random.choice(bases.comments)
							response = vkapi.wallComment(token, proxies, owner_id, post_id, message)

							if response == 'captcha':
								log(myid, 'feed commenting', 'captcha')

							elif response == 'banned in group':
								log(myid, 'feed commenting', 'comments closed or account banned in group, leaving')

							elif response == 'internal server error':
								log(myid, 'feed commenting', 'internal server error')

							elif 'ok' in response:
								cid = response.split(' ')[1]
								log(myid, 'feed commenting', f'comments posted, cid {cid}')

							else:
								log(myid, 'feed commenting', str(response))


						except Exception as e:
							print(type(e))
							print(e)
							log(myid, 'feed commenting', 'total error')

					elif d[0] == 'gc':
						with open(d[1]) as file:
							owner_id = '-' + str(random.choice(file.read().splitlines()))

						response = requests.get(geturl('wall.get', {'owner_id': owner_id,
							'filter': 'owner', 'count': 2}, token), proxies=proxies).json()


						if 'error' in response:
							print(response)
							log(myid, 'comment groups from file', f'group is closed {owner_id}')
							time.sleep(2)

						else:
							if len(response['response']['items']) != 0:
								if 'is_pinned' in response['response']['items'][0]:
									wall = response['response']['items'][1]

								else:
									wall = response['response']['items'][0]
							

								if wall ['comments']['can_post'] == 1:
									post_id = wall['id']
									message = random.choice(comments)

									resp = vkapi.wallComment(token, proxies, owner_id, post_id, message, myid=myid)

									if resp == 'captcha':
										log(myid, 'comment groups from file', 'captcha')

									elif resp == 'banned in group':
										log(myid, 'comment groups from file', 'comments closed or account banned in group, leaving')

									elif resp == 'internal server error':
										log(myid, 'comment groups from file', 'internal server error')
										sl(600)

									elif 'ok' in resp:
										cid = resp.split(' ')[1]
										log(myid, 'comment groups from file', f'comments posted, cid {cid}')

									else:
										log(myid, 'comment groups from file', str(resp))

								else:
									log(myid, 'comment groups from file', f'comments closed {owner_id}')

							else:
								log(myid, 'comment groups from file', f'no posts in group {owner_id}')

					elif d[0] == 'vc':
						q = d[1]
						videos = vkapi.videoSearch(kate_token, proxies, q, count=15, sort=2, offset=random.randint(10, 985))
						if len(videos) == 0:
							log(myid, 'video comment', 'error, video with open comms not found')

						else:
							video = random.choice(videos)
							message = random.choice(comments)

							owner_id = video['owner_id']
							video_id = video['id']

							resp = vkapi.videoComment(kate_token, proxies, owner_id, video_id, message)

							if resp == 'captcha':
								log(myid, 'video comment', 'captcha')

							elif resp == 'closed comments':
								log(myid, 'video comment', 'closed comments')

							elif resp == 'internal server error':
								log(myid, 'video comment', 'internal server error')

							elif 'ok' in resp:
								cid = resp.split(' ')[1]
								log(myid, 'video comment', f'comment posted, cid {cid}')

							else:
								log(myid, 'video comment', str(resp))

					elif d[0] == 'vu':
						porn_desc = d[2]
						q = d[1]

						offset = random.randint(10, 950)
						resp = vkapi.videoSearch(kate_token, proxies, q, comments_check=0, sort=2, filters='mp4,short', adult=0, offset=offset)
						video = random.choice(resp)

						for key in video['files']:
							pass

						link = video['files'][key]
						videopath = f'{bases.videos}{myid}.mp4'


						vkapi.videoDownload(link, videopath)
						resp = vkapi.videoUpload(kate_token, proxies, videopath, video ['title'], porn_desc)

						if 'size' in resp:
							log(myid, 'video upload', 'ok')

						elif 'error' in resp:
							if resp['error'] == 'too fast':
								log(myid, 'video upload', 'upload limit reached')

							else:
								log(myid, 'video upload', str(resp))

						else:
							log(myid, 'video upload', str(resp))

					elif d[0] == 'fs':
						resp = vkapi.friendGetSuggested(token, proxies, 100)

						if len(resp) == 0:
							log(myid, 'follow suggested', 'no suggested')

						else:
							uids = []
							for user in resp:
								uids.append(user['id'])

							uid = random.choice(uids)

							resp = vkapi.userAdd (token, proxies, uid, myid)

							if resp == 'captcha':
								log(myid, 'follow suggested', 'captcha')

							elif resp == 'not found':
								log(myid, 'follow suggested', 'user not found')

							elif resp == 'unknown error':
								log(myid, 'follow suggested', 'unknown error or limit reached')
								del(tasks[tasks.index(['fs'])])

							elif resp == 'ok':
								log(myid, 'follow suggested', 'user added')

							else:
								log(myid, 'follow suggested', str(resp))

					elif d[0] == 'ff':
						with open(d[1]) as file:
							uid = random.choice(file.read().splitlines())

						resp = vkapi.userAdd(token, proxies, uid)

						if resp == 'captcha':
							log(myid, 'follow from file', 'captcha')

						elif resp == 'not found':
							log(myid, 'follow from file', 'user not found')

						elif resp == 'unknown error':
							log(myid, 'follow from file', 'unknown error or limit reached')

						elif resp == 'ok':
							log(myid, 'follow from file', 'user added')

						else:
							log(myid, 'follow from file', str(resp))

					elif d[0] == 'fl':
						print('this function is not ready yet')

					elif d[0] == 'jf':
						group_id = random.choice(grouplist)
						del(grouplist[grouplist.index(group_id)])

						resp = vkapi.groupJoin(token, proxies, group_id, myid)

						if resp == 'captcha':
							log(myid, 'join group', 'captcha')

						elif resp == '5000':
							log(myid, 'join group', 'groups count limit reached')

						elif resp == 'ok':
							log(myid, 'join group', 'group joined')

						else:
							log(myid, 'join group', str(resp))

					for i in range(random.randint(st0, st1)):
						if getattr(t, 'do_run', True):
							time.sleep(1)


				except ConnectionResetError:
					print(bcolors.FAIL + 'ConnectionResetError' + bcolors.ENDC)

				except ConnectionError:
					print(bcolors.FAIL + 'ConnectionError' + bcolors.ENDC)

				except requests.exceptions.ProxyError:
					print('proxy error')

				except Exception as e:
					print('{} - {}'.format(myid, d[0]))
					print(e)
					print(type(e))
					with open('critical_errors.txt', 'a') as file:
						file.write(str(type(e)) + '\n')

					time.sleep(10)

			else:
				pass

	else:
		while getattr(t, 'do_run', True):
			for i in range(random.randint(st0, st1)):
				if getattr(t, 'do_run', True):
					time.sleep(1)

	try:
		tcr.do_run = False
		tcr.join()

	except:
		pass

	print('killing main thread')


###########################
def kill(names='n'):
	if names == 'n':
		killingthreads = []
		
		for i in threads:
			print(i)

		d = input('input name of group to kill\n↪ ')

		if d == 'cd':
			return

		elif d == 'all':
			keys = []
			for one in threads:
				keys.append(one)

			for one in keys:
				for i in threads[one]:
					killingthreads.append(threads[one][i][0])

				del(threads[one])

		else:
			keys = d.split(' ')

			for one in keys:
				for i in threads[one]:
					killingthreads.append(threads[one][i][0])

				del(threads[one])


		for t in killingthreads:
			t.do_run = False
			t.join()


	else:
		killingthreads = []
		
		for name in names:
			for i in threads[name]:
				killingthreads.append(threads[name][i][0])

			del(threads[name])


		for t in killingthreads:
			t.do_run = False
			t.join()


############################






def main():
	while True:
		info = ''
		print(info)

		d = input(bcolors.OKBLUE + 'main' + bcolors.ENDC + '\n↪ ')

		if d == 'add':
			d = input('proxies (1) or accounts (2)\n↪ ')

			if d == '1':
				addproxies()

			elif d == '2':
				addaccounts()

			elif d == 'clear':
				os.system('clear')

			elif d == 'cd':
				return

			else:
				print('command unknown {}'.format(d))

		elif d == 'groups':
			groups()

		elif d == 'start':
			start()

		elif d == 'restart':
			restart()

		elif d == 'check':
			bancheck()



		elif d == 'la':
			print(la())

		elif d == 'ls':
			print(ls())

		elif d == 'lc':
			print(ls(onlynames=1))


		elif d == 'kill':
			kill()


		elif d == 'log':
			showlog()

		elif d == 'logclear':
			with open(files.log, 'w') as file:
				pass


		elif d == 'clear':
			os.system('clear')


		elif d =='1':
			pass
			







if __name__ == '__main__':
	os.system('clear')
	main()