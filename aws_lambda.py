import json
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event=None, context=None):
    aws_region = "us-east-1"

    subject = "Please confirm your email address"
    sender = "no_reply@prod.yiqingjackiehuang.me"

    if event is not None:
        message = event['Records'][0]['Sns']['Message']
        message = json.loads(message)
        print(message)
        recipient = message["email"]
        token = message["token"]
    else:
        recipient = "yiqing.jackie.huang@gmail.com"
        from uuid import uuid4
        token = uuid4()

    table = boto3.resource('dynamodb', region_name=aws_region).Table('csye6225')
    response = table.get_item(Key={"user_id": recipient})
    if "Item" in response.keys():
        item = response['Item']
        if item["sendStatus"] == "sent":
            return
    else:
        return

    destination = {
        'ToAddresses': [
            recipient,
        ]
    }

    link = f'http://prod.yiqingjackiehuang.me/v1/verifyUserEmail?email={recipient}&token={token}'
    body = f'Hi {recipient},\n\n Thanks for creating your account! Before we get started, we need to verify your email to make sure we got it right. ' \
           f'All you need to do is to click the link below. Please notice that the link will be expired in 5 minutes.\n\n' \
           f'\t\t {link} \n\neikcaj Team'
    print(body)
    charset = "UTF-8"

    client = boto3.client('ses', region_name=aws_region)

    try:
        response = client.send_email(
            Destination=destination,
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender
        )

        item["sendStatus"] = "sent"
        table.put_item(Item=item)


    # Display an error if anything goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:")
        print(response['MessageId'])
        print(recipient)


if __name__ == '__main__':
    lambda_handler()
