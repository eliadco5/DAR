from PIL import ImageChops, ImageStat

def images_are_similar(img1, img2, tolerance=10):
    """
    Compare two PIL images. Return True if they are similar within the given tolerance.
    Tolerance is the maximum average pixel difference allowed.
    """
    if img1.size != img2.size:
        return False
    diff = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff)
    # Average difference per channel
    mean_diff = sum(stat.mean) / len(stat.mean)
    return mean_diff <= tolerance 