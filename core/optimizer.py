import os, string, random
from time import time
from PIL import Image, ImageSequence
from typing import List, Optional

class ImageOptimizer(object):
	"""
	A class to optimize images by compressing and resizing them based on user-defined settings.

	This class provides functionality to:
	- Parse and filter images from a specified folder.
	- Resize images while maintaining aspect ratio.
	- Compress images to reduce file size.
	- Generate new filenames with options for overwriting, adding prefixes, and timestamps.
	- Convert images to different formats.

	Attributes:
		parent (object): The parent object, typically the main application.
		path (str): The path to the folder containing images to be optimized.
		config (dict): A dictionary containing configuration settings for optimization.
		base_width (int): The base width to resize images to, maintaining aspect ratio.
		images (list): A list of image file paths to be processed.

	Methods:
		parseImages(basepath, folder):
			Parse and filter images in the specified folder based on allowed extensions.
		
		setName(image_path, overwrite, timestamp=True, prefix='-export', extension='default'):
			Generate a new filename for the image based on specified options.
		
		setAbsPath(filename):
			Get the absolute path for the given filename in the current path.
		
		resize(pillow_image):
			Resize the given Pillow image to the base width while maintaining aspect ratio.
		
		compress(overwrite=False, images=None, filemode=False):
			Compress and resize images based on the current configuration settings.

		buildGif(images, output_path):
			Build a GIF image from multiple images.
	"""

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
	def parseImages(basepath: str, folder: str) -> List[str]:
		"""
		Parse and filter images in the specified folder based on allowed extensions.

		Args:
			basepath (str): The base path where images are stored.
			folder (str): The folder to search for images.

		Returns:
			List[str]: A list of image file names with allowed extensions.
		"""		
		images = []
		# List of allowed extensions in lowercase
		extensions = [ext.lower() for ext in ImageOptimizer.allowed_extensions]		

		# Iterate through items in the folder
		for item in os.listdir(folder):			
			item_abs_path = os.path.join(folder, item)
			# Check if the item is a file
			if os.path.isfile(item_abs_path):				
				_, ext = os.path.splitext(os.path.basename(item))
				# Check if the file has an allowed extension
				if ('.' in ext) and (ext.lstrip('.').lower() in extensions):
					images.append(item)
		return images
	
	@staticmethod
	def generateRandomName(prefix="", extension="jpg"):
		"""
		Generates a random image name with a prefix and extension.

		Args:
			prefix (str, optional): A prefix to add to the image name. Defaults to "".
			extension (str, optional): The image extension. Defaults to "jpg".

		Returns:
			str: A random image name with the format prefix_randomString.extension
		"""
		letters = string.ascii_lowercase
		random_string = ''.join(random.choice(letters) for i in range(10))
		return f"{prefix}{random_string}.{extension}"

	@staticmethod
	def setName(image_path: str,
			overwrite: bool,
			timestamp: bool = True,
			prefix: str = '-export',
			extension: str = 'default'
		):
		"""
		Generate a new filename for the image based on the specified options.

		Args:
			image_path (str): The original image file path.
			overwrite (bool): Whether to overwrite the original file.
			timestamp (bool): Whether to include a timestamp in the filename. Defaults to True.
			prefix (str): A prefix to add to the filename. Defaults to '-export'.
			extension (str): The file extension to use. Defaults to 'default'.

		Returns:
			str: The new filename.
		"""				
		if overwrite:
			return os.path.basename(image_path)
			
		basename, ext = os.path.splitext(os.path.basename(image_path))

		print('============>', extension)
		# Use the provided extension or keep the source extension
		if (extension != 'default'):
			ext = f'.{extension}'
			
		# Generate the filename with the prefix
		filename = f'{basename}{prefix}{ext}'

		# Add timestamp to the filename if required
		if timestamp:            	
			filename = f'{basename}{prefix}-{time()}{ext}'
				
		return filename

	def setAbsPath(self, filename: str) -> str:
		"""
		Get the absolute path for the given filename in the current path.

		Args:
			filename (str): The filename for which to generate the absolute path.

		Returns:
			str: The absolute path of the filename.
		"""
		return os.path.join(self.path, filename)
	
	@staticmethod
	def calculateAspectRatioHeight(width: int, image: Image.Image) -> int:
		"""
		Calculate the new height of the image to maintain the aspect ratio based on the given width.

		Args:
			width (int): The desired width of the image.
			image (Image.Image): The original image.

		Returns:
			int: The new height of the image to maintain the aspect ratio.
		"""
		# Calculate the scale factor to resize the image based on the new width
		wpercent = (width / float(image.size[0]))

		# Calculate the new height to maintain the aspect ratio
		hSize = int((float(image.size[1]) * float(wpercent)))
		
		print(f'-- 01 --> Calculated new height: {hSize}')
		return hSize

	def resize(self, pillow_image: Image.Image) -> Image.Image:
		"""
		Resize an image to a new width while maintaining the aspect ratio.
		
		Args:
			pillow_image (Image.Image): The original image to resize.
		
		Returns:
			PIL.Image.Image: The resized image.
		"""		
		hSize = self.calculateAspectRatioHeight(self.base_width, pillow_image)
		# Resize the image using the calculated dimensions and high-quality resampling
		if (self.base_width > 0 and hSize > 0):
			print(f'-- 2 --> Resized to {self.base_width}x{hSize}')
			return pillow_image.resize((self.base_width, hSize), Image.Resampling.LANCZOS)
		else:
			return pillow_image	

	def compress(self,
			overwrite: bool = False,
			images: List[str] = None,
			filemode: bool = False
		) -> None:
		"""
		Compress and resize images based on configuration settings.

		Args:
			overwrite (bool): Whether to overwrite the original images. Defaults to False.
			images (list[str]): List of image file paths to be compressed. If None, parse images from the base path. Defaults to None.
			filemode (bool): Whether to use file mode for saving the images. Defaults to False.
		"""
		# Set the list of images to be processed
		if images:
			self.images = images
		else:
			self.images = ImageOptimizer.parseImages(self.parent.basepath, self.path)

		# Process each image
		for i,image_path in enumerate(self.images):
			# Open the image
			im = Image.open(self.setAbsPath(image_path))
			
			# Resize the image if the width exceeds the specified base width
			w, h = im.size
			if self.base_width:				
				if w > self.base_width:
					im = self.resize(im)

			# Set the export filename with options like timestamp and prefix
			format = self.config.get('format', 'default')
			filename = ImageOptimizer.setName(image_path, 
				overwrite,
				timestamp=self.config.get('timestamp', True),
				prefix=self.config.get('prefix', '-export'), 
				extension=format
			)
			
			# File mode: determine the destination path for the image
			if filemode:				
				dest_path = os.path.join(os.path.dirname(image_path), filename)
			else:
				dest_path = self.setAbsPath(filename)

			# Print debug information
			# print('Save to ', dest_path)
			print(dest_path, filename)
			print('Format: ', format)

			# Convert the image to RGB mode if the format is JPEG, as JPEG does not support RGBA
			if (format == 'jpg'):
				im = im.convert('RGB')
			
			# Save the image with the specified quality and format
			if format == 'default':
				im.save(dest_path, quality=self.config.get('quality', 80), optimize=True)
			else:
				print('====> Save into this format: ', format)
				im.save(dest_path, quality=self.config.get('quality', 80), optimize=True, format=format)

			# Emit the progress signal
			progress_value = ((i+1) * 100) // len(self.images)
			self.parent.signalProgression.emit(progress_value)

	def getLargestImage(self) -> Optional[Image.Image]:
		"""
		Finds the largest image in terms of dimensions from the `self.images` list.

		Returns:
			Image.Image or None: The largest image found, or None if no images are found or if dimensions are not determined.
		"""
		largest_image = None
		max_area = 0

		# Iterate through all images to find the largest one
		for image_path in self.images:
			try:
				im = Image.open(self.setAbsPath(image_path))
				width, height = im.size
				area = width * height

				if area > max_area:
					max_area = area
					largest_image = im

			except IOError as e:
				print(f"Error opening image {image_path}: {e}")

		return largest_image

	def buildGif(self,
		images: List[str] = [],
		filemode: bool = False,
		duration: int = 30,
		loop: int = 0,
		bgColor: tuple = (0, 0, 0)
	) -> None:
		"""
		Build a GIF image from multiple images.

		Args:
			images (List[str]): List of image file paths to be included in the GIF.
			filemode (bool): If True, the built GIF image will be saved in the same directory as the first image in the list.
			duration (int): The duration (in milliseconds) for each frame of the GIF.
			loop (int): The number of times the GIF should loop. 0 means loop indefinitely.
			bgColor (tuple): Background color as RGB.
		Returns:
			dest_path (str): Destination path of the final GIF file.
		"""
		# Set the list of images to be processed
		if images:
			self.images = images
		else:
			self.images = ImageOptimizer.parseImages(self.parent.basepath, self.path)

		frames = []
		# first_image = Image.open(self.setAbsPath(self.images[0]))		
		largest_image = self.getLargestImage()
		max_width, max_height = largest_image.size
		if self.base_width > 0:
			max_width = self.base_width
			max_height = self.calculateAspectRatioHeight(max_width, largest_image)
		for i, image_path in enumerate(self.images):
			# Open the image
			im = Image.open(self.setAbsPath(image_path))			
			# Resize the image while maintaining the aspect ratio
			resized_frame = self.resize(im)			
			# Create a black background if the image is smaller than the base size
			background = Image.new("RGB", (max_width, max_height), bgColor)
			# Center the image on the background
			position = ((max_width - resized_frame.width) // 2, (max_height - resized_frame.height) // 2)
			background.paste(resized_frame, position)
			# Append the resized frame to the frames list
			frames.append(background)

			# Emit the progress signal (Keep 25% to saving process)
			progress_value = ((i + 1) * 100) // len(self.images) - 25
			self.parent.signalProgression.emit(progress_value)

		filename = self.generateRandomName('GIF_', 'gif')

		# File mode: determine the destination path for the image
		if filemode:
			dest_path = os.path.join(os.path.dirname(self.images[0]), filename)
		else:
			dest_path = self.setAbsPath(filename)

		# Save the frames as a GIF
		if frames:
			frames[0].save(
				dest_path,
				save_all=True,
				append_images=frames[1:],
				loop=loop,
				duration=duration,
				optimize=True
			)
		self.parent.signalProgression.emit(100)
		return dest_path

# opt = ImageOptimizer(r'C:\Users\Usera\Pictures\bank\pixabay')
# opt.compress()