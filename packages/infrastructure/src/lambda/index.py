import os

def handler(event, context):
    print("Hello World")

    print(os.environ.get('webdavDomainName'))
    print(os.environ.get('webdavUsername'))
    print(os.environ.get('webdavPassword'))
    print(os.environ.get('webdavUploadPath'))
    print(os.environ.get('instagramUsername'))
    print(os.environ.get('instagramPassword'))
    print(os.environ.get('sanityTest'))
