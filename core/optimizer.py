import os
from time import time
from PIL import Image

class ImageOptimizer(object):
	"""docstring for ImageOptimizer"""

	allowed_extensions = ['WebP', 'png', 'jpeg', 'jpg', 'gif', 'ico', 'tiff' 'bmp']

	def __init__(self, parent, path, config={
			'quality': 80, 
			'base_width': 600,
			'format': 'default', 
			'prefix': '-export', 
			'timestamp': True
		}
	):
		super(ImageOptimizer, self).__init__()
		self.parent = parent
		self.path = path
		self.images = []
		self.config = config
		self.base_width = self.config.get('base_width', 600)		

	@staticmethod
	def parseImages(basepath, folder):
		# keep only allowed images		
		images = []
		extensions = [ext.lower() for ext in ImageOptimizer.allowed_extensions]		
		for item in os.listdir(folder):			
			item_abs_path = os.path.join(folder, item)
			if os.path.isfile(item_abs_path):				
				_, ext = os.path.splitext(os.path.basename(item))				
				if ('.' in ext) and (ext.lstrip('.').lower() in extensions):
					images.append(item)		
		return images

	@staticmethod
	def setName(image_path, overwrite, timestamp=True, prefix='-export', extension='default'):				
		if overwrite:
			return os.path.basename(image_path)
		basename, ext = os.path.splitext(os.path.basename(image_path))
		# Default keep the source ext, otherwise extension provided by UI havn't "."
		if (extension != 'default'):
			ext = '.' + extension
		# Prefix added if any
		filename = f'{basename}{prefix}{ext}'
		# Timestamp added on option
		if timestamp:            	
			filename = f'{basename}{prefix}-{time()}{ext}'		
		return filename

	def setAbsPath(self, filename):
		return os.path.join(self.path, filename)

	def resize(self, pillow_image):
		# Scale factor
		wpercent = (self.base_width / float(pillow_image.size[0]))
		# Calculate the new height of the image
		hsize = int((float(pillow_image.size[1]) * float(wpercent)))
		return pillow_image.resize((self.base_width, hsize), Image.ANTIALIAS)
		
	def compress(self, overwrite=False, images=None, filemode=False):
		if images:
			self.images = images
		else:
			self.images = ImageOptimizer.parseImages(self.parent.basepath, self.path)
		for i,image_path in enumerate(self.images):
			im = Image.open(self.setAbsPath(image_path))
			# Resize image if it is too much big and base width is above 0
			w, h = im.size
			if self.base_width:				
				if w > self.base_width:
					im = self.resize(im)
			# Set export name (options: add timestamp, suffix ...)
			format = self.config.get('format', 'default')			
			filename = ImageOptimizer.setName(image_path, 
				overwrite,
				timestamp=self.config.get('timestamp', True),
				prefix=self.config.get('prefix', '-export'), 
				extension=format
			)
			# File mode
			if filemode:
				dest_path = os.path.join(os.path.dirname(image_path), filename)
			else:
				dest_path = self.setAbsPath(filename)
			# print('Save to ', dest_path)			
			print(dest_path, filename)
			print('Format: ', format)
			# Since JPEG does not support the RGBA color mode, 
			# the image needs to be converted to a compatible color mode before saving it as a JPEG.
			if (format == 'jpg'):
				im = im.convert('RGB')
			if format:
				im.save(dest_path, quality=self.config.get('quality', 80), 
					optimize=True				
				)
			else:
				im.save(dest_path, quality=self.config.get('quality', 80), 
					optimize=True,
					format=format
				)
			progress_value = ((i+1) * 100) // len(self.images)
			self.parent.signalProgression.emit(progress_value)	

# opt = ImageOptimizer(r'C:\Users\Usera\Pictures\bank\pixabay')
# opt.compress()