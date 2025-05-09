from PIL import ImageChops, ImageStat
import logging
import os

# Configure logging
logger = logging.getLogger("ImageCompare")

def images_are_similar(img1, img2, tolerance=10, force_fail=False):
    """
    Compare two PIL images. Return True if they are similar within the given tolerance.
    Tolerance is the maximum average pixel difference allowed.
    
    Args:
        img1: First PIL image (reference)
        img2: Second PIL image (test)
        tolerance: Maximum allowed pixel difference (0-255)
        force_fail: If True, always returns False (for testing failure cases)
    
    Returns:
        bool: True if images are similar, False otherwise
    """
    # For testing purposes, allow forcing a failure
    if force_fail:
        logger.warning("Force fail flag is set - check will fail regardless of image similarity")
        return False
        
    # Check if debug mode is enabled via environment variable
    debug_mode = os.environ.get('DAR_DEBUG_IMAGE_COMPARE', '0') == '1'
    
    if img1.size != img2.size:
        logger.warning(f"Image size mismatch: {img1.size} vs {img2.size}")
        return False
        
    # Convert images to same mode if they differ
    if img1.mode != img2.mode:
        logger.info(f"Converting image modes to match: {img1.mode} vs {img2.mode}")
        if img1.mode == 'RGBA' and img2.mode == 'RGB':
            img1 = img1.convert('RGB')
        elif img2.mode == 'RGBA' and img1.mode == 'RGB':
            img2 = img2.convert('RGB')
    
    diff = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff)
    
    # Average difference per channel
    mean_diff = sum(stat.mean) / len(stat.mean)
    logger.info(f"Image comparison result: mean_diff={mean_diff:.2f}, tolerance={tolerance}")
    
    # Detailed channel differences for debugging
    channel_diffs = [f"Channel {i}: {val:.2f}" for i, val in enumerate(stat.mean)]
    logger.info(f"Channel differences: {', '.join(channel_diffs)}")
    
    # Save debug images if needed
    if debug_mode:
        debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'debug_images')
        os.makedirs(debug_dir, exist_ok=True)
        img1.save(os.path.join(debug_dir, 'ref_image.png'))
        img2.save(os.path.join(debug_dir, 'test_image.png'))
        diff.save(os.path.join(debug_dir, 'diff_image.png'))
        logger.info(f"Debug images saved to {debug_dir}")
    
    return mean_diff <= tolerance 