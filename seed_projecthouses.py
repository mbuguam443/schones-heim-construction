#!/usr/bin/env python
"""
Seed project house images into the database.
Reads images from sub-folders (folder name = title) and flat files.
Run: python seed_projecthouses.py
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.core.models import ProjectHouse
from django.core.files import File

BASE = os.path.join('static', 'project-houses')

DESCRIPTIONS = {
    "Residential Home - Karen": "A beautiful 4-bedroom residential home with modern finishes, spacious living areas, and a landscaped garden. Located in the serene Karen neighborhood.",
    "Modern Apartment Block - Westlands": "A modern 12-unit apartment block featuring contemporary design, parking facilities, and proximity to shopping centers in Westlands.",
    "Executive Villa - Runda": "An executive 5-bedroom villa with premium finishes, home automation, swimming pool, and gated compound in the prestigious Runda estate.",
    "Townhouse Complex - Kileleshwa": "A stylish townhouse complex featuring 8 units with shared amenities, children's play area, and 24/7 security in Kileleshwa.",
    "Estate Housing - South B": "An affordable estate housing development featuring quality finishes and modern amenities for young families in South B.",
    "Luxury Penthouse - Kilimani": "A luxury penthouse with panoramic city views, private terrace, modern kitchen, and premium fittings in Kilimani.",
    "Family Home - Lavington": "A spacious family home featuring 4 bedrooms, open-plan living, DSQ, and ample parking in the leafy Lavington neighborhood.",
    "Commercial Building - CBD": "A multi-story commercial building with modern office spaces, backup power, and prime CBD location.",
    "Office Complex - Upper Hill": "A premium office complex featuring flexible floor plans, conference facilities, and ample parking in Upper Hill.",
    "Mixed Use Development - Langata": "A mixed-use development combining retail and residential units with modern architectural design in Langata.",
    "Gated Community - Kitengela": "A secure gated community development featuring 20 family homes with shared amenities in Kitengela.",
    "Beach House - Diani": "A stunning beach house with ocean views, open-plan living, and direct beach access in the coastal Diani area.",
    "Country Home - Naivasha": "A country home getaway featuring rustic-modern design, garden, and scenic views in Naivasha.",
    "Serviced Apartments - Parklands": "Serviced apartments featuring furnished units with kitchenettes, Wi-Fi, and housekeeping in Parklands.",
    "Warehouse - Industrial Area": "A modern warehouse facility with high ceilings, loading docks, and secure premises in the Industrial Area.",
    "School Building - Kasarani": "A purpose-built school building featuring classrooms, laboratories, library, and sports facilities in Kasarani.",
    "Church Complex - Embakasi": "A modern church complex featuring a main auditorium, fellowship halls, and administrative offices in Embakasi.",
    "Medical Center - Eastleigh": "A medical center featuring consultation rooms, treatment areas, pharmacy, and modern medical equipment in Eastleigh.",
    "Shopping Plaza - Thika Road": "A shopping plaza featuring retail spaces, food court, parking, and modern amenities along Thika Road.",
    "Hotel & Resort - Nanyuki": "A hotel and resort development featuring guest rooms, conference facilities, restaurant, and recreational areas in Nanyuki.",
    "Sports Complex - Kasarani": "A sports complex featuring indoor and outdoor facilities, gym, and coaching areas in Kasarani.",
    "Student Hostel - University Area": "A student hostel featuring study rooms, shared kitchens, laundry, and high-speed internet near the university area.",
}

def main():
    print("\n=== Seeding Project Houses ===\n")
    
    if not os.path.exists(BASE):
        print(f"  Directory not found: {BASE}")
        return
    
    count = 0
    order = 0
    
    # Scan sub-folders first (each folder name = title)
    for item in sorted(os.listdir(BASE)):
        folder_path = os.path.join(BASE, item)
        if not os.path.isdir(folder_path):
            continue
        
        title = item
        desc = DESCRIPTIONS.get(title, f"Construction project by Schones Heim Builders - {title}.")
        
        # Get all images in this folder
        images = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        if not images:
            print(f"  No images in folder: {title}")
            continue
        
        for img_file in images:
            order += 1
            img_path = os.path.join(folder_path, img_file)
            
            if ProjectHouse.objects.filter(title=title, pk__in=ProjectHouse.objects.filter(image__endswith=img_file).values('pk')).exists():
                print(f"  Skipping (exists): {title} - {img_file}")
                continue
            
            with open(img_path, 'rb') as f:
                house = ProjectHouse(
                    title=title,
                    description=desc if ProjectHouse.objects.filter(title=title).count() == 0 else '',
                    order=order,
                    is_active=True,
                )
                house.image.save(img_file, File(f), save=True)
                print(f"  Created: {title} [{img_file}]")
                count += 1
    
    # Scan flat files (backward compatibility)
    flat_images = sorted([f for f in os.listdir(BASE) if os.path.isfile(os.path.join(BASE, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    flat_titles = [
        "Residential Home - Karen", "Modern Apartment Block - Westlands",
        "Executive Villa - Runda", "Townhouse Complex - Kileleshwa",
        "Estate Housing - South B", "Luxury Penthouse - Kilimani",
        "Family Home - Lavington", "Commercial Building - CBD",
        "Office Complex - Upper Hill", "Mixed Use Development - Langata",
        "Gated Community - Kitengela", "Beach House - Diani",
        "Country Home - Naivasha", "Serviced Apartments - Parklands",
        "Warehouse - Industrial Area", "School Building - Kasarani",
        "Church Complex - Embakasi", "Medical Center - Eastleigh",
        "Shopping Plaza - Thika Road", "Hotel & Resort - Nanyuki",
        "Sports Complex - Kasarani", "Student Hostel - University Area",
    ]
    
    for i, img_file in enumerate(flat_images):
        title = flat_titles[i] if i < len(flat_titles) else f"Project {i+1}"
        order += 1
        img_path = os.path.join(BASE, img_file)
        
        if ProjectHouse.objects.filter(title=title).exists():
            continue
        
        with open(img_path, 'rb') as f:
            house = ProjectHouse(
                title=title,
                description=DESCRIPTIONS.get(title, f"Construction project by Schones Heim Builders."),
                order=order,
                is_active=True,
            )
            house.image.save(img_file, File(f), save=True)
            print(f"  Created (flat): {title}")
            count += 1
    
    print(f"\n=== Done! Created {count} project houses ===\n")

if __name__ == '__main__':
    main()
