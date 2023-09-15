import boto3
import os
import botocore.config
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION,
                  config=botocore.config.Config(signature_version='s3v4'))

def upload_file_to_s3(file, bucket, object_name):
    try:
        s3.upload_fileobj(file, bucket, object_name or file.filename)
        return True, "File uploaded."
    except Exception as e:
        return False, str(e)
    
def generate_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        return False, str(e)
    return True, response
