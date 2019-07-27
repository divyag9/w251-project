import boto3
from botocore.exceptions import NoCredentialsError
from aws_credentials import ACCESS_KEY, SECRET_KEY

FILENAME = 'strawberries.csv'
BUCKET = 'w251'
CLIENT = 's3'


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client(CLIENT, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print("There was an exception: {}".format(repr(e)))
        raise


uploaded = upload_to_aws(FILENAME, BUCKET, FILENAME)

print("Status: {}".format(uploaded))
