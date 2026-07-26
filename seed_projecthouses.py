#!/usr/bin/env python
"""
Seed existing project house images into the database.
Run once after migration: python seed_projecthouses.py
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.core.models import ProjectHouse
from django.core.files import File

IMAGES_DIR = os.path.join('static', 'project-houses')

TITLES = [
    "Residential Home - Karen",
    "Modern Apartment Block - Westlands",
    "Executive Villa - Runda",
    "Townhouse Complex - Kileleshwa",
    "Estate Housing - South B",
    "Luxury Penthouse - Kilimani",
    "Family Home - Lavington",
    "Commercial Building - CBD",
    "Office Complex - Upper Hill",
    "Mixed Use Development - Langata",
    "Gated Community - Kitengela",
    "Beach House - Diani",
    "Country Home - Naivasha",
    "Serviced Apartments - Parklands",
    "Warehouse - Industrial Area",
    "School Building - Kasarani",
    "Church Complex - Embakasi",
    "Medical Center - Eastleigh",
    "Shopping Plaza - Thika Road",
    "Hotel & Resort - Nanyuki",
    "Sports Complex - Kasarani",
    "Student Hostel - University Area",
]

DESCRIPTIONS = [
    "A beautiful 4-bedroom residential home with modern finishes, spacious living areas, and a landscaped garden. Located in the serene Karen neighborhood.",
    "A modern 12-unit apartment block featuring contemporary design, parking facilities, and proximity to shopping centers in Westlands.",
    "An executive 5-bedroom villa with premium finishes, home automation, swimming pool, and gated compound in the prestigious Runda estate.",
    "A stylish townhouse complex featuring 8 units with shared amenities, children's play area, and 24/7 security in Kileleshwa.",
    "An affordable estate housing development featuring quality finishes and modern amenities for young families in South B.",
    "A luxury penthouse with panoramic city views, private terrace, modern kitchen, and premium fittings in Kilimani.",
    "A spacious family home featuring 4 bedrooms, open-plan living, DSQ, and ample parking in the leafy Lavington neighborhood.",
    "A multi-story commercial building with modern office spaces, backup power, and prime CBD location.",
    "A premium office complex featuring flexible floor plates, conference facilities, and ample parking in Upper Hill.",
    "A mixed-use development combining retail and residential units with modern architectural design in Langata.",
    "A secure gated community development featuring 20 family homes with shared amenities in Kitengela.",
    "A stunning beach house with ocean views, open-plan living, and direct beach access in the coastal Diani area.",
    "A country home getaway featuring rustic-modern design, garden, and scenic views in Naivasha.",
    "Serviced apartments featuring furnished units with kitchenettes, Wi-Fi, and housekeeping in Parklands.",
    "A modern warehouse facility with high ceilings, loading docks, and secure premises in the Industrial Area.",
    "A purpose-built school building featuring classrooms, laboratories, library, and sports facilities in Kasarani.",
    "A modern church complex featuring a main auditorium, fellowship halls, and administrative offices in Embakasi.",
    "A medical center featuring consultation rooms, treatment areas, pharmacy, and modern medical equipment in Eastleigh.",
    "A shopping plaza featuring retail spaces, food court, parking, and modern amenities along Thika Road.",
    "A hotel and resort development featuring guest rooms, conference facilities, restaurant, and recreational areas in Nanyuki.",
    "A sports complex featuring indoor and outdoor facilities, gym, and coaching areas in Kasarani.",
    "A student hostel featuring study rooms, shared kitchens, laundry, and high-speed internet near the university area.",
]

def main():
    print("\n=== Seeding Project Houses ===\n")
    
    images = sorted([f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    
    count = 0
    for i, img_file in enumerate(images):
        title = TITLES[i] if i < len(TITLES) else f"Project House {i+1}"
        desc = DESCRIPTIONS[i] if i < len(DESCRIPTIONS) else f"Construction project by Schones Heim Builders."
        
        img_path = os.path.join(IMAGES_DIR, img_file)
        
        if ProjectHouse.objects.filter(title=title).exists():
            print(f"  Skipping (exists): {title}")
            continue
        
        with open(img_path, 'rb') as f:
            house = ProjectHouse(
                title=title,
                description=desc,
                order=i+1,
                is_active=True,
            )
            house.image.save(img_file, File(f), save=True)
            print(f"  Created: {title}")
            count += 1
    
    print(f"\n=== Done! Created {count} project houses ===\n")

if __name__ == '__main__':
    main()
