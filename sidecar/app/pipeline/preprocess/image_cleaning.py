"""Image cleaning and preprocessing utilities."""

from typing import Tuple
import math

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.ndimage import uniform_filter, median_filter


class ImageCleaner:
    """Cleans and preprocesses images for OCR."""

    def __init__(self, deskew: bool = True, denoise: bool = True):
        """
        Initialize the image cleaner.

        Args:
            deskew: Whether to correct skew
            denoise: Whether to apply denoising
        """
        self.deskew = deskew
        self.denoise = denoise

    def process(self, image: Image.Image) -> Image.Image:
        """
        Process an image through cleaning pipeline.

        Args:
            image: Input PIL Image

        Returns:
            Cleaned PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            img_array = self._to_grayscale(img_array)

        # Apply denoising
        if self.denoise:
            img_array = self._denoise(img_array)

        # Apply deskewing
        if self.deskew:
            img_array = self._deskew(img_array)

        return Image.fromarray(img_array)

    def _to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Convert RGB image to grayscale."""
        # Simple weighted average
        return np.dot(img[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)

    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """Apply median filter denoising.

        Uses scipy's median_filter which is effective for salt-and-pepper noise
        commonly found in scanned documents.
        """
        # Apply median filter with 3x3 kernel
        denoised = median_filter(img, size=3)
        return denoised.astype(np.uint8)

    def _deskew(self, img: np.ndarray) -> np.ndarray:
        """Correct image skew using projection profile analysis.

        Detects skew angle by analyzing horizontal projection profiles
        at different rotation angles and finding the angle that maximizes
        the variance of the profile (sharpest text lines).
        """
        # Binarize for skew detection
        threshold = np.mean(img)
        binary = img < threshold

        # Try angles from -10 to 10 degrees
        best_angle = 0
        best_score = 0

        for angle in np.linspace(-10, 10, 41):  # 0.5 degree steps
            rotated = ndimage.rotate(binary, angle, reshape=False, order=0)
            # Calculate horizontal projection profile
            profile = np.sum(rotated, axis=1)
            # Score is the variance of the profile
            score = np.var(profile)
            if score > best_score:
                best_score = score
                best_angle = angle

        # Only correct if skew is significant (> 0.5 degrees)
        if abs(best_angle) > 0.5:
            return ndimage.rotate(img, best_angle, reshape=False, order=1, cval=255).astype(np.uint8)
        return img

    def binarize(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        """
        Convert image to binary (black and white).

        Args:
            image: Input image
            threshold: Binarization threshold

        Returns:
            Binary image
        """
        gray = image.convert("L")
        return gray.point(lambda x: 255 if x > threshold else 0, mode="1")
