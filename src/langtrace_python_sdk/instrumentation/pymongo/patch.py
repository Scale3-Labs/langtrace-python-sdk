def generic_patch(version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        wrapped(*args, **kwargs)

    return traced_method
