from imgurpython import ImgurClient
import boto3
from flask import Flask, jsonify, url_for
import requests
from cStringIO import StringIO
import os

imgur_client_id = os.environ['IMGUR_CLIENT_ID']
imgur_client_secret = os.environ['IMGUR_CLIENT_SECRET']

dynamodb_table = 'zappa-imgur-2'
s3_bucket = 'zappa-imgur'
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
        if not image.is_album and image.animated:
            return image


@app.route("/", methods=['GET'])
def get_pic():
    image = random_image()
    all_values = dict((k, v) for k, v in image.__dict__.iteritems() if v)
    r = table.put_item(Item=all_values)
    r = requests.get(image.link)
    key_name = image.link.rsplit('/')[-1]
    s3c = boto3.client('s3')
    fake_handle = StringIO(r.content)
    s3c.put_object(Bucket=s3_bucket,
                   Key=key_name,
                   Body=fake_handle.read(),
                   ACL='public-read',
                   ContentType=r.headers['Content-Type'])
    data = {
        's3_link': s3_link.format(bucket=s3_bucket, key=key_name),
        'metadata': url_for('get_metadata', image_id=image.id, _external=True)}
    return jsonify(data), 200


@app.route('/metadata/id/<image_id>', methods=['GET'])
def get_metadata(image_id):
    r = table.get_item(Key={'id': image_id})
    return jsonify(r['Item']), 200


if __name__ == '__main__':
    app.debug = True
    app.run()
