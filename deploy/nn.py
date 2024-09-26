# In nn.py (your enhancement module)
import cv2
from PIL import Image, ImageEnhance
import fingerprint_enhancer  # Assuming this is your fingerprint enhancement library
import os


def enhancer(image_path):
    # Process the image without using Tkinter or any GUI elements
    try:
        # Step 1: Read the input fingerprint image in grayscale
        img = cv2.imread(image_path, 0)
        if img is None:
            raise ValueError(f"Could not open or find the image at {image_path}.")

        # Step 2: Enhance the fingerprint image
        out = fingerprint_enhancer.enhance_Fingerprint(img)

        # Step 3: Apply thresholding to convert the background to white and fingerprint to black
        _, out_thresh = cv2.threshold(out, 127, 255, cv2.THRESH_BINARY_INV)

        # Step 4: Save the thresholded image temporarily
        output_fp_path = f'thresholded_{os.path.basename(image_path)}'
        cv2.imwrite(output_fp_path, out_thresh)

        # Step 5: Enhance the image with contrast using PIL
        image = Image.open(output_fp_path)
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(3)  # Increase contrast

        # Step 6: Create a white background and paste the enhanced image
        width, height = enhanced_image.size
        white_background = Image.new('RGB', (width, height), (255, 255, 255))
        enhanced_image = enhanced_image.convert("L")
        white_background.paste(enhanced_image, (0, 0))

        # Save the final enhanced image to a specific folder
        final_output_path = f'final_enhanced_{os.path.basename(image_path)}'
        white_background.save(final_output_path)

        return final_output_path  # Return the path of the enhanced image

    except Exception as e:
        raise RuntimeError(f"Error enhancing image: {e}")
