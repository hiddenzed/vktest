import json
import requests
import time
import os

from config import rucaptcha_token

captchalink = 'http://rucaptcha.com/'


def main(imglink, uid):
	getimage(imglink, uid)

	captchakey = getresult(sendcaptcha(uid))
	os.remove('{}.jpg'.format(uid))

	return captchakey


def getimage(imagelink, uid):
	im = requests.get(imagelink)
	jpegimage = open('{}.jpg'.format(uid), 'wb')
	jpegimage.write(im.content).close()


def sendcaptcha(uid):
	files = {'file': open('{}.jpg'.format(uid), 'rb')}
	captcha_params = {
		'key':rucaptcha_token,
		'method': post,
		'json': 1}

	cid = requests.post(captchalink + 'in.php', files=files,
		params=captcha_params).json()['request']

	time.sleep(7)
	return cid


def getresult(cid):
	get_result_params = {
		'key': rucaptcha_token,
		'action': 'get',
		'json': 1,
		'id': cid
	}

	answer = 'CAPCHA_NOT_READY'

	while answer == 'CAPCHA_NOT_READY':
		time.sleep (1)
		answer = requests.get(captchalink + 'res.php',
			params=getresultparams).json()['request']

	return answer

if __name__ == '__main__':
	main ()
