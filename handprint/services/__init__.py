from .amazon import AmazonRekognitionTR, AmazonTextractTR
from .google import GoogleTR
from .microsoft import MicrosoftTR

ACCEPTED_FORMATS = ('.jpg', '.jpeg', '.jp2', '.png', '.gif', '.bmp',
                    '.tif', '.tiff')

KNOWN_SERVICES = {
    'amazon-rekognition': AmazonRekognitionTR,
    'amazon-textract': AmazonTextractTR,
    'google': GoogleTR,
    'microsoft': MicrosoftTR,
}

# Save this list to avoid recreating it all the time.
SERVICES_LIST = sorted(KNOWN_SERVICES.keys())

def services_list():
    return SERVICES_LIST
