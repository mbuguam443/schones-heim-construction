#!/usr/bin/env python
"""
Seed project house images into the database.
Scans sub-folders — folder name becomes the title, all images inside share it.
Run: python seed_projecthouses.py
"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.core.models import ProjectHouse
from django.core.files import File

BASE = os.path.join('media', 'project-houses')

def main():
    print("\n=== Seeding Project Houses ===\n")
    if not os.path.exists(BASE):
        print(f"  Not found: {BASE}"); return
    count = 0; order = 0
    for item in sorted(os.listdir(BASE)):
        fp = os.path.join(BASE, item)
        if not os.path.isdir(fp): continue
        title = item
        images = sorted([f for f in os.listdir(fp) if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
        for img_file in images:
            path = os.path.join(fp, img_file)
            if ProjectHouse.objects.filter(image__endswith=img_file).exists():
                continue
            order += 1
            with open(path, 'rb') as f:
                ph = ProjectHouse(title=title,
                    description="", order=order, is_active=True)
                ph.image.save(img_file, File(f), save=True)
                print(f"  Created: {title} [{img_file}]")
                count += 1
    print(f"\n=== Done! Created {count} project houses ===\n")

if __name__ == '__main__':
    main()
