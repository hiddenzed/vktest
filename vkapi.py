import requests
import json
import lxml.html
import time
import pathlib
import captcha
import random
import bs4

def get_access_token(s, login, paswd, proxies, headers, client_id='4083558', log_in=1):
	if log_in == 1:
		loginpage = s.get('https://m.vk.com/login', proxies=proxies, headers=headers)
		parsedloginpage = lxml.html.fromstring(loginpage.content)
		form = parsedloginpage.forms[0]

		form.fields['email'] = login
		form.fields['pass'] = paswd

		auth = s.post(form.action, data=form.form_values(), proxies=proxies, headers=headers)


	params = {
		'client_id': client_id,
		'scope': 'friends,photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,messages,notifications,stats,ads,market,offline',
		'redirect_uri': 'https://api.vk.com/blank.html',
		'display': 'wap',
		'v': '5.80',
		'response_type': 'token',
		'revoke': 0}

	data = s.get('https://oauth.vk.com/authorize',
		params=params, proxies=proxies, headers=headers)

	try:
		toked = lxml.html.fromstring(data.content)
		form  = toked.forms [0]

		data = s.post(form.action, proxies=proxies, headers=headers)

	except:
		pass


	try:
		access_token = data.url.split('access_token=')[1].split('&expires')[0]

	except:
		access_token = data.url

	return access_token

def userAdd(access_token, proxies, user_id, myid='1'):
	params = {'access_token': access_token, 'v': '5.80', 'user_id': user_id}

	response = requests.get ('https://api.vk.com/method/friends.add',
		params=params, proxies=proxies).json ()

	if 'error' in response:
		if response['error']['error_code'] == 14:
			capkey = captcha.main (response ['error']['captcha_img'], myid)

			params.update ({'captcha_sid': response ['error']['captcha_sid'],
				'captcha_key': capkey})

			response = requests.get ('https://api.vk.com/method/friends.add',
				params=params, proxies=proxies).json ()

			return 'captcha'

		elif response ['error']['error_code'] == 177:
			params = {'access_token': access_token, 'v': '5.80', 'owner_id': user_id}
			resp = requests.get('https://api.vk.com/method/account.ban',
				params=params, proxies=proxies).json()

			return 'not found'

		elif response ['error']['error_code'] == 1:
			return 'unknown error'

		else:
			return response

	else:
		return 'ok'

def feedGet(access_token, proxies, count=10, start_time=0):
	params = {
		'access_token': access_token,
		'v': '5.80',
		'filters': 'post',
		'count': count,
		'start_time': start_time}

	feed = requests.get('https://api.vk.com/method/newsfeed.get', params=params, proxies=proxies)

	try:
		feed = feed.json()['response']['items']
		return feed

	except:
		try:
			return ['error', feed.json()]

		except:
			return ['error', feed]


def wallComment(access_token, proxies, owner_id, post_id, message=None, attachments=None, myid='1'):
	params = {'access_token': access_token, 'v': '5.80', 'owner_id': owner_id, 'post_id': post_id}

	if attachments != None:
		params.update({'attachments': attachments})

	if message != None:
		params.update({'message': message})

	response = requests.get('https://api.vk.com/method/wall.createComment',
		params=params, proxies=proxies)

	try:
		response = response.json()

		if 'error' in response:
			if response['error']['error_code'] == 14:
				capkey = captcha.main(response ['error']['captcha_img'], myid)

				params.update({'captcha_sid': response ['error']['captcha_sid'], 'captcha_key': capkey})

				response = requests.get('https://api.vk.com/method/wall.createComment',
					params=params, proxies=proxies).json()

				return 'captcha'

			elif response['error']['error_code'] == 213:
				params = {'group_id': -owner_id, 'access_token': access_token, 'v': '5.80'}

				requests.get('https://api.vk.com/method/groups.leave',
					params=params, proxies=proxies).json()

				return 'banned in group'

			elif response['error']['error_code'] == 10:
				return 'internal server error'

		else:
			cid = response['response']['comment_id']
			return f'ok {cid}'

	except:
		try:
			return response.json()

		except:
			return response

def videoSearch(access_token, proxies, q, comments_check=1, sort=0, adult=1, count=100, filters='mp4', offset=0):
	params = {
		'access_token': access_token,
		'v': '5.80',
		'q': q,
		'adult': adult,
		'sort': sort,
		'count': count,
		'filters': filters,
		'offset': offset}

	videos = requests.get('https://api.vk.com/method/video.search',
		params=params, proxies=proxies).json()


	try:
		if len(videos['response']['items']) == 0:
			print(videos['response'])
			
		videos = videos['response']['items']

	except:
		print(videos)

	# print(len(videos))
	# print(videos)

	time.sleep(0.5)

	if comments_check == 1:
		videos_ls = ''
		resp = []

		for video in videos:
			owner_id = video['owner_id']
			vid = video['id']
			videos_ls += f'{owner_id}_{vid},'

			params = {'access_token': access_token, 'v': '5.84', 'extended': 1, 'videos': videos_ls}

			response = requests.get('https://api.vk.com/method/video.get',
				params=params, proxies=proxies).json()

			time.sleep(1)

			try:
				response = response['response']['items']

			except:
				print(response)

			resp += response
		videos = []

		for video in resp:
			try:
				if video['can_comment'] == 1:
					videos.append (video)

			except:
				print('big error')

		return videos

	else:
		return videos

def videoComment(access_token, proxies, owner_id, video_id, message=None, attachments=None, myid='1'):
	params = {'access_token': access_token, 'v': '5.80', 'owner_id': owner_id, 'video_id': video_id}

	if attachments != None:
		params.update({'attachments': attachments})

	if message != None:
		params.update({'message': message})

	response = requests.get('https://api.vk.com/method/video.createComment',
		params=params, proxies=proxies)

	try:
		response = response.json()

		if 'error' in response:
			if response['error']['error_code'] == 14:
				capkey = captcha.main(response ['error']['captcha_img'], myid)

				params.update({'captcha_sid': response['error']['captcha_sid'], 'captcha_key': capkey})

				response = requests.get('https://api.vk.com/method/video.createComment',
					params=params, proxies=proxies).json()

				return 'captcha'

			elif response['error']['error_code'] == 801:
				return 'closed comments'

			elif response['error']['error_code'] == 10:
				return 'internal server error'

		else:
			cid = response['response']

			return f'ok {cid}'

	except:
		try:
			return response

		except:
			return response.json()

def videoDownload(link, name):
	im = requests.get(link, stream=True)

	with open(name, 'wb') as file:
		for chunk in im.iter_content(1024000):
			file.write(chunk)

def videoUpload(access_token, proxies, videopath, title, desc):
	params = {'access_token': access_token, 'v': '5.80', 'name': title, 'description': desc}

	response = requests.get('https://api.vk.com/method/video.save',
		params=params, proxies=proxies).json ()

	upload_url = response

	try:
		upload_url = upload_url['response']['upload_url']
		files = {'video_file': open(videopath, 'rb')}
		response = requests.post(upload_url, files=files, proxies=proxies)

		return response.json()

	except Exception as e:
		if 'error' in upload_url:
			if upload_url['error']['error_code'] == 204:
				return 'Access denied: user was banned for this action, can\'t add video'
			
			else:
				print(upload_url['error']['error_msg'])

		else:
			print(e)
			print(type(e))
			return upload_url

		

def friendGetSuggested(access_token, proxies, count=10):
	params = {'access_token': access_token, 'v': '5.80', 'count': count}
	response = requests.get('https://api.vk.com/method/friends.getSuggestions',
		params=params, proxies=proxies).json()['response']['items']

	return response

def groupJoin(access_token, proxies, group_id, myid='1'):
	# try:
	params = {'access_token': access_token, 'v': '5.80', 'group_id': group_id}

	response = requests.get('https://api.vk.com/method/groups.join',
		params=params,proxies=proxies).json()

	if 'error' in response:
		if response['error']['error_code'] == 14:
			capkey = captcha.main(response['error']['captcha_img'], myid)
			params.update({'captcha_sid': response['error']['captcha_sid'], 'captcha_key': capkey})

			requests.get('https://api.vk.com/method/groups.join',
				params=params, proxies=proxies).json()

			return 'captcha'

		elif response['error']['error_code'] == '103':
			return '5000'

		else:
			return response

	else:
		return 'ok'

	# except:
	# 	return 'error'

def avatarPost(access_token, proxies, path_to_photo='none'):
	files  = {'file': open(path_to_photo, 'rb')}
	params = {'access_token': access_token, 'v': '5.80'}

	avatar_url = requests.get('https://api.vk.com/method/photos.getOwnerPhotoUploadServer',
		params=params, proxies=proxies).json()['response']['upload_url']

	params = requests.post(avatar_url, files=files, proxies=proxies).json()

	params.update({'access_token': access_token, 'v': '5.80'})

	response = requests.get('https://api.vk.com/method/photos.saveOwnerPhoto',
		params=params, proxies=proxies).json()

	if 'response' in response:
		return 'ok'

	else:
		return response

def privacySet(access_token, proxies, keys):
	random.shuffle(keys)
	for key in keys:
		params = {'access_token': access_token, 'v': '5.80', 'key': key, 'value': 'nobody'}
		response = requests.get('https://api.vk.com/method/account.setPrivacy',
			params=params, proxies=proxies).json()

		if 'response' in response:
			print (f'done: {key} settings are set')

		else:
			print (response)

def logIn(login, paswd, proxies, headers):
	s = requests.session()
	loginpage = s.get('https://m.vk.com/login', proxies=proxies, headers=headers)
	parsedloginpage = lxml.html.fromstring(loginpage.content)
	form = parsedloginpage.forms[0]

	form.fields['email'] = login
	form.fields['pass'] = paswd

	auth = s.post(form.action, data=form.form_values(), proxies=proxies, headers=headers)

	return s

def stickersGet(s, proxies, headers):
	stickerLinks = [
		'https://m.vk.com/stickers?stickers_id=1&tab=free',
		'https://m.vk.com/stickers?stickers_id=2&tab=free',
		'https://m.vk.com/stickers?stickers_id=4&tab=free',
		'https://m.vk.com/stickers?stickers_id=75&tab=free',
		'https://m.vk.com/stickers?stickers_id=108&tab=free',
		'https://m.vk.com/stickers?stickers_id=139&tab=free',
		'https://m.vk.com/stickers?stickers_id=148&tab=free',
		'https://m.vk.com/stickers?stickers_id=267&tab=free',
		'https://m.vk.com/stickers?stickers_id=148&tab=free']

	for url in stickerLinks:
		data = s.get (url, proxies=proxies, headers=headers)

		try:
			soup = bs4.BeautifulSoup (data.content, 'html.parser')
			q = soup.find('a', class_="button wide_button sp_buy_str").get('href')

			s.get ('https://m.vk.com/' + str(q), proxies=proxies, headers=headers)

		except:
			print('error while stickers getting')

def albumsGet(access_token, proxies, owner_id=0):
	params = {'access_token': access_token, 'v': '5.80', 'need_system': 1}

	if owner_id != 0:
		params.update({'owner_id': owner_id})

	response = requests.get('https://api.vk.com/method/photos.getAlbums',
		params=params, proxies=proxies).json()['response']['items']

	return response

def photosDelete(access_token, proxies, album='profile', count='all'):
	params = {'access_token': access_token, 'v': '5.80', 'count': 1000, 'album_id': album}

	try:
		photos = requests.get('https://api.vk.com/method/photos.get',
			params=params, proxies=proxies).json()['response']['items']

		if count != 'all':
			photos = photos [:count]

		resp = []
		for photo in photos:
			params = {'access_token': access_token, 'v': '5.80', 'owner_id': photo ['owner_id'], 'photo_id': photo ['id']}

			response = requests.get('https://api.vk.com/method/photos.delete',
				params=params, proxies=proxies).json()

			if 'error' in response:
				if response['error']['error_code'] == 100:
					resp.append('photo is incorrect')

				else:
					resp.append(response ['error']['error_msg'])

			elif 'response' in response:
				resp.append('photo deleted')

			else:
				resp.append(response)

			time.sleep (0.15)

		return resp

	except:
		return 'error'

def getMostViewedPost(posts):
	wall = {'views': {'count': 0}}

	for post in posts:
		try:
			if post['comments']['can_post'] == 1:
				try:
					if post['views']['count'] > wall['views']['count']:
						wall = post

				except KeyError:
					pass

				except Exception as e:
					print('getMostViewedPost, views, exception - ', e)
					print(e)
					print(type(e))

		except Exception as e:
			print('getMostViewedPost, comments, exception - ', e)

	return wall
