'''
credentials_files.py: mapping of services to credentials files
'''

CREDENTIALS_FILES = {
    'amazon'             : 'amazon_credentials.json',
    'amazon-rekognition' : 'amazon_credentials.json',
    'amazon-textract'    : 'amazon_credentials.json',
    'google'             : 'google_credentials.json',
    'microsoft'          : 'microsoft_credentials.json',
}

def credentials_filename(service):
    assert service in CREDENTIALS_FILES
    return CREDENTIALS_FILES[service]
