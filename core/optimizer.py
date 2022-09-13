import os
from time import time
from PIL import Image

class ImageOptimizer(object):
	"""docstring for ImageOptimizer"""
	def __init__(self, path, config={'quality': 80, 'base_width': 600}):
		super(ImageOptimizer, self).__init__()
		self.path = path
		self.images = os.listdir(self.path)
		self.config = config
		self.base_width = self.config.get('base_width', 600)

	@staticmethod
	def setName(image_path, timestamp=True, prefix='-export'):
		basename = os.path.basename(image_path)
		base, ext = os.path.splitext(basename)
		filename = f'{base}{prefix}{ext}'
		if timestamp:            	
			filename = f'{base}{prefix}-{time()}{ext}'
		return filename

	def setAbsPath(self, filename):
		return os.path.join(self.path, filename)

	def resize(self, pillow_image):
		# Scale factor
		wpercent = (self.base_width / float(pillow_image.size[0]))
		# Calculate the new height of the image
		hsize = int((float(pillow_image.size[1]) * float(wpercent)))
		return pillow_image.resize((self.base_width, hsize), Image.ANTIALIAS)
		
	def compress(self, timestamp=True):
		for image_path in self.images:
			im = Image.open(self.setAbsPath(image_path))
			# Resize image if it is too much big		
			w, h = im.size
			if w > self.base_width:
				im = self.resize(im)
			filename = ImageOptimizer.setName(image_path)
			dest_path = self.setAbsPath(filename)
			# print('Save to ', dest_path)
			im.save(dest_path, quality=self.config.get('quality', 80), optimize=True)

# opt = ImageOptimizer(r'C:\Users\Usera\Pictures\bank\pixabay')
# opt.compress()