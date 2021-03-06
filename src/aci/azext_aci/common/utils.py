def singleton(myclass):
    instance = [None]
    
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = myclass(*args, **kwargs)
        return instance[0]
    return wrapper 

def time_now_as_string():
    from datetime import datetime
    now = datetime.utcnow().strftime('%H%M%S')
    return now
