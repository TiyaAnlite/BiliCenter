from bilicenter_middleware.event2job import accept_job


def main_route(event, context):
    return accept_job(event)



