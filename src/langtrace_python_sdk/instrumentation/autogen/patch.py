def patch_autogen(name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        print("Tracing", instance.__class__.__name__)
        return wrapped(*args, **kwargs)

    return traced_method
