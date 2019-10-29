def hello(event, context):
    print(event)
    return {
        "message": "A<Go Serverless v1.0! Your function executed successfully! Yehu",
        "event": event
    }
