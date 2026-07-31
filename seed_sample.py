#!/usr/bin/env python
"""Seed a sample Contract Agreement + paid Invoice (with Receipt) for preview.

Run: python seed_sample.py
Safe to re-run: existing demo records are replaced, not duplicated.
"""
import os, sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
from apps.clients.models import Client
from apps.projects.models import Project
from apps.contracts.models import Contract
from apps.invoices.models import Invoice, InvoiceItem, Payment


def main():
    admin = User.objects.filter(is_superuser=True).order_by('id').first()
    if not admin:
        admin = User.objects.filter(is_active=True).order_by('id').first()
    if not admin:
        print("ERROR: No user found to attach records to. Create a user first.")
        return

    # 1. Client - use an existing client user (e.g. client1) so portal signing works
    client_user = User.objects.filter(role=User.Role.CLIENT, client_profile__isnull=False).order_by('id').first()
    if not client_user:
        print("ERROR: No client user with a linked Client profile found. Run seed_data.py first.")
        return
    client = client_user.client_profile
    print(f"Client: {client.full_name} (linked to user {client_user.username})")

    # Remove any previous demo records so re-runs stay clean
    Contract.objects.filter(contract_number__in=['CTR-2026-DEMO']).delete()
    Invoice.objects.filter(invoice_number__in=['INV-2026-DEMO']).delete()
    Project.objects.filter(name__in=['Demo Residence - Roysambu', 'Mwangi Residence - Roysambu']).delete()
    Client.objects.filter(email='demo.client@example.com').delete()

    # 2. Project
    project = Project.objects.create(
        name='Demo Residence - Roysambu',
        client=client,
        description='Design and construction of a 4-bedroom stone masonry residence including foundation, masonry, roofing, plastering, electrical and plumbing works.',
        location='Roysambu, Nairobi',
        start_date=date(2026, 8, 1),
        end_date=date(2026, 12, 1),
        budget=Decimal('5000000.00'),
        status='Ongoing',
        progress_percent=25,
        created_by=admin,
    )
    print(f"Project: created - {project.name}")

    # 3. Contract (unsigned so both parties can sign online)
    contract = Contract.objects.create(
        client=client,
        project=project,
        title='Construction of Demo Residence',
        description=project.description,
        terms=(
            '1. The Client shall pay a 30% deposit upon signing this agreement.\n'
            '2. The balance shall be paid in milestone installments as certified by the Engineer.\n'
            '3. Any variation to the scope shall be confirmed in writing and priced accordingly.\n'
            '4. The Contractor shall warrant the works for a period of 6 months after completion.\n'
            '5. The Client shall not employ subcontractors directly without the Contractor\u2019s consent.\n'
            '6. This agreement is governed by the laws of the Republic of Kenya.'
        ),
        contract_amount=Decimal('5000000.00'),
        deposit_percent=Decimal('30.00'),
        start_date=date(2026, 8, 1),
        end_date=date(2026, 12, 1),
        status='Sent',
        notes='Demo contract seeded for preview - ready for online signing.',
        created_by=admin,
    )
    print(f"Contract: created - {contract.contract_number}")

    # 4. Invoice with items
    invoice = Invoice.objects.create(
        client=client,
        project=project,
        date=date(2026, 7, 31),
        due_date=date(2026, 8, 15),
        status='Paid',
        subtotal=Decimal('1500000.00'),
        tax_percent=Decimal('0.00'),
        tax_amount=Decimal('0.00'),
        discount=Decimal('0.00'),
        grand_total=Decimal('1500000.00'),
        amount_paid=Decimal('1500000.00'),
        balance=Decimal('0.00'),
        notes='30% deposit per Contract CTR-2026-DEMO.',
        created_by=admin,
    )
    InvoiceItem.objects.create(
        invoice=invoice,
        description='Deposit - Construction of Demo Residence (30% of KSh 5,000,000)',
        quantity=1,
        unit='lump sum',
        unit_price=Decimal('1500000.00'),
    )
    print(f"Invoice: created - {invoice.invoice_number}")

    # 5. Payment (this generates the receipt)
    payment = Payment.objects.create(
        invoice=invoice,
        amount=Decimal('1500000.00'),
        payment_date=date(2026, 7, 31),
        payment_method='Bank Transfer',
        reference='DEMO-TRANSFER-001',
        notes='Deposit payment per Contract CTR-2026-DEMO.',
        recorded_by=admin,
    )
    print(f"Payment: created - {payment.receipt_number}")

    print()
    print("=" * 60)
    print("  SAMPLE DATA READY")
    print("=" * 60)
    print(f"  Client login: {client_user.username} / Client123!")
    print(f"  Contract:  {contract.contract_number}")
    print(f"    View:    https://schones-heim-builders.co.ke/contracts/")
    print(f"    Print:   https://schones-heim-builders.co.ke/contracts/{contract.pk}/pdf/")
    print(f"  Invoice:   {invoice.invoice_number}")
    print(f"    View:    https://schones-heim-builders.co.ke/invoices/")
    print(f"  Receipt:   {payment.receipt_number}")
    print(f"    View:    https://schones-heim-builders.co.ke/invoices/receipt/{payment.pk}/")
    print("=" * 60)


if __name__ == '__main__':
    main()
