dt = 'dt/'

class bcolors:
	HEADER  = '\033[95m'
	OKBLUE  = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL    = '\033[91m'
	ENDC    = '\033[0m'
	BOLD    = '\033[1m'
	UNDER   = '\033[4m'


class info:
	main = ''
	groups = '(1) create\n(2) edit\n(3) actions\n(4) glue groups\n(5) delete'
	group_edit = '(1) group info\n(2) tasks\n(3) accounts'

class files:
	groups = dt + 'groups.json'
	awg = dt + 'awg.json'
	log = dt + 'log.txt'
	banned = dt + 'banned.json'


class bases:
	comments = dt + 'bases/comments.txt'
	uas = dt + 'bases/useragents.txt'

	videos = dt + 'bases/videos/'
	proxies = dt + 'bases/aip/proxies.txt'

	badproxies = dt + 'bases/aip/badproxies.txt'
	badaccounts = dt + 'bases/aip/badaccounts.txt'

	avadirs = dt + 'bases/a/'

class js:
	la = dt + 'js/la.js'

class infiles:
	proxies = dt + 'in/proxies.txt'
	accounts = dt + 'in/accounts.txt'


rucaptcha_token = ''