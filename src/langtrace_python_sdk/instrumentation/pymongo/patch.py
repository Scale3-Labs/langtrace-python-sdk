def generic_patch(version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        print("kwargs", kwargs)
        print("args", args)
        print("instance", instance)
        wrapped(*args, **kwargs)

    return traced_method
