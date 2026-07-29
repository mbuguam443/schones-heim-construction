with open('apps/core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("context_object_name = 'houses'", "context_object_name = 'projecthouses'")
with open('apps/core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
