import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Tubes"]
collection = db["comments"]

# Loop through documents in the collection
for doc in collection.find():
    # Initialize counts for positive, negative, and neutral sentiments
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    # Loop through comments in the document
    for comment_key, comment_value in enumerate(doc.get('comments', [])):
        if 'sentiment' in comment_value:
            sentiment = comment_value['sentiment']

            # Update sentiment count based on the label
            if sentiment == 'positive':
                positive_count += 1
            elif sentiment == 'neutral':
                neutral_count += 1
            elif sentiment == 'negative':
                negative_count += 1

    # Determine the label based on the highest count
    if positive_count >= neutral_count and positive_count >= negative_count:
        label = 'positive'
    elif neutral_count >= positive_count and neutral_count >= negative_count:
        label = 'neutral'
    else:
        label = 'negative'

    # Update the document with the determined label
    collection.update_one(
        {'_id': doc['_id']},
        {'$set': {'label': label}}
    )

    print(f"postId: {doc['postId']}, Positive Count: {positive_count}, Neutral Count: {neutral_count}, Negative Count: {negative_count}, Label: {label}")

print("Data update completed.")