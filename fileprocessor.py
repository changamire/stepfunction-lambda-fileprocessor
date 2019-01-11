import boto3
import json
import os
import logging
import logging.config
from botocore.exceptions import ClientError

s3 = boto3.client('s3')


def load_log_config():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    return root


def process_file(bucket, key, start_byte, end_byte):
    logger.info('Processing file, Bucket: ' + bucket + ', Key: ' + key)
    logger.info('bytes={}-{}'.format(start_byte, end_byte))

    chunk = s3.get_object(Bucket=bucket, Key=key,
                          Range='bytes={}-{}'.format(start_byte, end_byte))

    last_newline = 0
    newline = '\n'.encode()

    read_chunk = chunk['Body'].read()
    last_newline = read_chunk.rfind(newline)
    result = read_chunk[0:last_newline+1].decode('utf-8')

    for line in result.splitlines():
        process_line(line)

    result = {}
    result['start_byte'] = start_byte + last_newline + \
        1  # add a byte to skip the newline
    return result


def has_file_contents(file_like_obj):
    '''Checks if a file like object has anything in it'''
    file_like_obj.seek(0, os.SEEK_END)
    size = file_like_obj.tell()
    if (size > 0):
        return True
    return False


def process_line(line):
    '''Do something useful here'''
    print(line)


def get_filesize(bucket, key):
    try:
        obj = s3.head_object(Bucket=bucket, Key=key)
        return obj['ContentLength']
    except ClientError as exc:
        if exc.response['Error']['Code'] != '404':
            raise


def is_final_iteration(next_start_byte, file_size, chunk_size):
    '''check if this is the final chunk of the file to process'''
    if ((next_start_byte + chunk_size) >= file_size):
        return True
    else:
        return False


# Load logging config and create logger
logger = load_log_config()


def handler(event, context):
    logger.info('Received event: ' + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    file_size = get_filesize(bucket, key)
    logger.info('File size ' + str(file_size))

    chunk_size = int(os.environ['CHUNK_SIZE'])
    logger.info('Chunk size ' + str(chunk_size))

    start_byte = 0

    if ('fileprocessor' not in event):
        # First invocation
        end_byte = chunk_size

        if (end_byte > file_size):
            end_byte = file_size
        process_file_result = process_file(
            bucket, key, start_byte, end_byte)
        next_start_byte = process_file_result['start_byte']

        final_iteration = is_final_iteration(start_byte, file_size, chunk_size)
        event['fileprocessor'] = {
            'results': {
                'startByte': next_start_byte,
                'finished': final_iteration
            }
        }
    else:
        start_byte = event['fileprocessor']['results']['startByte']
        end_byte = start_byte + chunk_size

        if (end_byte > file_size):
            end_byte = file_size

        final_iteration = is_final_iteration(
            start_byte, file_size, chunk_size)

        process_file_result = process_file(
            bucket, key, start_byte, end_byte)
        next_start_byte = process_file_result['start_byte']

        event['fileprocessor']['results'] = {
            'startByte': next_start_byte, 'finished': final_iteration}

    logger.info('Returning event: ' + json.dumps(event, indent=2))
    return event
