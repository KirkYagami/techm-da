import os
from google.cloud import pubsub_v1

## pip install google-cloud-pubsub
import json
from google.auth import jwt


service_account_info = json.load(open(r"river-yew-500209-t8-c024f2edbbf6.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"
credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)
subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
# The same for the publisher, except that the "audience" claim needs to be adjusted
publisher_audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
credentials_pub = credentials.with_claims(audience=publisher_audience)
publisher = pubsub_v1.PublisherClient(credentials=credentials_pub)

PROJECT_ID = 'river-yew-500209-t8'
TOPIC = 'topic0073'
topic_name = f'projects/{PROJECT_ID}/topics/{TOPIC}'
# publisher.create_topic(name=topic_name)
future = publisher.publish(topic_name, b'My second message!', spam='milk')
future.result()
print("done")
 