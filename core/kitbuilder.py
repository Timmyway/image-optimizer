import requests, os
from bs4 import BeautifulSoup

class Kitbuilder(object):
	"""docstring for Kitbuilder"""
	url = 'http://127.0.0.1:9000/'
	def __init__(self, user_creds):
		super(Kitbuilder, self).__init__()
		self.url = ''
		self.session = requests.Session()
		self.user_creds = user_creds
		self.user = None
		self.headers = None
		self.cookies = None		
		try:
			self.login()
			self.status = 'on'
		except:
			print('Could not connect to Kitbuilder api')
			self.status = 'off'		

	def getToken(self, url, token={}):
		page = self.session.get(url)
		soup = BeautifulSoup(page.text, 'html.parser')
		print('==========> soup', soup)
		tag = token.get('tag', 'meta')
		search = token.get('search', {"name": "csrf-token"})
		attr = token.get('value', 'content')
		token = soup.find(tag, search).get(attr)			
		return token

	def login(self):
		login_url = f'{Kitbuilder.url}login'
		sanctum_url = f'{Kitbuilder.url}sanctum/csrf-cookie'
		payload = {
			'email': self.user_creds['username'],
			'password': self.user_creds['password']
		}
		sanctum_page_response = self.session.get(sanctum_url)
		if 'XSRF-TOKEN' in self.session.cookies:
			xsrf_token = self.session.cookies['XSRF-TOKEN']		
		csrf_token = self.getToken(login_url)
		self.headers = {			
			'X-CSRF-TOKEN': csrf_token,
    		'Accept': "application/json",
    		'Referer': Kitbuilder.url
		}
		self.cookies = {
			'csrftoken': csrf_token,
			'XSRF-TOKEN': xsrf_token
		}
		print(payload)
		print('Headers: ', self.headers)
		r = self.session.post(login_url, data=payload, headers=self.headers)		

	def getImages(self, page=1, user='all'):		
		gallery_url = f'{Kitbuilder.url}api/images/?page=1&user=all'
		print('Reach endpoint: ', gallery_url)
		print('Open this url: ', gallery_url)		
		r = self.session.get(gallery_url, headers=self.headers)		
		images = r.json()
		return images


	def storeImage(self, image_url):
		gallery_url = f'{Kitbuilder.url}api/images'
		print('POST to following endpoint: ', gallery_url)
		files = {'image_to_upload': open(image_url,'rb')}
		payload = {
			'name': os.path.basename(image_url)
		}
		self.headers['X-CSRF-TOKEN'] = self.getToken(gallery_url)
		r = self.session.post(gallery_url, headers=self.headers, files=files, params=payload)		
		image = r.json()		
		try:
			return image['url']
		except KeyError:
			return ''
		return ''

	def deleteImage(self, image_id):
		gallery_url = f'{Kitbuilder.url}api/images/{image_id}'
		print('DEL to following endpoint: ', gallery_url)		
		self.headers['X-CSRF-TOKEN'] = self.getToken(gallery_url)
		r = self.session.delete(gallery_url, headers=self.headers)
		response = r.json()		
		try:
			return response['response']
		except KeyError:
			return response['error']

	@staticmethod
	def save(content):
		with open('report.html', 'w', encoding='utf-8') as f:
			f.write(content)