# fix it
with open('apps/core/views.py', 'r') as f:
    content = f.read()
content = content.replace("context_object_name = 'houses'", "context_object_name = 'projecthouses'")
with open('apps/core/views.py', 'w') as f:
    f.write(content)
print('Fixed')
