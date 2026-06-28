# Cloud Pub/Sub Basics using gcloud

## Step-01: Introduction
- gcloud: Create Pub/Sub Topic
- gcloud: Create Pub/Sub Subscription
- gcloud: Publish Messages
- gcloud: Pull Messages in Subscription and Acknowledge

## Step-02: gcloud: Create Pub/Sub Topic, Subscription
```bash
# Set Project
gcloud config set project PROJECT_ID
gcloud config set project nickk-498807

# Create Cloud Pub/Sub Topic
gcloud pubsub topics create mytopic2

# Create Cloud Pub/Sub Subscription
gcloud pubsub subscriptions create mysubscription2 --topic mytopic2

# Review Topic and Subscription in Web Console
1. Go to Cloud Pub/Sub -> mytopic2
2. Go to Cloud Pub/Sub -> mysubscription2
```
## Step-03: gcloud: Publish Messages
```bash
# Publish Message-1
gcloud pubsub topics publish projects/nickk-498807/topics/mytopic2 --message="hello kirk 1" 
gcloud pubsub topics publish projects/nickk-498807/topics/mytopic2 --message="hello kirk 2" 
gcloud pubsub topics publish projects/nickk-498807/topics/mytopic2 --message="hello kirk 3" 



# Pull all messages from subscription: mysubscription3
gcloud pubsub subscriptions pull mysubscription2
gcloud pubsub subscriptions pull mysubscription2 —-auto-ack
```


