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

	allowed_extensions = ['webp', 'png', 'jpeg', 'jpg', 'gif', 'ico', 'tiff', 'bmp']

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
             filemode: bool = False) -> None:
		"""Compress and resize images; automatically optimizes GIFs using reduceGifSize."""

		self.images = images or ImageOptimizer.parseImages(self.parent.basepath, self.path)

		for i, image_path in enumerate(self.images):
			abs_path = self.setAbsPath(image_path)
			ext = os.path.splitext(image_path)[1].lower()

			# Generate filename and destination path
			format = self.config.get("format", "default")
			normalized_format = format.lower()
   
			filename = ImageOptimizer.setName(
				image_path,
				overwrite,
				timestamp=self.config.get("timestamp", True),
				prefix=self.config.get("prefix", "-export"),
				extension="gif" if ext == ".gif" else normalized_format
			)
			dest_path = os.path.join(os.path.dirname(image_path), filename) if filemode else self.setAbsPath(filename)

			if ext == ".gif":
				# Map quality to colors and frame_step
				q = self.config.get("quality", 80)
				colors = max(2, min(256, q))
				frame_step = max(1, int(12 - q / 10))
				self.reduceGifSize(abs_path, dest_path, colors=colors, frame_step=frame_step, max_width=self.base_width or None)
			else:
				# Open, resize, and save normal images
				im = Image.open(abs_path)
    
				if self.base_width and im.width > self.base_width:
					im = self.resize(im)				

				if normalized_format in ("jpg", "jpeg"):
					im = im.convert("RGB")

				save_args = {
					"quality": self.config.get("quality", 80),
					"optimize": True
				}
    
				if normalized_format != "default":
					save_args["format"] = (
						"JPEG"
						if normalized_format in ("jpg", "jpeg")
						else normalized_format.upper()
					)

				im.save(dest_path, **save_args)

			# Emit progress
			self.parent.signalProgression.emit(((i + 1) * 100) // len(self.images))

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
	
	def reduceGifSize(
		self,
		gif_path: str,
		output_path: Optional[str] = None,
		colors: int = 24,
		frame_step: int = 6,
		max_width: Optional[int] = None,
	) -> str:
			"""
			Reduce the file size of an animated GIF with optional downscaling.

			Args:
				gif_path (str): Path to the original GIF.
				output_path (str, optional): Destination path.
					Defaults to '<basename>-optimized.gif'.
				colors (int): Max colors to keep (lower = smaller size).
				frame_step (int): Keep every n-th frame.
				max_width (int, optional): Resize each frame to this width
					(maintains aspect ratio). If None, keep original size.

			Returns:
				str: Path to the optimized GIF.
			"""
			if output_path is None:
				base, ext = os.path.splitext(gif_path)
				output_path = f"{base}-optimized{ext}"

			im = Image.open(gif_path)
			frames, durations = [], []
			total_frames = im.n_frames

			for i in range(0, total_frames, frame_step):
				im.seek(i)
				frame = im.copy()

				# --- Optional downscale ---
				if max_width:
					w, h = frame.size
					if w > max_width:
						ratio = max_width / float(w)
						new_h = int(h * ratio)
						frame = frame.resize((max_width, new_h), Image.Resampling.LANCZOS)

				# Maintain original speed
				duration = im.info.get("duration", 100) * frame_step
				durations.append(duration)

				# Reduce color palette
				frame = frame.convert("P", palette=Image.ADAPTIVE, colors=colors)
				frames.append(frame)

				# Progress feedback
				progress = int(((i + 1) / total_frames) * 100)
				self.parent.signalProgression.emit(progress)

			frames[0].save(
				output_path,
				save_all=True,
				append_images=frames[1:],
				optimize=True,
				loop=im.info.get("loop", 0),
				duration=durations,
				disposal=2,
			)

			before = os.path.getsize(gif_path) / 1024
			after = os.path.getsize(output_path) / 1024
			print(f"Original: {before:.1f} KB → Optimized: {after:.1f} KB")

			self.parent.signalProgression.emit(100)
			return output_path


# opt = ImageOptimizer(r'C:\Users\Usera\Pictures\bank\pixabay')
# opt.compress()