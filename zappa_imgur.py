from imgurpython import ImgurClient
import boto3
from flask import Flask, jsonify, url_for
import requests
from cStringIO import StringIO

imgur_client_id = ''
imgur_client_secret = ''

dynamodb_table = ''
s3_bucket = ''
region = 'ap-southeast-1'

dynamodb = boto3.resource('dynamodb', region)
client = ImgurClient(imgur_client_id, imgur_client_secret)
table = dynamodb.Table(dynamodb_table)

s3_link = "https://{bucket}.s3.amazonaws.com/{key}"

app = Flask(__name__)

def random_image():
    """ returns a random animated image from imgur """
    gallery = client.gallery_random(page=0)
    for image in gallery:
        if not image.is_album and image.is_animated:
            return image

@app.route("/", methods=['GET'])
def get_pic():
    image = random_image()
    
