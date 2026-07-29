#!/usr/bin/env python
"""
Seed project house images into the database.
Scans sub-folders (folder name = title) AND flat files for backward compatibility.
Run: python seed_projecthouses.py
"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.core.models import ProjectHouse
from django.core.files import File

BASE = os.path.join('static', 'project-houses')

DESCRIPTIONS = {
    "Residential Home - Karen": "A beautiful 4-bedroom residential home with modern finishes and a landscaped garden in Karen.",
    "Modern Apartment Block - Westlands": "A modern 12-unit apartment block with contemporary design in Westlands.",
    "Executive Villa - Runda": "An executive 5-bedroom villa with premium finishes and swimming pool in Runda.",
    "Townhouse Complex - Kileleshwa": "A stylish townhouse complex with shared amenities in Kileleshwa.",
    "Estate Housing - South B": "An affordable estate housing development in South B.",
    "Luxury Penthouse - Kilimani": "A luxury penthouse with panoramic city views in Kilimani.",
    "Family Home - Lavington": "A spacious family home in the leafy Lavington neighborhood.",
    "Commercial Building - CBD": "A multi-story commercial building in the CBD.",
    "Office Complex - Upper Hill": "A premium office complex in Upper Hill.",
    "Mixed Use Development - Langata": "A mixed-use development in Langata.",
    "Gated Community - Kitengela": "A secure gated community development in Kitengela.",
    "Beach House - Diani": "A stunning beach house with ocean views in Diani.",
    "Country Home - Naivasha": "A country home with scenic views in Naivasha.",
    "Serviced Apartments - Parklands": "Serviced apartments in Parklands.",
    "Warehouse - Industrial Area": "A modern warehouse facility in the Industrial Area.",
    "School Building - Kasarani": "A purpose-built school building in Kasarani.",
    "Church Complex - Embakasi": "A modern church complex in Embakasi.",
    "Medical Center - Eastleigh": "A medical center in Eastleigh.",
    "Shopping Plaza - Thika Road": "A shopping plaza along Thika Road.",
    "Hotel & Resort - Nanyuki": "A hotel and resort in Nanyuki.",
    "Sports Complex - Kasarani": "A sports complex in Kasarani.",
    "Student Hostel - University Area": "A student hostel near the university area.",
}

def main():
    print("\n=== Seeding Project Houses ===\n")
    if not os.path.exists(BASE):
        print(f"  Not found: {BASE}"); return
    count = 0; order = 0

    # Scan sub-folders (folder name = title)
    for item in sorted(os.listdir(BASE)):
        fp = os.path.join(BASE, item)
        if not os.path.isdir(fp): continue
        title = item
        images = sorted([f for f in os.listdir(fp) if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
        for img_file in images:
            order += 1
            path = os.path.join(fp, img_file)
            if ProjectHouse.objects.filter(title=title).exists():
                continue
            with open(path, 'rb') as f:
                ph = ProjectHouse(title=title,
                    description=ProjectHouse.objects.filter(title=title).first() and '' or DESCRIPTIONS.get(title,''),
                    order=order, is_active=True)
                ph.image.save(img_file, File(f), save=True)
                print(f"  Created: {title}")
                count += 1

    # Scan flat files
    flat = sorted([f for f in os.listdir(BASE) if os.path.isfile(os.path.join(BASE,f)) and f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
    flat_titles = [
        "Residential Home - Karen","Modern Apartment Block - Westlands",
        "Executive Villa - Runda","Townhouse Complex - Kileleshwa",
        "Estate Housing - South B","Luxury Penthouse - Kilimani",
        "Family Home - Lavington","Commercial Building - CBD",
        "Office Complex - Upper Hill","Mixed Use Development - Langata",
        "Gated Community - Kitengela","Beach House - Diani",
        "Country Home - Naivasha","Serviced Apartments - Parklands",
        "Warehouse - Industrial Area","School Building - Kasarani",
        "Church Complex - Embakasi","Medical Center - Eastleigh",
        "Shopping Plaza - Thika Road","Hotel & Resort - Nanyuki",
        "Sports Complex - Kasarani","Student Hostel - University Area",
    ]
    for i, img_file in enumerate(flat):
        order += 1
        title = flat_titles[i] if i < len(flat_titles) else f"Project {i+1}"
        path = os.path.join(BASE, img_file)
        if ProjectHouse.objects.filter(title=title).exists():
            continue
        with open(path, 'rb') as f:
            ph = ProjectHouse(title=title, description=DESCRIPTIONS.get(title,''), order=order, is_active=True)
            ph.image.save(img_file, File(f), save=True)
            print(f"  Created: {title}")
            count += 1

    print(f"\n=== Done! Created {count} project houses ===\n")

if __name__ == '__main__':
    main()
