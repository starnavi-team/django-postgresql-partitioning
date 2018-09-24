def partitioning(config):
    def decorator(model):
        model.partitioning = config
        return model

    return decorator
