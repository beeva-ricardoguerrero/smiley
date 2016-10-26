from image_operation import ImageOperator

class Filters(ImageOperator):

	def nashville(self, img, hue = 1, saturation = 1.5, contrast = 1.2, brightness = -20):
		img = self.hue_saturation(img, hue, saturation)
		img = self.brightness_contrast(img, contrast, brightness)
		return img


	def lomo(self, img, r_channel = 1.33, g_channel = 1.33):
		img = self.channel_enhance(img, "R", r_channel)
		img = self.channel_enhance(img, "G", g_channel)
		return img

	def gotham(self, img, hue = 1.2, saturation = 0.4, contrast = 1, brightness = -10):
		img = self.hue_saturation(img, hue, saturation)
		img = self.brightness_contrast(img, contrast, brightness)
		return img

	def toaster(self, img, hue, saturation, contrast, brightness):
		pass

	def kelvin(self, img, hue, saturation, contrast, brightness):
		pass

	def hist_match(self, img, img_match):
		img = self.histogram_matching(img, img_match)
		return img
