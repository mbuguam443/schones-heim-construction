import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from random import randint, choice, uniform

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.clients.models import Client
from apps.projects.models import Project, ProjectAssignment
from apps.employees.models import Employee, Attendance
from apps.inventory.models import Material, StockTransaction
from apps.equipment.models import Equipment, EquipmentUsageLog
from apps.quotations.models import Quotation, QuotationItem
from apps.site_reports.models import DailySiteReport
from apps.documents.models import DocumentCategory, Document
from apps.core.models import CompanySettings, Notification

User = get_user_model()

def create_company_settings():
    settings, _ = CompanySettings.objects.get_or_create(
        pk=1,
        defaults={
            'company_name': 'SCHONES HEIM BUILDERS',
            'address': 'Nairobi, Kenya',
            'phone': '+254 700 000 000',
            'email': 'info@schonesheim.co.ke',
            'kra_pin': 'P051234567Z',
            'mpesa_number': '0797770539',
            'bank_name': 'NCBA Bank',
            'bank_account': '1006092731',
        }
    )
    print('Company settings created.')
    return settings

def create_users():
    users_data = [
        {'username': 'admin', 'password': 'Admin123!', 'role': User.Role.ADMIN, 'first_name': 'System', 'last_name': 'Admin', 'phone': '+254700000001'},
        {'username': 'pm', 'password': 'Pm123!', 'role': User.Role.PROJECT_MANAGER, 'first_name': 'John', 'last_name': 'Mbugua', 'phone': '+254700000002'},
        {'username': 'accountant', 'password': 'Acc123!', 'role': User.Role.ACCOUNTANT, 'first_name': 'Jane', 'last_name': 'Wanjiku', 'phone': '+254700000003'},
        {'username': 'supervisor', 'password': 'Sup123!', 'role': User.Role.SITE_SUPERVISOR, 'first_name': 'Peter', 'last_name': 'Kamau', 'phone': '+254700000004'},
        {'username': 'client1', 'password': 'Client123!', 'role': User.Role.CLIENT, 'first_name': 'Mary', 'last_name': 'Njoki', 'phone': '+254700000005', 'email': 'mary@njokiproperties.com'},
        {'username': 'client2', 'password': 'Client123!', 'role': User.Role.CLIENT, 'first_name': 'Grace', 'last_name': 'Wambui', 'phone': '+254700000008', 'email': 'grace@gracehomes.com'},
        {'username': 'client3', 'password': 'Client123!', 'role': User.Role.CLIENT, 'first_name': 'Peter', 'last_name': 'Kamau', 'phone': '+254700000009', 'email': 'peter@kamauholdings.com'},
        {'username': 'client4', 'password': 'Client123!', 'role': User.Role.CLIENT, 'first_name': 'Faith', 'last_name': 'Nyambura', 'phone': '+254700000010', 'email': 'faith@nyamburaent.com'},
        {'username': 'client5', 'password': 'Client123!', 'role': User.Role.CLIENT, 'first_name': 'Samuel', 'last_name': 'Ochieng', 'phone': '+254700000011', 'email': 'sam@ochiengrealty.com'},
        {'username': 'storekeeper', 'password': 'Store123!', 'role': User.Role.STORE_KEEPER, 'first_name': 'David', 'last_name': 'Mwangi', 'phone': '+254700000012', 'email': 'david@schonesheim.co.ke'},
        {'username': 'employee1', 'password': 'Emp123!', 'role': User.Role.EMPLOYEE, 'first_name': 'James', 'last_name': 'Ochieng', 'phone': '+254700000006'},
        {'username': 'employee2', 'password': 'Emp123!', 'role': User.Role.EMPLOYEE, 'first_name': 'Sarah', 'last_name': 'Akinyi', 'phone': '+254700000007'},
    ]
    created_users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': data['role'],
                'phone': data['phone'],
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
        created_users.append(user)
        print(f"  User '{data['username']}' ({data['role']}): {'created' if created else 'already exists'}")
    return created_users

def create_clients():
    clients_data = [
        {'full_name': 'Mary Njoki', 'company_name': 'Njoki Properties Ltd', 'email': 'mary@njokiproperties.com', 'phone': '+254711000001', 'address': 'Nairobi', 'kra_pin': 'P123456789A', 'username': 'client1'},
        {'full_name': 'David Kimani', 'company_name': 'Kimani Enterprises', 'email': 'david@kimani.com', 'phone': '+254711000002', 'address': 'Mombasa', 'kra_pin': 'P987654321B'},
        {'full_name': 'Grace Wambui', 'company_name': 'Grace Homes Ltd', 'email': 'grace@gracehomes.com', 'phone': '+254711000003', 'address': 'Nakuru', 'kra_pin': 'P456789123C', 'username': 'client2'},
        {'full_name': 'Peter Kamau', 'company_name': 'Kamau Holdings', 'email': 'peter@kamauholdings.com', 'phone': '+254711000004', 'address': 'Nairobi', 'kra_pin': 'P111111111A', 'username': 'client3'},
        {'full_name': 'Faith Nyambura', 'company_name': 'Nyambura Enterprises', 'email': 'faith@nyamburaent.com', 'phone': '+254711000005', 'address': 'Nakuru', 'kra_pin': 'P222222222B', 'username': 'client4'},
        {'full_name': 'Samuel Ochieng', 'company_name': 'Ochieng Realty', 'email': 'sam@ochiengrealty.com', 'phone': '+254711000006', 'address': 'Kisumu', 'kra_pin': 'P333333333C', 'username': 'client5'},
    ]
    admin = User.objects.filter(role=User.Role.ADMIN).first()
    created = []
    for data in clients_data:
        client, _ = Client.objects.get_or_create(
            email=data['email'],
            defaults={
                'full_name': data['full_name'],
                'company_name': data['company_name'],
                'phone': data['phone'],
                'address': data['address'],
                'kra_pin': data['kra_pin'],
                'created_by': admin,
            }
        )
        # Link client to user if username specified
        username = data.get('username')
        if username:
            user = User.objects.filter(username=username).first()
            if user:
                client.user = user
                client.save(update_fields=['user'])
        created.append(client)
        print(f"  Client '{data['full_name']}' created.")
    return created

def create_projects(clients):
    admin = User.objects.filter(role=User.Role.ADMIN).first()
    pm = User.objects.filter(role=User.Role.PROJECT_MANAGER).first()
    projects_data = [
        {'name': 'Green Valley Estate', 'client': clients[0], 'location': 'Karen, Nairobi', 'budget': 50000000, 'status': Project.Status.ONGOING, 'progress': 45},
        {'name': 'Ocean View Apartments', 'client': clients[1], 'location': 'Nyali, Mombasa', 'budget': 35000000, 'status': Project.Status.ONGOING, 'progress': 20},
        {'name': 'Highland Mall Construction', 'client': clients[0], 'location': 'Nakuru Town', 'budget': 120000000, 'status': Project.Status.PLANNING, 'progress': 0},
        {'name': 'Sunrise School Complex', 'client': clients[2], 'location': 'Ruiru', 'budget': 25000000, 'status': Project.Status.COMPLETED, 'progress': 100},
        {'name': 'Downtown Office Block', 'client': clients[1], 'location': 'CBD, Nairobi', 'budget': 80000000, 'status': Project.Status.ON_HOLD, 'progress': 60},
        {'name': 'Westlands Tower', 'client': clients[3], 'location': 'Westlands, Nairobi', 'budget': 50000000, 'status': Project.Status.ONGOING, 'progress': 35},
        {'name': 'Mountain View Resort', 'client': clients[4], 'location': 'Naivasha', 'budget': 75000000, 'status': Project.Status.PLANNING, 'progress': 10},
        {'name': 'City Mall Extension', 'client': clients[4], 'location': 'Nairobi CBD', 'budget': 120000000, 'status': Project.Status.ONGOING, 'progress': 60},
        {'name': 'Riverside Apartments', 'client': clients[5], 'location': 'Kisumu', 'budget': 30000000, 'status': Project.Status.ON_HOLD, 'progress': 25},
    ]
    created = []
    for data in projects_data:
        project, _ = Project.objects.get_or_create(
            name=data['name'],
            defaults={
                'client': data['client'],
                'location': data['location'],
                'budget': data['budget'],
                'status': data['status'],
                'progress_percent': data['progress'],
                'start_date': date.today() - timedelta(days=randint(30, 365)),
                'end_date': date.today() + timedelta(days=randint(30, 365)),
                'description': f"Construction of {data['name']} - a premium development project.",
                'created_by': pm or admin,
            }
        )
        created.append(project)
        print(f"  Project '{data['name']}' created.")
    return created

def create_employees(users):
    employees_data = [
        {'user': users[3], 'position': 'Site Supervisor', 'department': 'Construction', 'salary': 80000},
        {'user': users[5], 'position': 'Mason', 'department': 'Construction', 'salary': 35000},
        {'user': users[6], 'position': 'Carpenter', 'department': 'Construction', 'salary': 35000},
    ]
    created = []
    for data in employees_data:
        emp, _ = Employee.objects.get_or_create(
            user=data['user'],
            defaults={
                'position': data['position'],
                'department': data['department'],
                'salary': data['salary'],
                'employment_date': date.today() - timedelta(days=randint(90, 365)),
                'phone': data['user'].phone,
                'is_active': True,
            }
        )
        created.append(emp)
        print(f"  Employee '{data['user'].get_full_name()}' created.")
    return created

def assign_employees_to_projects(employees, projects, users):
    """Assign employees to projects via ProjectAssignment."""
    supervisor = users[3]
    storekeeper = users[9]  # David Mwangi
    assignments = [
        (employees[0], projects[0]),  # Site Supervisor -> Green Valley
        (employees[0], projects[1]),  # Site Supervisor -> Ocean View
        (employees[1], projects[0]),  # Mason -> Green Valley
        (employees[2], projects[0]),  # Carpenter -> Green Valley
        (employees[2], projects[3]),  # Carpenter -> Sunrise School
    ]
    created = 0
    for emp, proj in assignments:
        _, was_created = ProjectAssignment.objects.get_or_create(
            project=proj,
            employee=emp.user,
            defaults={'assigned_by': supervisor}
        )
        if was_created:
            created += 1
            print(f"  Assigned {emp.user.get_full_name()} -> {proj.name}")

    # Assign storekeeper to first project
    _, was_created = ProjectAssignment.objects.get_or_create(
        project=projects[0],
        employee=storekeeper,
        defaults={'assigned_by': supervisor}
    )
    if was_created:
        created += 1
        print(f"  Assigned {storekeeper.get_full_name()} -> {projects[0].name}")

    if created == 0:
        print("  All assignments already exist.")
    return assignments


def create_materials():
    materials_data = [
        {'name': 'Cement (50kg)', 'category': 'Cement', 'quantity': 500, 'unit': 'bags', 'unit_cost': 650, 'supplier': 'Bamburi Cement', 'reorder_level': 50},
        {'name': 'Sand (ton)', 'category': 'Sand', 'quantity': 200, 'unit': 'tons', 'unit_cost': 2500, 'supplier': 'Machakos Quarry', 'reorder_level': 20},
        {'name': 'Gravel (ton)', 'category': 'Gravel', 'quantity': 150, 'unit': 'tons', 'unit_cost': 3000, 'supplier': 'Machakos Quarry', 'reorder_level': 15},
        {'name': 'Steel Bars 12mm', 'category': 'Steel', 'quantity': 80, 'unit': 'pieces', 'unit_cost': 1200, 'supplier': 'Steel Works Ltd', 'reorder_level': 10},
        {'name': 'Paint (5L)', 'category': 'Paint', 'quantity': 120, 'unit': 'litres', 'unit_cost': 1800, 'supplier': 'Crown Paints', 'reorder_level': 20},
        {'name': 'Timber 2x4', 'category': 'Timber', 'quantity': 300, 'unit': 'pieces', 'unit_cost': 350, 'supplier': 'Timber Mart', 'reorder_level': 50},
        {'name': 'Tiles 300x300', 'category': 'Other', 'quantity': 400, 'unit': 'pieces', 'unit_cost': 450, 'supplier': 'Tile Gallery', 'reorder_level': 40},
    ]
    admin = User.objects.filter(role=User.Role.ADMIN).first()
    created = []
    for data in materials_data:
        mat, _ = Material.objects.get_or_create(
            name=data['name'],
            defaults={
                'category': data['category'],
                'quantity': data['quantity'],
                'unit': data['unit'],
                'unit_cost': data['unit_cost'],
                'supplier': data['supplier'],
                'reorder_level': data['reorder_level'],
            }
        )
        created.append(mat)
        print(f"  Material '{data['name']}' created.")
    return created

def create_stock_transactions(materials, projects, users):
    """Create sample stock in/out transactions linked to projects."""
    admin = users[0]
    supervisor = users[3]
    from apps.inventory.models import StockTransaction
    transactions_data = [
        {'material': materials[0], 'type': 'in', 'qty': 100, 'project': projects[0], 'ref': 'PO-001', 'notes': 'Cement delivery for Green Valley', 'by': admin},
        {'material': materials[0], 'type': 'out', 'qty': 40, 'project': projects[0], 'ref': 'GRN-001', 'notes': 'Foundation concreting - Green Valley', 'by': supervisor},
        {'material': materials[1], 'type': 'in', 'qty': 50, 'project': projects[1], 'ref': 'PO-002', 'notes': 'Sand delivery for Ocean View', 'by': admin},
        {'material': materials[1], 'type': 'out', 'qty': 20, 'project': projects[1], 'ref': 'GRN-002', 'notes': 'Block work - Ocean View', 'by': supervisor},
        {'material': materials[3], 'type': 'in', 'qty': 30, 'project': projects[2], 'ref': 'PO-003', 'notes': 'Steel bars for Highland Mall', 'by': admin},
        {'material': materials[3], 'type': 'out', 'qty': 15, 'project': projects[2], 'ref': 'GRN-003', 'notes': 'Column reinforcement - Highland Mall', 'by': supervisor},
        {'material': materials[2], 'type': 'out', 'qty': 10, 'project': projects[3], 'ref': 'GRN-004', 'notes': 'Concrete mix - Sunrise School', 'by': supervisor},
        {'material': materials[4], 'type': 'in', 'qty': 60, 'project': None, 'ref': 'PO-004', 'notes': 'General paint stock', 'by': admin},
    ]
    created = []
    for td in transactions_data:
        t, _ = StockTransaction.objects.get_or_create(
            material=td['material'],
            transaction_type=td['type'],
            quantity=td['qty'],
            reference=td['ref'],
            defaults={
                'project': td['project'],
                'notes': td['notes'],
                'done_by': td['by'],
            }
        )
        if td['project']:
            print(f"  Stock {td['type']}: {td['material'].name} x{td['qty']} -> {td['project'].name}")
        else:
            print(f"  Stock {td['type']}: {td['material'].name} x{td['qty']} (general)")
        created.append(t)
    return created


def create_equipment():
    equipment_data = [
        {'name': 'Excavator CAT 320', 'category': 'Excavators', 'registration': 'KCA 001E', 'status': 'In Use'},
        {'name': 'Concrete Mixer 500L', 'category': 'Mixers', 'registration': 'KCB 002M', 'status': 'Available'},
        {'name': 'Dump Truck Scania', 'category': 'Trucks', 'registration': 'KCC 003T', 'status': 'Under Maintenance'},
        {'name': 'Generator 50KVA', 'category': 'Generators', 'registration': 'KCD 004G', 'status': 'Available'},
        {'name': 'Air Compressor', 'category': 'Compressors', 'registration': 'KCE 005C', 'status': 'In Use'},
    ]
    created = []
    for data in equipment_data:
        equip, _ = Equipment.objects.get_or_create(
            name=data['name'],
            defaults={
                'category': data['category'],
                'registration_number': data['registration'],
                'purchase_date': date.today() - timedelta(days=randint(365, 1095)),
                'maintenance_date': date.today() - timedelta(days=randint(30, 90)),
                'status': data['status'],
            }
        )
        created.append(equip)
        print(f"  Equipment '{data['name']}' created.")
    return created


def create_equipment_usage_logs(equipment_list, projects, users):
    """Create usage logs linking equipment to projects."""
    sup = users[3]  # supervisor
    usage_data = [
        (equipment_list[0], projects[0], '2024-01-15', '2024-03-15', 320, 'Foundation excavation - Green Valley Estate'),
        (equipment_list[1], projects[0], '2024-02-01', '2024-04-01', 180, 'Concrete mixing for footings'),
        (equipment_list[0], projects[1], '2024-03-01', '2024-05-01', 240, 'Site clearing and piling - Ocean View'),
        (equipment_list[3], projects[2], '2024-04-01', None, 120, 'Power supply for Highland Mall construction'),
        (equipment_list[4], projects[3], '2024-01-10', '2024-04-10', 400, 'General site work - Sunrise School'),
        (equipment_list[2], projects[4], '2024-03-15', None, 200, 'Material haulage - Downtown Office Block'),
    ]
    created = []
    from datetime import datetime
    for equip, proj, start, end, hours, notes in usage_data:
        log, _ = EquipmentUsageLog.objects.get_or_create(
            equipment=equip,
            project=proj,
            start_date=start,
            defaults={
                'end_date': end,
                'hours_used': hours,
                'assigned_to': sup,
                'notes': notes,
            }
        )
        created.append(log)
        print(f"  Usage log: {equip.name} -> {proj.name}")
    return created


def create_quotations(clients, projects, users):
    admin = users[0]
    pm = users[1]
    today = date.today()
    quotations_data = [
        {
            'number': 'QTN-2024-0001', 'client': clients[0], 'project': projects[0],
            'date': today - timedelta(days=15), 'expiry': today + timedelta(days=15),
            'subtotal': 2480000, 'tax_pct': 16, 'grand': 2876800,
            'status': 'Sent', 'created_by': pm,
            'items': [
                ('Excavation & Foundation Works', 1, 'lump sum', 850000, 850000),
                ('Concrete Works (Grade 30)', 45, 'm³', 18000, 810000),
                ('Steel Reinforcement (12mm)', 320, 'pieces', 1200, 384000),
                ('Blockwork (6" blocks)', 1800, 'pcs', 145, 261000),
                ('Damp Proof Membrane', 1, 'lump sum', 175000, 175000),
            ]
        },
        {
            'number': 'QTN-2024-0002', 'client': clients[1], 'project': projects[1],
            'date': today - timedelta(days=30), 'expiry': today,
            'subtotal': 3120000, 'tax_pct': 16, 'grand': 3619200,
            'status': 'Accepted', 'created_by': pm,
            'items': [
                ('Structural Steel Framework', 15, 'tons', 95000, 1425000),
                ('Roofing (GCI Sheets 28g)', 520, 'm²', 1250, 650000),
                ('Plumbing Works (Complete)', 1, 'lump sum', 480000, 480000),
                ('Electrical Installation', 1, 'lump sum', 365000, 365000),
                ('Floor Tiling (600x600)', 320, 'm²', 625, 200000),
            ]
        },
        {
            'number': 'QTN-2024-0003', 'client': clients[2], 'project': projects[3],
            'date': today - timedelta(days=60), 'expiry': today - timedelta(days=30),
            'subtotal': 1860000, 'tax_pct': 16, 'grand': 2157600,
            'status': 'Converted', 'created_by': admin,
            'items': [
                ('Classroom Block Construction', 1, 'lump sum', 920000, 920000),
                ('Plastering & Painting', 850, 'm²', 380, 323000),
                ('Window Installation (Aluminium)', 45, 'pcs', 8500, 382500),
                ('Door Installation (Solid Core)', 24, 'pcs', 9750, 234000),
            ]
        },
        {
            'number': 'QTN-2024-0004', 'client': clients[0], 'project': projects[2],
            'date': today - timedelta(days=5), 'expiry': today + timedelta(days=25),
            'subtotal': 4780000, 'tax_pct': 16, 'grand': 5544800,
            'status': 'Draft', 'created_by': pm,
            'items': [
                ('Site Clearance & Earthworks', 1, 'lump sum', 650000, 650000),
                ('Reinforced Concrete Frame', 120, 'm³', 15500, 1860000),
                ('Masonry Works', 2500, 'pcs', 160, 400000),
                ('Steel Roof Trusses', 28, 'tons', 82000, 2296000),
                ('Rainwater Downpipes & Gutters', 320, 'm', 450, 144000),
            ]
        },
        {
            'number': 'QTN-2024-0005', 'client': clients[1], 'project': projects[4],
            'date': today - timedelta(days=45), 'expiry': today - timedelta(days=15),
            'subtotal': 560000, 'tax_pct': 16, 'grand': 649600,
            'status': 'Rejected', 'created_by': admin,
            'items': [
                ('Interior Design Consultation', 1, 'lump sum', 150000, 150000),
                ('Gypsum Ceiling Installation', 320, 'm²', 850, 272000),
                ('Floor Polishing (Terrazzo)', 280, 'm²', 325, 91000),
                ('Fencing (Chain Link)', 180, 'm', 260, 46800),
            ]
        },
        {
            'number': 'QTN-2024-0006', 'client': clients[3], 'project': projects[5],
            'date': today - timedelta(days=5), 'expiry': today + timedelta(days=25),
            'subtotal': 3200000, 'tax_pct': 16, 'grand': 3712000,
            'status': 'Sent', 'created_by': pm,
            'items': [
                ('Site Preparation & Earthworks', 1, 'lump sum', 450000, 450000),
                ('Reinforced Concrete Frame (Grade 35)', 95, 'm3', 16500, 1567500),
                ('Steel Reinforcement (16mm, 12mm)', 420, 'pieces', 1350, 567000),
                ('Masonry Works (6 inch blocks)', 2200, 'pcs', 155, 341000),
                ('Plastering & Finishing', 950, 'm2', 295, 280250),
            ]
        },
    ]
    created = []
    for qd in quotations_data:
        q, _ = Quotation.objects.get_or_create(
            quotation_number=qd['number'],
            defaults={
                'client': qd['client'],
                'project': qd['project'],
                'date': qd['date'],
                'expiry_date': qd['expiry'],
                'subtotal': qd['subtotal'],
                'tax_percent': qd['tax_pct'],
                'tax_amount': round(qd['subtotal'] * qd['tax_pct'] / 100, 2),
                'grand_total': qd['grand'],
                'status': qd['status'],
                'created_by': qd['created_by'],
                'notes': f'Quotation for {qd["project"].name} - {qd["client"].full_name}.',
                'terms_conditions': 'Payment due within 30 days. All prices subject to 16% VAT.',
            }
        )
        for desc, qty, unit, uprice, total in qd['items']:
            QuotationItem.objects.get_or_create(
                quotation=q, description=desc,
                defaults={
                    'quantity': qty, 'unit': unit,
                    'unit_price': uprice, 'total': total,
                }
            )
        created.append(q)
        print(f"  Quotation '{qd['number']}' ({qd['status']}) with {len(qd['items'])} items.")
    return created

def create_site_reports(projects, users):
    supervisor = users[3]  # site supervisor
    today = date.today()
    reports_data = [
        {
            'project': projects[0], 'day_offset': 1,
            'weather': 'Sunny, 28 deg C',
            'workers': 24,
            'tasks': 'Excavation of foundation trenches completed\nConcrete mixing and pouring for footings started\nSteel reinforcement cutting and bending in progress',
            'materials': 'Cement: 45 bags\nSand: 12 tons\nGravel: 8 tons\nSteel bars 12mm: 60 pieces',
            'challenges': 'Delayed delivery of aggregates from supplier\nOne mixer breakdown - repaired within 2 hours',
        },
        {
            'project': projects[0], 'day_offset': 0,
            'weather': 'Cloudy, 24 deg C',
            'workers': 28,
            'tasks': 'Footing concrete pouring completed\nBlockwork for foundation walls started\nSite drainage trench dug',
            'materials': 'Cement: 52 bags\nSand: 14 tons\nGravel: 10 tons\nBlocks: 400 pcs',
            'challenges': 'Minor flooding in excavation pit due to overnight rain\nWater pump used to dewater',
        },
        {
            'project': projects[1], 'day_offset': 2,
            'weather': 'Sunny, 30 deg C',
            'workers': 18,
            'tasks': 'Site clearing and leveling completed\nSetting out for building lines done\nPiling works commenced',
            'materials': 'Fuel: 200 litres\nTimber: 50 pieces\nNails: 5 kg',
            'challenges': 'Hard rock layer encountered during excavation\nNeed for pneumatic breaker - ordered',
        },
        {
            'project': projects[2], 'day_offset': 3,
            'weather': 'Rainy, 22 deg C',
            'workers': 12,
            'tasks': 'Survey and beacon placement done\nSoil testing samples collected\nAccess road grading completed',
            'materials': 'No major materials used - site preparation phase',
            'challenges': 'Limited access due to muddy roads\nGrading postponed to afternoon after rain stopped',
        },
        {
            'project': projects[3], 'day_offset': -2,
            'weather': 'Sunny, 26 deg C',
            'workers': 32,
            'tasks': 'Final painting touch-ups in classrooms\nWindows and door fittings checked\nLandscaping and tree planting completed\nHandover inspection conducted',
            'materials': 'Paint: 10 litres\nPlants: 25 seedlings\nGrass turf: 200 m²',
            'challenges': 'Minor cracks found in 2 classrooms - rectified with filler',
        },
    ]
    created = []
    for rd in reports_data:
        report_date = today + timedelta(days=rd['day_offset'])
        report, _ = DailySiteReport.objects.get_or_create(
            project=rd['project'],
            date=report_date,
            defaults={
                'weather': rd['weather'],
                'workers_present': rd['workers'],
                'tasks_completed': rd['tasks'],
                'materials_used': rd['materials'],
                'challenges': rd['challenges'],
                'submitted_by': supervisor,
            }
        )
        created.append(report)
        print(f"  Site Report: {report} ({rd['weather']}, {rd['workers']} workers)")
    return created

def create_document_categories():
    categories = [
        {'name': 'Contracts & Agreements', 'description': 'Signed contracts, MoUs, and service agreements'},
        {'name': 'Drawings & Blueprints', 'description': 'Architectural and structural drawings'},
        {'name': 'Permits & Licenses', 'description': 'Construction permits, NEMA licenses, and approvals'},
        {'name': 'Site Photos', 'description': 'Progress photos and site imagery'},
        {'name': 'Reports & Certificates', 'description': 'Inspection reports, test certificates, and compliance docs'},
        {'name': 'Correspondence', 'description': 'Official letters, emails, and meeting minutes'},
    ]
    created = []
    for cat in categories:
        c, _ = DocumentCategory.objects.get_or_create(
            name=cat['name'],
            defaults={'description': cat['description']}
        )
        created.append(c)
        print(f"  Category '{cat['name']}' created.")
    return created


def create_documents(categories, projects, users):
    from django.core.files.base import ContentFile
    from django.conf import settings
    admin = users[0]
    pm = users[1]
    media_dir = settings.MEDIA_ROOT
    docs_dir = os.path.join(media_dir, 'documents')
    os.makedirs(docs_dir, exist_ok=True)

    documents_data = [
        {'title': 'Construction Contract - Green Valley', 'cat': categories[0], 'project': projects[0], 'version': '1.0', 'uploaded_by': admin, 'content': 'CONTRACT AGREEMENT\n\nThis agreement is made between SCHONES HEIM BUILDERS and Njoki Properties Ltd for the construction of Green Valley Estate.\n\nTotal Contract Value: KSh 50,000,000\nDuration: 18 months\nSign Date: 2024-01-15\n\nTerms and conditions as per the standard construction contract template.'},
        {'title': 'Architectural Drawings - Green Valley', 'cat': categories[1], 'project': projects[0], 'version': '2.1', 'uploaded_by': pm, 'content': 'ARCHITECTURAL DRAWINGS SET\n\nProject: Green Valley Estate\nSheet Count: 24\nRevision: 2.1\nDate: 2024-02-20\n\nIncludes: Site plan, floor plans, elevations, sections, and detail drawings.'},
        {'title': 'NEMA License - Ocean View', 'cat': categories[2], 'project': projects[1], 'version': '1.0', 'uploaded_by': admin, 'content': 'NEMA CONSTRUCTION LICENSE\n\nLicense No: NEMA/CNST/2024/0567\nProject: Ocean View Apartments\nValidity: 2024-03-01 to 2025-02-28\n\nApproved for construction subject to environmental management plan.'},
        {'title': 'Foundation Completion Report', 'cat': categories[4], 'project': projects[0], 'version': '1.0', 'uploaded_by': pm, 'content': 'FOUNDATION COMPLETION REPORT\n\nProject: Green Valley Estate\nDate: 2024-04-10\n\nAll foundation works have been completed per the structural specifications.\nConcrete strength tests passed at 28 days.\nRecommendation: Proceed to superstructure works.'},
        {'title': 'Site Progress Photos - March 2024', 'cat': categories[3], 'project': projects[0], 'version': '1.0', 'uploaded_by': pm, 'content': 'SITE PROGRESS PHOTOS\n\nProject: Green Valley Estate\nMonth: March 2024\n\nPhotos documenting excavation, footing concreting, and blockwork stages.'},
        {'title': 'Weekly Progress Report - Week 12', 'cat': categories[4], 'project': projects[1], 'version': '1.0', 'uploaded_by': pm, 'content': 'WEEKLY PROGRESS REPORT\n\nProject: Ocean View Apartments\nWeek: 12 (2024-03-18 to 2024-03-24)\n\nProgress: 22% complete\nActivities: Piling completed, ground beam concreting in progress\nWorkers on site: 18\nChallenges: Material delivery delays'},
        {'title': 'Variation Order - Additional Floor', 'cat': categories[0], 'project': projects[2], 'version': '1.0', 'uploaded_by': admin, 'content': 'VARIATION ORDER\n\nProject: Highland Mall Construction\nDescription: Addition of one floor (4th floor)\nAdditional Cost: KSh 15,000,000\nApproved By: Client Representative\nDate: 2024-05-01'},
        {'title': 'Meeting Minutes - Site Coordination', 'cat': categories[5], 'project': projects[0], 'version': '1.0', 'uploaded_by': pm, 'content': 'SITE COORDINATION MEETING MINUTES\n\nDate: 2024-03-15\nAttendees: PM, Site Supervisor, Client Rep, Architect\n\nAgenda:\n1. Progress review - on schedule\n2. Material procurement - cement order placed\n3. Safety inspection - passed\n4. Next steps - roof works mobilization'},
        {'title': 'Material Test Certificates - Steel', 'cat': categories[4], 'project': projects[3], 'version': '1.0', 'uploaded_by': pm, 'content': 'MATERIAL TEST CERTIFICATE\n\nMaterial: Steel Reinforcement Bars 12mm\nBatch: SB-2024-045\nTest Date: 2024-02-10\n\nYield Strength: 550 MPa (Pass)\nTensile Strength: 650 MPa (Pass)\nElongation: 18% (Pass)\n\nCertified by: Kenya Bureau of Standards'},
        {'title': 'Handover Certificate - Sunrise School', 'cat': categories[0], 'project': projects[3], 'version': '1.0', 'uploaded_by': admin, 'content': 'PROJECT HANDOVER CERTIFICATE\n\nProject: Sunrise School Complex\nDate of Handover: 2024-06-01\n\nThis certifies that the above project has been completed per the contract specifications and is hereby handed over to the client.\n\nDefects Liability Period: 12 months from handover date.'},
    ]
    created = []
    for dd in documents_data:
        filename = dd['title'].lower().replace(' ', '_')[:50] + '.txt'
        filepath = os.path.join(docs_dir, filename)
        doc, _ = Document.objects.get_or_create(
            title=dd['title'],
            defaults={
                'category': dd['cat'],
                'project': dd['project'],
                'version': dd['version'],
                'uploaded_by': dd['uploaded_by'],
                'description': dd['content'][:100],
            }
        )
        if not doc.file:
            doc.file.save(filename, ContentFile(dd['content']))
            doc.save(update_fields=['file'])
        created.append(doc)
        print(f"  Document '{dd['title']}' created.")
    return created


def create_notifications(users):
    notification_messages = [
        'Welcome to SCHONES HEIM BUILDERS Construction Management System.',
        'Your profile has been updated successfully.',
        'A new project has been assigned to you.',
    ]
    for user in users[:4]:
        for msg in notification_messages[:2]:
            Notification.objects.get_or_create(
                recipient=user,
                title='System Notification',
                defaults={'message': msg}
            )
    print('  Sample notifications created.')

def main():
    print('\n=== SCHONES HEIM BUILDERS - Seed Data ===\n')
    print('Creating company settings...')
    create_company_settings()
    print('\nCreating users...')
    users = create_users()
    print('\nCreating clients...')
    clients = create_clients()
    print('\nCreating projects...')
    projects = create_projects(clients)
    print('\nCreating employees...')
    employees = create_employees(users)
    print('\nAssigning employees to projects...')
    assign_employees_to_projects(employees, projects, users)
    print('\nCreating materials...')
    materials = create_materials()
    print('\nCreating stock transactions...')
    stock_transactions = create_stock_transactions(materials, projects, users)
    print('\nCreating equipment...')
    equipment = create_equipment()
    print('\nCreating equipment usage logs...')
    create_equipment_usage_logs(equipment, projects, users)
    print('\nCreating quotations...')
    quotations = create_quotations(clients, projects, users)
    print('\nCreating site reports...')
    site_reports = create_site_reports(projects, users)
    print('\nCreating document categories...')
    categories = create_document_categories()
    print('\nCreating documents...')
    documents = create_documents(categories, projects, users)
    print('\nCreating notifications...')
    create_notifications(users)
    print('\n=== Seed data creation complete! ===\n')
    print('Default credentials:')
    print('  Admin:    admin / Admin123!')
    print('  PM:       pm / Pm123!')
    print('  Acc:      accountant / Acc123!')
    print('  Super:    supervisor / Sup123!')
    print('  Client:   client1 / Client123!  (Mary Njoki)')
    print('  Client:   client2 / Client123!  (Grace Wambui)')
    print('  Client:   client3 / Client123!  (Peter Kamau)')
    print('  Client:   client4 / Client123!  (Faith Nyambura)')
    print('  Client:   client5 / Client123!  (Samuel Ochieng)')
    print('  Store Keeper: storekeeper / Store123!  (David Mwangi)')
    print('  Employee: employee1 / Emp123!')
    print('  Employee: employee2 / Emp123!')

if __name__ == '__main__':
    main()
