def summarize(*args, **kwargs):
    total = sum(args)
    details = ", ".join(f"{k}: {v}" for k, v in kwargs.items())
    return total, details
result = summarize(10, 20, 30, name="Alice", role="Admin")
print(result)